import uuid
import boto3
from fastapi import UploadFile
from botocore.exceptions import ClientError
from app.config.config import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower()

def get_name(filename: str) -> str:
    return filename.rsplit(".", 1)[0].lower()

def validate_file(file: UploadFile) -> None:
    ext = get_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("type")

    file.file.seek(0, 2)       # seek to end
    size = file.file.tell()    # get size
    file.file.seek(0)          # reset to start
    if size > MAX_FILE_SIZE:
        raise ValueError("size")

def upload_file(file: UploadFile, folder: str = "uploads") -> str:
    validate_file(file)

    name = get_name(file.filename)
    ext = get_extension(file.filename)
    s3_key = f"{folder}/{name}_{uuid.uuid4()}.{ext}"

    s3_client.upload_fileobj(
        file.file,
        settings.AWS_BUCKET_NAME,
        s3_key,
        ExtraArgs={"ContentType": file.content_type}
    )

    return s3_key  # store this in DB

def get_presigned_url(s3_key: str, expiry_seconds: int = 3600) -> str:
    try:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_BUCKET_NAME,
                "Key": s3_key
            },
            ExpiresIn=expiry_seconds
        )
    except ClientError:
        raise ValueError("not_found")

def delete_file(s3_key: str) -> None:
    s3_client.delete_object(
        Bucket=settings.AWS_BUCKET_NAME,
        Key=s3_key
    )