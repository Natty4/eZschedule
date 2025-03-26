from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates a superuser if it does not already exist'

    def handle(self, *args, **options):
        username = 'admin'  # Change this to the desired superuser username
        email = 'admin@example.com'  # Change this to the desired email
        password = settings.SUPERUSER_PASSWORD

        User = get_user_model()

        # Check if the superuser already exists
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} already exists'))