from django.core.management.base import BaseCommand, CommandError
from users.models import CustomUser
from utils.utils import get_email_from_netid
import time

class Command(BaseCommand):
    help = 'Command to track user and account information in order to check on slurm usage/other info and to be able to email them if needed'

    def handle(self, *args, **options):
        for user in CustomUser.objects.filter(email=''):
            time.sleep(2)
            email = get_email_from_netid(user.username)
            if 'DOCTYPE' in email:
                user.delete()
                continue
            print(email, user.username)
            user.email = email
            user.save()
