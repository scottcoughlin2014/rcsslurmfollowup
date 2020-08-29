from django.core.management.base import BaseCommand, CommandError
from users.models import CustomUser, Account
from efficiency.models import Efficiency

import subprocess 
import pandas 
import time
import datetime

class Command(BaseCommand):
    help = 'Command to update efficiency tables with memory requested and memory used information for a given day'

    def add_arguments(self, parser):
        parser.add_argument("--start-time", default = datetime.datetime.now().strftime("%m/%d/%y"))
        parser.add_argument("--end-time", default = datetime.datetime.now().strftime("%m/%d/%y"))
        parser.add_argument("--nsamples", type=int, default=5)

    def handle(self, *args, **options):
        # loop over all users in quest
        for user in CustomUser.objects.all(): 
            netid = user.username 
            # figure out how many accounts this user is a part of
            accounts = Account.objects.filter(user=user) 
            for account in accounts: 
                # use sacct to find jobids of jobs from a given day, and whether they completed or not
                result = subprocess.run(['sacct', '--user={0}'.format(netid), '--account={0}'.format(account.account), '-X', '--starttime={0}'.format(options['start_time']), '--endtime={0}'.format(options['end_time']), "--format=JobID,JobName,Partition,Account,AllocCPUS,State,ExitCode,NNodes"], stdout=subprocess.PIPE) 
                result = result.stdout.decode("utf-8") 
                # have they submitted jobs during this time frame? 
                if len(result.split("\n")) > 3: 
                    # if yes make a helpful dataframe for thos jobs
                    job_df = pandas.DataFrame([i.split(" ") for i in result.replace("  "," ").replace("  ", " ").replace("  ", " ").replace("  "," ").replace("  "," ").split("\n")], columns=["JobID", "JobName", "Partition", "Account", "AllocCPUS", "State", "ExitCode", "NNodes", "None", "None1"]) 
                    breakpoint()
                    breakpoint()
                    # did any of their jobs complete that day?
                    job_df = job_df.loc[job_df.State == "COMPLETED"] 
                    if job_df.empty:
                        continue

                    # take a sampling of the completed jobs
                    job_df = job_df.sample(n=min(options['nsamples'], len(job_df))) 
                    for jobid, numcpus, nnodes in zip(job_df.JobID, job_df.AllocCPUS, job_df.NNodes):
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

                        eff = Efficiency(user=user, jobid=jobid, emailed=False, cpueff=cpueff, mem_eff=mem_eff, mem_used=mem_used, mem_requested=mem_requested, number_of_cpus=numcpus, number_of_nodes=nnodes)
                        eff.save()
