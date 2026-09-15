from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from common.models.User import User
from common.components import UserService


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return UserService.register_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "role")
        read_only_fields = ("id", "username", "email", "role")


class UserRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[User.Role.CHEF, User.Role.WAITER])

    def update(self, instance, validated_data):
        instance.role = validated_data["role"]
        instance.save()
        return instance
