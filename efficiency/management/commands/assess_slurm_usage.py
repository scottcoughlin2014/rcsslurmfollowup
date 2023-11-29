from django.core.management.base import BaseCommand, CommandError
from users.models import CustomUser, Account
from efficiency.models import Efficiency
from io import StringIO

import subprocess 
import pandas 
import time
import datetime
import csv
import warnings

warnings.filterwarnings("ignore")

class Command(BaseCommand):
    help = 'Command to update efficiency tables with memory requested and memory used information for a given day'

    def add_arguments(self, parser):
        parser.add_argument("--start-time", required=True) 
        parser.add_argument("--end-time", required=True) 
        parser.add_argument("--nsamples", type=int, default=5)

    def handle(self, *args, **options):
        # based on start and stop time, create a date range so we can load daily job data from /artspace/reports/daily/
        daily_date_range = [[i.strftime("%m%d%y"),(i + datetime.timedelta(days=1)).strftime("%m%d%y")] for i in pandas.date_range(start=options['start_time'],end=options['end_time']).to_pydatetime()]
        
        all_jobs_df = pandas.DataFrame()
        # use sacct to find jobids of all completed jobs over the supplied time period
        for date in daily_date_range:
            df = pandas.read_csv("/artspace/reports/daily/quest_report_{0}_{1}".format(date[0], date[1]), delimiter="|")
            df = df.loc[df.State == "COMPLETED"]
            all_jobs_df = all_jobs_df.append(df)

        # loop over all users in quest
        for user in CustomUser.objects.filter(active_nu_member=True): 
            netid = user.username 
            # figure out how many accounts this user is a part of
            accounts = Account.objects.filter(user=user)
            for account in accounts:
                job_df = all_jobs_df.loc[(all_jobs_df.Account == account.account) & (all_jobs_df.User == netid)]
                # have they submitted jobs during this time frame? 
                if not job_df.empty: 
                    # take a sampling of the completed jobs (number of samples will depend on how many days of data we have)
                    job_df = job_df.sample(n=min(options['nsamples'], len(job_df))) 
                    for jobid, numcpus, nnodes, start_time, end_time in zip(job_df.JobID, job_df.ReqCPUS, job_df.AllocNodes, job_df.Start, job_df.End):
                        try:
                            result = subprocess.run(["seff", "{0}".format(jobid)], stdout=subprocess.PIPE)  
                            result = result.stdout.decode("utf-8").split("\n")

                            # find correct indicies
                            for i in range(len(result)):
                                if "CPU Efficiency" in result[i]:
                                    cpueff_index = i
                                elif "Memory Efficiency" in result[i]:
                                    mem_eff_index = i
                                elif "Memory Utilized" in result[i]:
                                    mem_used_index = i

                            cpueff = float(result[cpueff_index].split("CPU Efficiency: ")[-1].split("%")[0])*0.01
                            mem_eff = float(result[mem_eff_index].split("Memory Efficiency: ")[-1].split("%")[0])*0.01
                            mem_used_unit = result[mem_used_index].split("Memory Utilized: ")[-1].split(" ")[-1]
                            mem_used = float(result[mem_used_index].split("Memory Utilized: ")[-1].split(" ")[0])
                            if mem_used_unit == "MB":
                                mem_used = mem_used/1000
                            if mem_used_unit == "TB":
                                mem_used = mem_used * 1000
                            if mem_used_unit == "EB":
                                continue

                            mem_requested_unit = result[mem_eff_index].split("Memory Efficiency: ")[-1].split(" of ")[-1].split(" ")[-1]
                            mem_requested = float(result[mem_eff_index].split("Memory Efficiency: ")[-1].split(" of ")[-1].split(" ")[0])
                            if mem_requested_unit == "MB":
                                mem_requested = mem_requested/1000
                            if mem_requested_unit == "TB":
                                mem_requested = mem_requested * 1000

                            eff = Efficiency(user=user, account=account, jobid=jobid, emailed=False, cpueff=cpueff, mem_eff=mem_eff, mem_used=mem_used, mem_requested=mem_requested, number_of_cpus=numcpus, number_of_nodes=nnodes, job_start=start_time, job_end=end_time)
                            eff.save()
                        except:
                            print("Processing of jobid {0} from user {1} failed".format(jobid, netid))
