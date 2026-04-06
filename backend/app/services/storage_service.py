import uuid
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import UnprocessableException

# Allowed MIME types for uploaded images
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

# Max file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024


def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def _build_url(key: str) -> str:
    return f"https://{settings.aws_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{key}"


async def _validate_and_read(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise UnprocessableException(
            f"Unsupported file type '{file.content_type}'. Allowed: jpeg, png, webp."
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise UnprocessableException("File exceeds the 5MB size limit.")

    return contents


async def upload_avatar(user_id: uuid.UUID, file: UploadFile) -> str:
    """
    Uploads a user avatar to S3.
    Returns the public URL of the uploaded file.
    """
    contents = await _validate_and_read(file)

    extension = file.content_type.split("/")[-1]
    key = f"avatars/{user_id}.{extension}"

    try:
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=settings.aws_bucket_name,
            Key=key,
            Body=contents,
            ContentType=file.content_type,
        )
    except (BotoCoreError, ClientError) as e:
        raise UnprocessableException(f"File upload failed: {str(e)}")

    return _build_url(key)


async def upload_cover(project_id: uuid.UUID, file: UploadFile) -> str:
    """
    Uploads a project cover image to S3.
    Returns the public URL of the uploaded file.
    """
    contents = await _validate_and_read(file)

    extension = file.content_type.split("/")[-1]
    key = f"covers/{project_id}.{extension}"

    try:
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=settings.aws_bucket_name,
            Key=key,
            Body=contents,
            ContentType=file.content_type,
        )
    except (BotoCoreError, ClientError) as e:
        raise UnprocessableException(f"File upload failed: {str(e)}")

    return _build_url(key)