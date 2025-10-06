from fastapi import APIRouter, Depends, Form,HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_llm_service, get_resume_parser, get_db_session
from app.services.llm_service import LLMService
from app.services.resume_parser import Parser
from app.models.interview_models import Candidate, CandidateCreate, CandidateRead, JobDescription
from uuid import UUID, uuid4

router = APIRouter(prefix='/candidate' ,tags=['resume', 'candidate'])

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_candidate(
    name: str = Form(..., description="Candidate's full name"),
    e164_phone: str = Form(..., description="Candidate's E.164 format phone number (e.g., +91xxxxxxxxx)"),
    jd_id: str = Form(..., description="UUID of the Job Description to link this candidate to"),
    file: UploadFile = File(..., description="Docx or pdf file"),
    resume_parser: Parser = Depends(get_resume_parser),
    llm_service: LLMService = Depends(get_llm_service),
    db: Session = Depends(get_db_session)
):
    try:
        
        raw_text = await resume_parser.read_file(file)
        if not raw_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read file or file is unsupported. Only PDF/DOCX are supported"
            )

        structured_output = llm_service.parse_resume_data(raw_text)

        clean_id = str(jd_id).strip().replace('"','')

        candidate_info = CandidateCreate(
            name=name,
            e164_phone=e164_phone,
            jd_id=clean_id
        )
        jd_id_uuid = UUID(candidate_info.jd_id)
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id_uuid).first()

        if not jd:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job description with {candidate_info.jd_id} not found"
            )
        
        final_data = candidate_info.model_dump()
        final_data["jd_id"] = str(jd_id_uuid)
        final_data["resume_summary"] = structured_output
        final_data['id'] = str(uuid4())
        db_candidate = Candidate(**final_data)
        db.add(db_candidate)

        try:
            db.commit()
            db.refresh(db_candidate)
        except Exception as e:
            db.rollback()

            if "duplicate key value" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Candidate with this No. already exists"
                )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database error creating candidate: {e}"
            )

        return db_candidate


    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI resume parsing failed: {e}"
        )           
