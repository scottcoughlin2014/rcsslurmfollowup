from django.core.management.base import BaseCommand, CommandError
from efficiency.models import Efficiency
from users.models import CustomUser

import subprocess 
import pandas 
import time
import numpy
import datetime
import email
import smtplib

class Command(BaseCommand):
    help = 'Command that emails users about their computing resource efficiency based on certain criteria'

    def add_arguments(self, parser):
        parser.add_argument("--memory-efficiency-threshold", type=float, default = 0.1)
        parser.add_argument("--memory-requested-threshold", type=int, default = 16)
        parser.add_argument("--start-time", required=True,
                            help="It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.")
        parser.add_argument("--end-time", required=True,
                            help="It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.")

    def handle(self, *args, **options):
        # For now we simple print this reflag information
        print("""
There were {0}/{1} jobs that requested more than {2}GB of memory and had an efficiency less than {3} percent during this time
""".format(Efficiency.objects.filter(job_start__gte=options["start_time"]).filter(job_start__lte=options["end_time"]).filter(mem_eff__lt=options['memory_efficiency_threshold']).filter(mem_requested__gt=options['memory_requested_threshold']).count(), Efficiency.objects.filter(job_start__gte=options["start_time"]).filter(job_start__lte=options["end_time"]).filter(mem_requested__gt=options['memory_requested_threshold']).count(), options['memory_requested_threshold'], options['memory_efficiency_threshold'] *100))

        print("""
There are {0} users with jobs that requested more than {2}GB of memory and had an efficiency less than {3} percent during this time
""".format(len(Efficiency.objects.filter(job_start__gte=options["start_time"]).filter(job_start__lte=options["end_time"]).filter(mem_eff__lt=options['memory_efficiency_threshold']).filter(mem_requested__gt=options['memory_requested_threshold']).order_by('user').values('user').distinct())))
