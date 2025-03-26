import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
# Get the logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creates a superuser if it does not already exist'

    def handle(self, *args, **options):
        username = 'admin'  
        email = 'admin@ezgo.com'  
        password = settings.SUPERUSER_PASSWORD

        User = get_user_model()

        # Check if the superuser already exists
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            logger.info(f'Superuser {username} created successfully')
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created successfully'))
        else:
            logger.info(f'Superuser {username} already exists')
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} already exists'))
