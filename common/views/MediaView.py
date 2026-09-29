from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema
from common.permissions import HasRole
from common.components import MediaService
from common.serializers.MediaSerializer import (
    PresignedUploadRequestSerializer,
    PresignedUploadResponseSerializer,
    PresignedDownloadRequestSerializer,
    PresignedDownloadResponseSerializer,
)
from common.responses import api_response
from rest_framework.permissions import IsAuthenticated


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


class MediaPresignedDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[PresignedDownloadRequestSerializer],
        responses=PresignedDownloadResponseSerializer,
    )
    def get(self, request):
        serializer = PresignedDownloadRequestSerializer(data=request.query_params)

        if not serializer.is_valid():
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid request",
                errors=serializer.errors,
                is_success=False,
            )

        result = MediaService.create_presigned_download_url(serializer.validated_data["object_key"])

        if result is None:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="File not found",
                is_success=False,
            )

        return api_response(
            status_code=status.HTTP_200_OK,
            message="Pre-signed download URL generated successfully",
            data=PresignedDownloadResponseSerializer(result).data,
        )
