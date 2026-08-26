from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):

    help = "Create default KHOJ user roles"

    def handle(self, *args, **options):

        roles = [
            "Customer",
            "Admin",
        ]

        for role_name in roles:

            group, created = Group.objects.get_or_create(
                name=role_name
            )

            if created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created role: {role_name}"
                    )
                )

            else:

                self.stdout.write(
                    self.style.WARNING(
                        f"Role already exists: {role_name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "KHOJ roles are ready."
            )
        )