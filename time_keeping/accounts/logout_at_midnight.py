from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, logout

class Command(BaseCommand):
    help = 'Logs out all active users at midnight.'

    def handle(self, *args, **options):
        User = get_user_model()
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            for user in User.objects.filter(is_active=True):
                logout(user)
            self.stdout.write(self.style.SUCCESS('Successfully logged out all active users.'))
