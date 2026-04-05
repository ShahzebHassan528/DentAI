from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

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


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "app": "DentAI API", "version": "1.0.0"}


# Routers will be included here as they are built (Day 3+)
# from app.routers import auth, predict, treatments
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(predict.router, prefix="/predict", tags=["predict"])
# app.include_router(treatments.router, prefix="/treatments", tags=["treatments"])
