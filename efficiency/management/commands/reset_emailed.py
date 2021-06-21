from django.core.management.base import BaseCommand, CommandError
from efficiency.models import Efficiency
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Before e-mailing users for the next month, we must reset their already been emailed status'

    def handle(self, *args, **options):
        for user in CustomUser.objects.filter(has_been_emailed=True):
            user.has_been_emailed = False
            user.save()
