## Image Service (FastAPI + LocalStack S3 + MongoDB)

### Introduction
This project is a scalable Image Service microservice built with FastAPI, providing RESTful APIs for uploading, storing, retrieving, and deleting images. Images are stored in an S3-compatible object store (via LocalStack), while metadata is managed in MongoDB. The service is containerized with Docker and designed for easy local development and testing, making it ideal for modern cloud-native applications that require efficient image management.

### Stack
- FastAPI (Python 3.12)
- S3 via LocalStack for file upload
- MongoDB for database
- Docker Compose for building apps, localstack and mongodb

### Run locally
1. Build and start:
```bash
docker compose up --build -d
```
2. Verify API: `http://localhost:8000/docs`

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs` - Interactive API documentation
- **ReDoc**: `http://localhost:8000/redoc` - Alternative API documentation
- **OpenAPI JSON**: `http://localhost:8000/openapi.json` - Download for Postman import

### Endpoints
- POST `/api/images` (multipart): params `user_id`; file field `file`.
- GET `/api/images`: filters `user_id`, `content_type`, `limit`, `skip`.
- GET `/api/images/{user_id}/{filename}`: download/view.
- DELETE `/api/images/{user_id}/{filename}`

### How it works
- File stored to S3 bucket `images-bucket` (LocalStack).
- Metadata persisted in MongoDB (`images_db.images`).

### Running tests
```bash
pip install -r requirements.txt
pytest
```

### LocalStack notes
- S3 is exposed on `http://localhost:4566`. The app ensures the bucket exists at startup.


