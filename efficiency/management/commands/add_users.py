from django.core.management.base import BaseCommand, CommandError
from users.models import CustomUser, Account

import subprocess
import pandas
import time
import datetime
import time

class Command(BaseCommand):
    help = 'Command to track user and account information in order to check on slurm usage/other info and to be able to email them if needed'

    def handle(self, *args, **options):

        # first step is to determine all of the currently active general access allocations
        subprocess.run("awk '{$1=$1}1' /hpc/slurm/northwestern/allocation_log.txt > all_allocations.txt", shell=True)
        df = pandas.read_csv('all_allocations.txt', sep=' ')
        df["Type"] = pandas.to_datetime(df["Type"])
        df = df.loc[df["Type"] > datetime.datetime.now()]
        df = df.loc[~df.Allocation.isin(["a9009", "kellogg", "p30157"])]
        df = df.loc[df.Allocation.apply(lambda x: 'p' in x)]
        active_general_access = df.Allocation.tolist()
        # add b1042
        active_general_access.append('b1042')

        # second step is to identify all the users in each general access allocation
        allocation_user_dict = {}
        for allocation in active_general_access:
             result = subprocess.run(['grep', '{0}'.format(allocation), '/etc/group'],stdout=subprocess.PIPE)
             allocation_user_dict[allocation] = result.stdout.decode('utf-8').split('\n')[0].split(":")[-1].split(",")

        # loop over allocations and users in that allocation
        for allocation_name, users in allocation_user_dict.items():
            for netid in users:
                # check if user has been set to no login
                result = subprocess.run(["finger", "{0}".format(netid)], stdout=subprocess.PIPE)
                no_login = result.stdout.decode("utf-8").find("nologin")
                if no_login == -1:
                    if netid in ['jsteege', 'akh9585', 'akh9585', 'apv175', 'barryc', 'sas4990', 'sbc538', 'zhs7376', 'ctg9595', 'jon9348', 'damir', 'apm3087']:
                        continue
                    user, was_just_created = CustomUser.objects.get_or_create(username=netid)
                    if was_just_created:
                        print(allocation_name, netid, "{0}@e.northwestern.edu".format(netid))
                        user.email = "{0}@e.northwestern.edu".format(netid)
                        user.is_superuser=False
                        user.is_staff=False
                        user.save()
                    allocation, was_just_created = Account.objects.get_or_create(account=allocation_name, user=user)
                    if was_just_created:
                        allocation.save()
