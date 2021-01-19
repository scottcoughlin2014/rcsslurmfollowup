from django.core.management.base import BaseCommand, CommandError
from users.models import CustomUser, Account
from utils.utils import get_email_from_netid

import subprocess
import pandas
import time
import datetime

class Command(BaseCommand):
    help = 'Command to track user and account information in order to check on slurm usage/other info and to be able to email them if needed'

    def handle(self, *args, **options):

        result = subprocess.run(['grep', '11113', '/etc/group'],stdout=subprocess.PIPE)
        outter_list = []
        for x in result.stdout.decode('utf-8').split('\n'):
            try:
                inner_list = []
                tmp = x.split(":")
                # check if a general access allocation
                if 'p' in tmp[0]:
                    inner_list.append(tmp[0])
                    inner_list.extend(tmp[3].split(','))
                    outter_list.append(inner_list)
                else:
                    continue
            except:
                pass

        # loop over allocations and users in that allocation
        for allocation_and_users in outter_list:
            allocation_name = allocation_and_users[0]
            for netid in allocation_and_users[1::]:
                # check if user has been set to no login
                result = subprocess.run(["finger", "{0}".format(netid)], stdout=subprocess.PIPE)
                no_login = result.stdout.decode("utf-8").find("nologin")
                if no_login == -1:
                    user, was_just_created = CustomUser.objects.get_or_create(username=netid)
                    if was_just_created:
                        email = get_email_from_netid(netid)
                        if 'http' in email:
                            continue
                        print(allocation_name, netid, email)
                        user.email = email
                        user.is_superuser=False
                        user.is_staff=False
                        user.save()
                    allocation, was_just_created = Account.objects.get_or_create(account=allocation_name, user=user)
                    if was_just_created:
                        allocation.save()
