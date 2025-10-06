from fastapi import APIRouter, Depends, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from twilio.twiml.voice_response import VoiceResponse
from app.api.dependencies import get_db_session, get_llm_service
from app.models.interview_models import Candidate, InterviewResult
from app.services.llm_service import LLMService
from uuid import UUID
import json
from typing import Annotated, Optional

llm_service_dep = Depends(get_llm_service)

router = APIRouter(prefix="/twilio/interview", tags=["Twilio Webhooks"])

def get_twiml_response(response: VoiceResponse) -> Response:
    return Response(content=str(response), media_type="application/xml")

@router.post("/start/{candidate_id}")
def start_interview(
    candidate_id: UUID, 
    db: Session = Depends(get_db_session)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        return get_twiml_response(VoiceResponse().say("Error: Candidate record not found. Goodbye."))

    questions = candidate.jd.generated_questions
    if not questions:
        return get_twiml_response(VoiceResponse().say("Error: No questions found for this interview. Goodbye."))

    response = VoiceResponse()
    
    response.say("Hello. Welcome to your automated interview. Please answer the questions clearly after the beep.")
    
    next_url = f"/twilio/interview/question/{candidate_id}/0"
    response.redirect(url=next_url, method='POST')

    return get_twiml_response(response)

@router.post("/question/{candidate_id}/{question_index}")
def handle_question(
    candidate_id: UUID,
    question_index: int,
    db: Session = Depends(get_db_session)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    questions = candidate.jd.generated_questions
    total_questions = len(questions)

    if question_index >= total_questions:
        response = VoiceResponse()
        response.say("Thank you for completing the interview. Goodbye!")
        response.redirect(url=f"/twilio/interview/finish/{candidate_id}", method='POST')
        return get_twiml_response(response)

    current_question = questions[question_index]
    
    response = VoiceResponse()
    response.say(f"Question number {question_index + 1}: {current_question}")
    
    action_url = f"/twilio/interview/advance_call/{candidate_id}/{question_index+1}"

    callback_url =f"/twilio/interview/record_data/{candidate_id}/{question_index}"
    
    
    response.record(
        action=action_url,
        method='POST',
        timeout=10,             
        transcribe=True,        
        transcribe_callback=callback_url, 
        play_beep=True,         
        finish_on_key='#'       
    )
    
    next_question_index = question_index + 1
    redirect_url = f"/twilio/interview/question/{candidate_id}/{next_question_index}"
    response.redirect(url=redirect_url, method='POST')

    return get_twiml_response(response)

@router.post("/advance_call/{candidate_id}/{next_question}")
def advance_call(
    candidate_id: UUID,
    next_question: int,
    db: Session = Depends(get_db_session)
):
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        print(f"Candidate with {candidate_id} not found")
        return get_twiml_response(VoiceResponse().say("An error occured during call advancement"))

    response = VoiceResponse()
    total = len(candidate.jd.generated_questions)
    if next_question < total:
        redirect_url = f"/twilio/interview/question/{candidate_id}/{next_question}"
    else:
        redirect_url = f"/twilio/interview/finish/{candidate_id}"
        response.say("Thank you for your interview have a good day.")
    
    response.redirect(url=redirect_url, method='POST')
    return get_twiml_response(response)

@router.post("/record_data/{candidate_id}/{question_index}")
async def record_callback(
    candidate_id: UUID  ,
    question_index: int,
    RecordingUrl: Annotated[Optional[str], Form()] = None,
    RecordingDuration: Annotated[Optional[str], Form()] = None,
    TranscriptionText: Annotated[Optional[str], Form()] = None,
    db: Session = Depends(get_db_session)
):
    
    result_record = db.query(InterviewResult).filter(InterviewResult.candidate_id == candidate_id).first()

    if not result_record or not result_record.candidates.jd.generated_questions:
        print(f"Error: Result record or questions not found for candidate {candidate_id}")
        return Response(status_code=200)

    current_question = result_record.candidates.jd.generated_questions[question_index]

    new_qa_entry = {
        "question_index": question_index,
        "question": current_question,
        "transcript": TranscriptionText if TranscriptionText else "[No response or transcription available]",
        "audio_url": RecordingUrl,
        "duration": RecordingDuration,
        "score": None, 
        "reasoning": None
    }
    
    interview_data:list = result_record.interview_data or []
    interview_data.append(new_qa_entry)
    result_record.interview_data = interview_data
    result_record.id = str(result_record.id)

    db.commit()
    db.refresh(result_record)

    return Response(status_code=200)

@router.post("/finish/{candidate_id}")
async def finish_interview(
    candidate_id: UUID,
    llm_service: LLMService = llm_service_dep,
    db: Session = Depends(get_db_session)
):
    result_record = db.query(InterviewResult).filter(InterviewResult.candidate_id == candidate_id).first()
    
    if not result_record:
        return Response(status_code=200)

    jd = result_record.candidates.jd
    resume_summary = result_record.candidates.resume_summary
    
    try:
        scoring_data = llm_service.score_and_recommend(
            jd_text=jd.content, 
            resume_data=resume_summary, 
            interview_data=result_record.interview_data
        )
        scoring_data = json.loads(scoring_data)

        result_record.final_score = scoring_data.get("final_score")
        result_record.final_recommendation = scoring_data.get("final_recommendation")
        
        individual_scores = scoring_data.get("individual_scores", [])
        
        # Update individual scores/reasoning
        for qa_entry in result_record.interview_data:
            match = next((s for s in individual_scores if s.get('question') == qa_entry['question']), None)
            if match:
                qa_entry['score'] = match.get('score')
                qa_entry['reasoning'] = match.get('reasoning')

        result_record.interview_data = result_record.interview_data
        
        db.add(result_record)
        db.commit()

        print(f"Scoring complete for {candidate_id}. Final Score: {result_record.final_score}")

    except Exception as e:
        print(f"FATAL SCORING ERROR for {candidate_id}: {e}")

    response = VoiceResponse()
    response.hangup() 
    return get_twiml_response(response)