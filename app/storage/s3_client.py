import io
from typing import Optional

import boto3
from botocore.client import BaseClient

from app.core.config import settings


class S3StorageClient:
    def __init__(self, client: Optional[BaseClient] = None) -> None:
        self._client = client or boto3.client(
            "s3",
            region_name=settings.aws_region,
            endpoint_url=settings.aws_endpoint_url,
        )

    def ensure_bucket(self, bucket: Optional[str] = None) -> None:
        bucket_name = bucket or settings.s3_bucket_name
        existing = self._client.list_buckets().get("Buckets", [])
        if not any(b["Name"] == bucket_name for b in existing):
            self._client.create_bucket(Bucket=bucket_name)

    def put_object(self, key: str, content: bytes, content_type: str) -> str:
        self._client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=key,
            Body=io.BytesIO(content),
            ContentType=content_type,
        )
        return f"s3://{settings.s3_bucket_name}/{key}"

    def get_object(self, key: str) -> bytes:
        obj = self._client.get_object(Bucket=settings.s3_bucket_name, Key=key)
        return obj["Body"].read()

    def delete_object(self, key: str) -> None:
        self._client.delete_object(Bucket=settings.s3_bucket_name, Key=key)

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return self._client.generate_presigned_url(
            "getObject",
            Params={"Bucket": settings.s3_bucket_name, "Key": key},
            ExpiresIn=expires_in,
        )


