from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import CustomUser


class Command(BaseCommand):

    help = "Create a super user with admin role"

    def add_arguments(self, parser):
        parser.add_argument("--unique_code", required=True)
        parser.add_argument("--center", required=True)
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                if CustomUser.objects.filter(center=options["center"], role=CustomUser.ADMIN).exists():
                    self.stdout.write(self.style.ERROR('User with this email already exists'))
                    return

                user = CustomUser.objects.create(
                    password=options["password"],
                    center=options["center"],
                    username=options["username"],
                    role=CustomUser.ADMIN,
                    unique_code=options["unique_code"],
                    is_staff=True,
                    is_superuser=True
                )

                user.set_password(options["password"])
                user.save()

                self.stdout.write(self.style.SUCCESS(f'Super user created successfully, unique_code: {user.unique_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating super user: {e}'))
