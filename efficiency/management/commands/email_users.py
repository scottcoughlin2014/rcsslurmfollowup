from django.core.management.base import BaseCommand, CommandError
from efficiency.models import Efficiency
from users.models import CustomUser
from utils.quickstart import send_followup

import subprocess 
import pandas 
import time
import numpy
import datetime

class Command(BaseCommand):
    help = 'Command that emails users about their computing resource efficiency based on certain criteria'

    def add_arguments(self, parser):
        parser.add_argument("--memory-efficiency-threshold", type=float, default = 0.5)
        parser.add_argument("--memory-requested-threshold", type=int, default = 10)
        parser.add_argument("--cpu-efficiency-threshold", type=float, default = 0.5)
        parser.add_argument("--cpus-requested-threshold", type=int, default = 14)
        parser.add_argument("--start-time", default = datetime.datetime.now().strftime("%Y-%m-%d"),
                            help="It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.")
        parser.add_argument("--end-time", default = datetime.datetime.now().strftime("%Y-%m-%d"),
                            help="It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.")
        parser.add_argument("--google-api-token")

    def handle(self, *args, **options):
        # For now we simple print this reflag information
        print("There were {0} jobs that had a CPU efficiency less than 50 percent during this time".format(Efficiency.objects.filter(job_start__gte=options["start_time"]).filter(job_start__lte=options["end_time"]).filter(cpueff__lt=options['cpu_efficiency_threshold']).count()))
        print("""
There were {0}/{1} jobs that requested more than {2}GB of memory and less than {3} CPUs
that have a memory efficiency less than 50 percent during this time
""".format(Efficiency.objects.filter(job_start__gte=options["start_time"]).filter(job_start__lte=options["end_time"]).filter(mem_eff__lt=options['memory_efficiency_threshold']).filter(mem_requested__gt=options['memory_requested_threshold']).filter(number_of_cpus__lt=options['cpus_requested_threshold']).count(), Efficiency.objects.filter(job_start__gte=options["start_time"]).filter(job_start__lte=options["end_time"]).filter(mem_requested__gt=options['memory_requested_threshold']).filter(number_of_cpus__lt=options['cpus_requested_threshold']).count(), options['memory_requested_threshold'], options['cpus_requested_threshold']))
        # loop over jobs where a certain memory efficiency was not met and the user has not been emailed about these jobs
        all_jobs_ids = []
        all_number_of_cpus = []
        all_number_of_nodes = []
        all_memory_requested = []
        all_mem_eff = []
        all_users = []
        all_mem_used = []
        all_emails = []
        for eff in Efficiency.objects.filter(emailed=False).filter(mem_requested__gt=options['memory_requested_threshold']).filter(mem_eff__lt=options['memory_efficiency_threshold']).filter(number_of_cpus__lt=options['cpus_requested_threshold']).filter(job_start__gte=options["start_time"]).filter(job_start__lte=options["end_time"]).order_by('user'): 
            all_jobs_ids.append(eff.jobid)
            all_memory_requested.append(eff.mem_requested)
            all_mem_eff.append(eff.mem_eff)
            all_mem_used.append(eff.mem_used)
            all_number_of_cpus.append(eff.number_of_cpus)
            all_number_of_nodes.append(eff.number_of_nodes)
            all_users.append(eff.user.username)
            all_emails.append(eff.user.email)
        df = pandas.DataFrame({'jobid': all_jobs_ids, 'mem_requested' : all_memory_requested, 'mem_eff' : all_mem_eff, 'user' : all_users, 'email': all_emails, 'number_of_cpus' : all_number_of_cpus, 'mem_used' : all_mem_used, 'nnodes' : all_number_of_nodes})
        for (user, email), utilization in df.groupby(["user", "email"]):
            subject = "Concerning Utilization of Computing Resources by Recent Jobs on QUEST"
            message_text="""
Hello,

The Research Computing Services team at Northwestern is attempting to help general access users understand the differences between the computing resources they request for their job versus the computing resources that end up being used by that job. This effort is meant to help in two ways. First, this can help your FairShare score which determines your priority in receiving computing resources relative to the rest of the community. Second, this can help make sure that we are maximizing the research computing provided by QUEST. To this end, we wanted to inform you of some recent jobs you have submitted which use less than half of the memory you requested for them. We also provide a recommended setting for the memory of each job

"""
            for jobid, mem_eff, mem_requested, num_cpus, mem_used, nnodes in zip(utilization.jobid, utilization.mem_eff, utilization.mem_requested, utilization.number_of_cpus, utilization.mem_used, utilization.nnodes):
                message_text = message_text + """
\tJobID : {0}, Number of Nodes Requested: {1}, Numbers of CPUS per Node Requested {2}, Memory Requested {3}, Memory Requested Per CPU {4}, Memory Utilized {5}, Memory Efficiency {6}

Recommendation #SBATCH --mem-per-cpu={7}
""".format(jobid, nnodes, num_cpus, mem_requested, mem_requested/num_cpus, mem_used, mem_eff, numpy.ceil(mem_used) + 1)

            message_text = message_text + """
Please see https://kb.northwestern.edu/92939 for more information on how to determine the memory footprint of your completed jobs and please do not hesitate to e-mail any question you have to quest-help@northwestern.edu,

Thanks!

Scotty and the Research Computing Services Team

Scott Coughlin, PhD
Computational Specialist
IT Research Computing Services
Northwestern University
s-coughlin@northwestern.edu
"""
            # send email
            send_followup(credentials_token=options['google_api_token'], to='mnballer1992@gmail.com', subject=subject, message_text=message_text)
            job_obj = Efficiency.objects.get(jobid=jobid)
            job_obj.emailed =True
            job_obj.save()
