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
        parser.add_argument("--start-time", default = datetime.datetime.now().strftime("%m/%d/%y"))
        parser.add_argument("--end-time", default = datetime.datetime.now().strftime("%m/%d/%y"))
        parser.add_argument("--nsamples", type=int, default=5)

    def handle(self, *args, **options):
        # use sacct to find jobids of all completed jobs over the supplied time period
        f = StringIO()
        result = subprocess.run(['sacct', '-X', '--starttime={0}'.format(options['start_time']), '--endtime={0}'.format(options['end_time']), "--format=JobID,JobName,Partition,Account,User,AllocCPUS,State,ExitCode,NNodes,Start", "--parsable", "--state=cd", "--allusers"], stdout=subprocess.PIPE)
        csv.writer(f).writerows([[i] for i in result.stdout.decode("utf-8").split("\n") if i])
        all_jobs_df = pandas.read_csv(StringIO(f.getvalue()), delimiter="|")
        all_jobs_df = all_jobs_df.loc[all_jobs_df.State == "COMPLETED"]
        f.close()

        # loop over all users in quest
        for user in CustomUser.objects.filter(active_nu_member=True): 
            netid = user.username 
            # figure out how many accounts this user is a part of
            accounts = Account.objects.filter(user=user) 
            for account in accounts: 
                job_df = all_jobs_df.loc[(all_jobs_df.Account == account.account) & (all_jobs_df.User == netid)]
                # have they submitted jobs during this time frame? 
                if not job_df.empty: 
                    # take a sampling of the completed jobs
                    job_df = job_df.sample(n=min(options['nsamples'], len(job_df))) 
                    for jobid, numcpus, nnodes, time in zip(job_df.JobID, job_df.AllocCPUS, job_df.NNodes, job_df.Start):
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

                            eff = Efficiency(user=user, jobid=jobid, emailed=False, cpueff=cpueff, mem_eff=mem_eff, mem_used=mem_used, mem_requested=mem_requested, number_of_cpus=numcpus, number_of_nodes=nnodes, job_start=time)
                            eff.save()
                        except:
                            print("Processing of jobid {0} from user {1} failed".format(jobid, netid))
