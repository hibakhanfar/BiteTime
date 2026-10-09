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
