from django.core.management.base import BaseCommand
from common.components import UserService
from common.models.User import User


class Command(BaseCommand):
    help = "Creates a MANAGER user "

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, required=True)
        parser.add_argument("--email", type=str, required=True)
        parser.add_argument("--password", type=str, required=True)

    def handle(self, *args, **options):
        user = UserService.register_user(
            username=options["username"],
            email=options["email"],
            password=options["password"],
            role=User.Role.MANAGER,
        )

        self.stdout.write(self.style.SUCCESS(f"Manager created successfully: {user.email}"))
