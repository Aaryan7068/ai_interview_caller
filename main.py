from fastapi import FastAPI, Depends
from sqlalchemy_utils import database_exists, create_database
from app.core.database import engine, Base
from app.core.security import verify_api_key
from app.api.endpoints import jd, candidate, interview, webhooks

if not database_exists(engine.url):
    create_database(engine.url)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI interview caller",
    version="1.0.0"
)

secure_dependency = [Depends(verify_api_key)]
app.include_router(jd.router, dependencies=secure_dependency)
app.include_router(candidate.router, dependencies=secure_dependency)
app.include_router(interview.router, dependencies=secure_dependency)
app.include_router(webhooks.router)

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "AI Interview Screener Backend is running."}
