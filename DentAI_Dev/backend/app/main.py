from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import predict, treatments

app = FastAPI(
    title="DentAI API",
    description="Dental diagnosis API using EfficientNetV2 + BERT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, prefix="/predict", tags=["predict"])
app.include_router(treatments.router, prefix="/treatments", tags=["treatments"])


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "app": "DentAI API", "version": "1.0.0"}
