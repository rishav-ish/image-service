import os


class Settings:
    aws_endpoint_url: str = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    s3_bucket_name: str = os.getenv("S3_BUCKET_NAME", "images-bucket")
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
    mongodb_db: str = os.getenv("MONGODB_DB", "images_db")
    mongodb_collection: str = os.getenv("MONGODB_COLLECTION", "images")


settings = Settings()


