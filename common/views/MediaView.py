from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema
from common.permissions import HasRole
from common.components import MediaService
from common.serializers.MediaSerializer import (
    PresignedUploadRequestSerializer,
    PresignedUploadResponseSerializer,
)
from common.responses import api_response


class MediaPresignedURLView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["WAITER", "CHEF", "MANAGER"]

    @extend_schema(
        request=PresignedUploadRequestSerializer,
        responses=PresignedUploadResponseSerializer,
    )
    def post(self, request):
        serializer = PresignedUploadRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid request",
                errors=serializer.errors,
                is_success=False,
            )

        result = MediaService.create_presigned_upload_url(
            user=request.user,
            file_name=serializer.validated_data["file_name"],
            content_type=serializer.validated_data["content_type"],
        )

        return api_response(
            status_code=status.HTTP_201_CREATED,
            message="Pre-signed upload URL generated successfully",
            data=PresignedUploadResponseSerializer(result).data,
        )
