from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema
from common.permissions import HasRole
from common.components import TableService
from common.serializers.TableCheckInSerializer import (
    TableCheckInCreateSerializer,
    TableCheckInResponseSerializer,
)
from common.responses import api_response


class TableCheckInView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["CUSTOMER"]

    @extend_schema(
        request=TableCheckInCreateSerializer,
        responses=TableCheckInResponseSerializer,
    )
    def post(self, request):
        serializer = TableCheckInCreateSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            checkin = serializer.save()
            return api_response(
                status_code=status.HTTP_201_CREATED,
                message="Checked in successfully",
                data=TableCheckInResponseSerializer(checkin).data,
            )

        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Check-in failed",
            errors=serializer.errors,
            is_success=False,
        )


class TableCheckOutView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["CUSTOMER"]

    @extend_schema(
        request=TableCheckInCreateSerializer,
        responses=TableCheckInResponseSerializer,
    )
    def patch(self, request):
        checkin = TableService.check_out(customer=request.user)

        if checkin is None:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="No active check-in found",
                is_success=False,
            )

        return api_response(
            status_code=status.HTTP_200_OK,
            message="Checked out successfully",
            data=TableCheckInResponseSerializer(checkin).data,
        )
