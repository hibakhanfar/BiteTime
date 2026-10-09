import uuid
import boto3
from django.conf import settings


class S3Service:
    @staticmethod
    def _client():
        return boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

    @staticmethod
    def generate_presigned_upload_url(file_name, content_type):
        object_key = f"uploads/{uuid.uuid4()}/{file_name}"
        expiry_seconds = settings.PRESIGNED_URL_EXPIRY_SECONDS

        upload_url = S3Service._client().generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=expiry_seconds,
        )

        return {
            "upload_url": upload_url,
            "object_key": object_key,
            "expires_in": expiry_seconds,
        }
