from common.models.User import User


class UserService:
    @staticmethod
    def register_user(username: str, email: str, password: str) -> User:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=User.Role.CUSTOMER,
        )
        return user
