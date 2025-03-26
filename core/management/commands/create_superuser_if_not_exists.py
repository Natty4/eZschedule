from django.core.management.base import BaseCommand
from core.models import User
from django.conf import settings

class Command(BaseCommand):
    help = 'Create superuser if it does not exist'

    def handle(self, *args, **kwargs):
        username = 'admin'
        email = 'admin@ezgo.com'
        password = settings.SUPERUSER_PASSWORD  # Password from settings

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} already exists'))
