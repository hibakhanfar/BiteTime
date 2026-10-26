from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common.responses import api_response
from common.serializers.UserSerializer import RegisterSerializer, UserProfileSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user_data = UserProfileSerializer(user).data

            return api_response(
                status_code=status.HTTP_201_CREATED,
                message="User registered successfully",
                data=user_data,
                is_success=True,
            )

        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Registration failed",
            errors=serializer.errors,
            is_success=False,
        )
