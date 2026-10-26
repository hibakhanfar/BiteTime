import uuid
import boto3
from django.conf import settings
from botocore.exceptions import ClientError
from botocore.config import Config


class S3Service:
    @staticmethod
    def _client():
        return boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
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

    @staticmethod
    def object_exists(object_key):
        try:
            S3Service._client().head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=object_key)
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
                return False
            raise

    @staticmethod
    def generate_presigned_download_url(object_key):
        expiry_seconds = settings.PRESIGNED_URL_EXPIRY_SECONDS
        file_name = object_key.rsplit("/", 1)[-1].replace('"', "").replace("\\", "")

        download_url = S3Service._client().generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": object_key,
                "ResponseContentDisposition": f'attachment; filename="{file_name}"',
            },
            ExpiresIn=expiry_seconds,
        )

        return {
            "download_url": download_url,
            "object_key": object_key,
            "expires_in": expiry_seconds,
        }
