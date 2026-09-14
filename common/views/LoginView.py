from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from common.responses import api_response
from common.serializers.LoginSerializer import CustomTokenObtainPairSerializer


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Login failed",
                errors=serializer.errors,
            )

        tokens = serializer.validated_data
        user = serializer.user

        data = {
            "user": {
                "id": user.id,
                "email": user.email,
                "role": getattr(user, "role", "CUSTOMER"),
            },
            "tokens": tokens,
        }

        return api_response(
            status_code=status.HTTP_200_OK,
            message="Login successful",
            data=data,
        )
