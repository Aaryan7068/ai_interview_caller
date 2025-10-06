from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_llm_service, get_db_session
from app.services.llm_service import LLMService
from app.models.interview_models import JobDescription, JobDescriptionCreate
from uuid import uuid4
router = APIRouter(prefix='/jd', tags=['Job Description'])

@router.post("/generate-questions", status_code=status.HTTP_201_CREATED)
def generate_questions(
    jd_in: JobDescriptionCreate,
    llm_service: LLMService = Depends(get_llm_service),
    db: Session = Depends(get_db_session)
): 
    try:
        questions = llm_service.generate_interview_questions(jd_text=jd_in.content)
        generate_jid = str(uuid4())
        db_jd = JobDescription(
            id= generate_jid,
            title = jd_in.title,
            content = jd_in.content,
            generated_questions = questions
        )
        db.add(db_jd)
        db.commit()
        db.refresh(db_jd)
        return {"jd_id": db_jd.id, "questions": db_jd.generated_questions}
    except Exception as e:
        print(f"Error occured while generating questions: ")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=f"AI Question generation failed: {e}"
        )
    
