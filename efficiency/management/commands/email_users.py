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

def send_allocation_email(email_values: list) -> None:
    """Emails users for new allocation and renewal notices.
    Values in the email_values list are as follows:
    0: email address
    1: name
    2: message_text
    """
    message = email.message.EmailMessage()
    message["From"] = email.headerregistry.Address(
        "Research Computing", "quest-help", "northwestern.edu")
    local_part: str = email_values[0].split("@")[0]
    domain: str = email_values[0].split("@")[1]
    message["To"] = email.headerregistry.Address(email_values[1],
                                                 local_part, domain)
    # BCC Scotty so that we have a log of the email being sent
    message["bcc"] = email.headerregistry.Address("Scott Coughlin",
                                                  "s-coughlin",
                                                  "northwestern.edu")
    message["Subject"] = "Opportunity to Maximize Your Quest Jobs Efficiency"
    # Set HTML as the primary method with a plaintext failover
    message.set_content(email_values[2])
    message.add_alternative(email_values[2], subtype="html")
    smtpservice = smtplib.SMTP("localhost")
    smtpservice.send_message(message)
    smtpservice.quit()

class Command(BaseCommand):
    help = 'Command that emails users about their computing resource efficiency based on certain criteria'

    def add_arguments(self, parser):
        parser.add_argument("--memory-efficiency-threshold", type=float, default = 0.1)
        parser.add_argument("--memory-requested-threshold", type=int, default = 16)
        parser.add_argument("--cpu-efficiency-threshold", type=float, default = 0.5)
        parser.add_argument("--cpus-requested-threshold", type=int, default = 20)
        parser.add_argument("--start-time", required=True,
                            help="It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.")
        parser.add_argument("--end-time", required=True,
                            help="It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.")

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
        for eff in Efficiency.objects.filter(user__active_nu_member=True).filter(user__has_been_emailed=False).filter(emailed=False).filter(mem_requested__gt=options['memory_requested_threshold']).filter(mem_eff__lt=options['memory_efficiency_threshold']).filter(number_of_cpus__lte=options['cpus_requested_threshold']).filter(job_start__gte=options["start_time"]).filter(job_start__lte=options["end_time"]).order_by('user'): 
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
            all_jobs = []  
            message_text="""
Dear Quest User,  
<br>
<br>
We are reaching out to inform you about the efficiency of some of your jobs on Quest and a possible opportunity for reducing your jobs’ wait times and improving how efficiently they use computing resources.
<br>
<br>
Once a month, we sample random Quest jobs to monitor the difference between the requested and utilized computing and memory resources. Our data from {0} to {1} shows that at least one of your jobs, indicated below, requested a larger amount of resources than needed and this may be affecting your job’s wait time.
<br>
<br>
""".format(options["start_time"], options["end_time"])
            # Only report full statistics on one job, otherwise simply list the other ones
            count = 0
            for jobid, mem_eff, mem_requested, num_cpus, mem_used, nnodes in zip(utilization.jobid, utilization.mem_eff, utilization.mem_requested, utilization.number_of_cpus, utilization.mem_used, utilization.nnodes):
                if count == 0:
                    message_text = message_text + """
\tJobID : {0}
<br>
\tTotal Memory Requested : {1}
<br>
\tMemory Requested Per CPU : {2:.2f}
<br>
\tTotal Memory Utilized : {3:.2f}
<br>
\tMemory Efficiency : {4:.4f}
<br>
<br>
Requesting memory resources closer to what is needed for your job can improve your priority, which will result in lower wait times. Our recommendation is to use the following memory for this job:
<br>
<br>
Recommendation #SBATCH --mem={5}G
<br>
<br>
""".format(jobid, mem_requested, mem_requested/num_cpus, mem_used, mem_eff, int(numpy.ceil(mem_used) + 2))
                    count = 1
                all_jobs.append(jobid)

            message_text = message_text + """
Additional jobs that should be considered for adjustment have been identified with the following IDs: {0}. 
<br>
<br>
Please visit <a href="https://kb.northwestern.edu/92939">Specifying Memory for Jobs on Quest</a> for more information on how to determine the memory used for your completed jobs including the ones listed above. If you have any questions or need support please contact quest-help@northwestern.edu.
<br>
<br>
Sincerely, 
<br>
Arman 
<br>
-- 
<br>
Arman Pazouki, PhD (he/him/his) 
<br>
Lead Computational Specialist  
<br>
Northwestern IT Research Computing Services 
<br>
Northwestern University 
<br>
pazouki@northwestern.edu  
<br>
847.467.7349 
""".format(','.join([str(i) for i in all_jobs]))
            # send email
            send_allocation_email([email, email, message_text])
            for ji in all_jobs:
                job_obj = Efficiency.objects.get(jobid=ji)
                job_obj.emailed = True
                job_obj.save()
            user_obj = job_obj.user
            user_obj.has_been_emailed = True
            user_obj.save()
