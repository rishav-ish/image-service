from fastapi import FastAPI
from app.api.routes import router as api_router
from app.storage.s3_client import S3StorageClient
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Image Service",
        version="1.0.0",
        description="A scalable image upload and storage service with S3 and MongoDB",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()