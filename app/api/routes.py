import uuid
from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, Path
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.repositories.mongo_repo import ImageRepository
from app.storage.s3_client import S3StorageClient
from app.logger import get_logger


router = APIRouter()
logger = get_logger()


def get_repo() -> ImageRepository:
    return ImageRepository()


def get_s3() -> S3StorageClient:
    return S3StorageClient()


@router.on_event("startup")
def _ensure_bucket() -> None:
    S3StorageClient().ensure_bucket(settings.s3_bucket_name)


@router.post(
    "/images", 
    status_code=201,
    summary="Upload an image",
    description="Upload an image file with metadata. The image will be stored in S3 and metadata in MongoDB.",
    response_description="Returns the uploaded image and its meta data like size, format, etc."
)
async def upload_image(
    user_id: str = Query(..., description="Unique identifier for the user uploading the image"),
    file: UploadFile = File(..., description="Image file to upload (supports common image formats)"),
    repo: ImageRepository = Depends(get_repo),
    s3: S3StorageClient = Depends(get_s3),
):
    contents = await file.read()
    s3_key = f"{user_id}/{uuid.uuid4()}"
    s3_uri = s3.put_object(key=s3_key, content=contents, content_type=file.content_type)
    doc = {
        "user_id": user_id,
        "filename": file.filename,
        "size": len(contents),
        "content_type": file.content_type,
        "s3_key": s3_key,
        "s3_uri": s3_uri,
    }
    image_id = repo.insert_image(doc)
    return {"id": image_id, **doc}


@router.get(
    "/images",
    summary="List images",
    description="Retrieve a list of images with optional filtering by user_id and content_type. Supports pagination.",
    response_description="Returns a list of image metadata objects"
)
def list_images(
    user_id: Optional[str] = Query(None, title="Filter images by specific user ID"),
    content_type: Optional[str] = Query(None, title="Filter images by MIME type (e.g., 'image/jpeg', 'image/png')"),
    filename: Optional[str] = Query(None, title="Filter images by filename"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of images to return (1-200)"),
    skip: int = Query(0, ge=0, description="Number of images to skip for pagination"),
    repo: ImageRepository = Depends(get_repo),
):
    return repo.list_images(user_id=user_id, content_type=content_type, filename=filename, limit=limit, skip=skip)


@router.get(
    "/image/{user_id}/{file_id}",
    summary="Download/View image",
    description="Download or view an image file by user ID and filename. Returns the raw image data.",
    response_description="Returns the image file as a stream"
)
def download_image(
    user_id: str = Path(..., title="User ID who owns the image"),
    file_id: str = Path(..., title="File ID of the image to download"),
    repo: ImageRepository = Depends(get_repo),
    s3: S3StorageClient = Depends(get_s3),
):
    meta = repo.get_image_by_user_and_file(user_id=user_id, file_id=file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Image not found")
    # content = s3.get_object(meta["s3_key"])
    presigned_url = s3.generate_presigned_url(meta["s3_key"])
    return presigned_url


@router.delete(
    "/image/{user_id}/{file_id}", 
    status_code=204,
    summary="Delete image",
    description="Delete an image file and its metadata from both S3 and MongoDB.",
    response_description="No content returned on successful deletion"
)
def delete_image(
    user_id: str = Path(..., description="User ID who owns the image"),
    file_id: str = Path(..., description="File ID of the image to delete"),
    repo: ImageRepository = Depends(get_repo),
    s3: S3StorageClient = Depends(get_s3),
):
    meta = repo.get_image_by_user_and_file(user_id=user_id, file_id=file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Image not found")
    s3.delete_object(meta["s3_key"])
    repo.delete_by_key(meta["s3_key"])


