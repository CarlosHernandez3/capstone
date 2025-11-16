from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.applicants import router as applicants_router
from routers.analyze import router as analyze_router

app = FastAPI(title="Loan Validation Backend")

# Allow frontend
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
