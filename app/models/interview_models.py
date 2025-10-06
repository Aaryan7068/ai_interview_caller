from typing import List, Optional, Dict, Annotated
from uuid import UUID
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, UUID
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, TypeAdapter
from app.core.database import Base

# schema models
class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=UUID)
    title = Column(String, index=True)
    content = Column(String)
    generated_questions = Column(JSON)
    candidates = relationship("Candidate", back_populates='jd')

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=UUID)
    name = Column(String, index=True,)
    e164_phone = Column(String, unique=True)
    resume_summary = Column(JSON)
    jd_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id"))
    jd = relationship("JobDescription", back_populates="candidates")
    results = relationship("InterviewResult", back_populates="candidates")

class InterviewResult(Base):
    __tablename__ = "results"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=UUID)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), unique=True, index=True, nullable=False)
    call_sid = Column(String, unique=True, index=True)
    interview_data = Column(MutableList.as_mutable(JSON), default=[], nullable=False) 
    final_score = Column(Integer, nullable=True)
    final_recommendation = Column(String, nullable=True)
    candidates = relationship("Candidate", back_populates="results")

# API models
class JobDescriptionCreate(BaseModel):
    title: str
    content: str

class CandidateCreate(BaseModel):
    name: str
    e164_phone: str
    jd_id: str
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 


    @field_validator('e164_phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v or not (v.startswith('+') and v[1:].isdigit() and 7 <= len(v) <= 15):
            raise ValueError('Phone number must be in E.164 format')
        return v

class CandidateRead(BaseModel):
    id: str
    name: str
    e164_phone: str
    resume_summary: Dict
    jd_id: str
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 

    
    

class InterviewResultRead(BaseModel):
    id: str
    candidate_id: str
    call_sid: str
    interview_data: Dict
    final_score: Optional[int] = None
    final_recommendation: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 

    
