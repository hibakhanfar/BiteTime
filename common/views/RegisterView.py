from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from common.permissions import HasRole
from common.responses import api_response
from common.serializers.UserSerializer import (
    RegisterSerializer,
    UserProfileSerializer,
    UserRoleUpdateSerializer,
    UserAvatarUpdateSerializer,
)
from rest_framework.generics import get_object_or_404
from common.models import User
from rest_framework.parsers import MultiPartParser, FormParser


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


class UserListView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["MANAGER"]

    def get(self, request):
        users = User.objects.all()
        serializer = UserProfileSerializer(users, many=True)

        return api_response(
            status_code=200,
            message="Users retrieved successfully",
            data=serializer.data,
        )


class UserRoleUpdateView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["MANAGER"]
    serializer_class = UserRoleUpdateSerializer

    def patch(self, request, pk):
        instance = get_object_or_404(User, pk=pk)
        serializer = UserRoleUpdateSerializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return api_response(
                status_code=status.HTTP_200_OK,
                message="User role updated successfully",
                data={"id": instance.id, "email": instance.email, "role": instance.role},
            )

        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Role update failed",
            errors=serializer.errors,
        )


class UserAvatarUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = UserAvatarUpdateSerializer

    def patch(self, request):
        serializer = UserAvatarUpdateSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return api_response(
                status_code=status.HTTP_200_OK,
                message="Avatar updated successfully",
                data=UserProfileSerializer(request.user).data,
            )

        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Avatar update failed",
            errors=serializer.errors,
        )
