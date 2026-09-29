from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "common"

    def ready(self):
        from . import schema  # noqa: F401
