from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine   # just importing, not redefining
from .models import Applicant, Document, ExtractedField

from .routers.applicants import router as applicants_router
from backend.routers.analyze import router as analyze_router


app = FastAPI(title="Loan Validation Backend")

Base.metadata.create_all(bind=engine)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
def health():
    return {"status": "ok"}

app.include_router(applicants_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
