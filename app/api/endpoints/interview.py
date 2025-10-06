from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db_session, get_telephony_service
from app.services.telephony_service import TelephonyService
from app.models.interview_models import Candidate, InterviewResult
from uuid import UUID, uuid4

router = APIRouter(prefix="/interview", tags=["Interview Flow"])

@router.post("/trigger/{candidate_id}", status_code=status.HTTP_202_ACCEPTED)
def trigger_interview(
    candidate_id: UUID,
    telephony_service: TelephonyService = Depends(get_telephony_service),
    db: Session = Depends(get_db_session)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found.")

    existing_result = db.query(InterviewResult).filter(InterviewResult.candidate_id == candidate_id).first()
    # if existing_result:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, 
    #         detail="Interview already triggered or completed for this candidate."
    #     )

    call_sid = telephony_service.trigger_outbound_call(
        to_number=candidate.e164_phone,
        candidate_id=str(candidate_id)
    )

    if not call_sid:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to initiate outbound call via Twilio. Check Twilio logs/API key."
        )
    
    new_result = InterviewResult(
        id=str(uuid4()), 
        candidate_id=str(candidate_id), 
        call_sid=call_sid,
        interview_data=[]
    )
    db.add(new_result)
    db.commit()

    return {"call_sid": call_sid, "status": "Call initiated"}