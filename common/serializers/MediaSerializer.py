from rest_framework import serializers
from common.components import MediaService


class PresignedUploadRequestSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    content_type = serializers.CharField(max_length=100)

    def validate_content_type(self, value):
        if value not in MediaService.ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                f"Content type '{value}' is not allowed. Allowed types: "
                f"{', '.join(sorted(MediaService.ALLOWED_CONTENT_TYPES))}"
            )
        return value


class PresignedUploadResponseSerializer(serializers.Serializer):
    upload_url = serializers.CharField()
    object_key = serializers.CharField()
    expires_in = serializers.IntegerField()


class PresignedDownloadRequestSerializer(serializers.Serializer):
    object_key = serializers.CharField(max_length=500)

    def validate_object_key(self, value):
        if not value.startswith("uploads/") or ".." in value.split("/"):
            raise serializers.ValidationError("Invalid object key.")
        return value


class PresignedDownloadResponseSerializer(serializers.Serializer):
    download_url = serializers.CharField()
    object_key = serializers.CharField()
    expires_in = serializers.IntegerField()
