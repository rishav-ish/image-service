FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

# ENV AWS_ENDPOINT_URL=http://localstack:4566 \
#     AWS_REGION=us-south-1 \
#     S3_BUCKET_NAME=images-bucket \
#     MONGODB_URI=mongodb://mongodb:27017 \
#     MONGODB_DB=images_db \
#     MONGODB_COLLECTION=images

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


