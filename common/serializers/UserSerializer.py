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
        fields = ("id", "username", "email", "role", "avatar")
        read_only_fields = ("id", "username", "email", "role")


class UserRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[User.Role.CHEF, User.Role.WAITER])

    def update(self, instance, validated_data):
        instance.role = validated_data["role"]
        instance.save()
        return instance


class UserAvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("avatar",)

    def validate_avatar(self, image):
        allowed_extensions = ("jpg", "jpeg", "png", "webp")
        max_size_mb = 5

        extension = image.name.rsplit(".", 1)[-1].lower() if "." in image.name else ""

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file type '.{extension}'. "
                f"Allowed types: {', '.join(allowed_extensions)}."
            )

        if image.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f"Image file too large. Maximum allowed size is {max_size_mb}MB."
            )

        return image
