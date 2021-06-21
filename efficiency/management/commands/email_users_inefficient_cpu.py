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
    smtpservice = smtplib.SMTP("localhost")
    smtpservice.send_message(message)
    smtpservice.quit()

class Command(BaseCommand):
    help = 'Command that emails users about their computing resource efficiency based on certain criteria'

    def add_arguments(self, parser):
        parser.add_argument("--cpu-efficiency-threshold", type=float, default = 0.25)
        parser.add_argument("--start-time", default = datetime.datetime.now().strftime("%Y-%m-%d"),
                            help="It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.")
        parser.add_argument("--end-time", default = datetime.datetime.now().strftime("%Y-%m-%d"),
                            help="It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.")

    def handle(self, *args, **options):
        print("There were {0} jobs that had a CPU efficiency less than {1} percent during this time".format(Efficiency.objects.filter(job_start__gte=options["start_time"]).filter(job_start__lte=options["end_time"]).filter(cpueff__lt=options['cpu_efficiency_threshold']).count(), options['cpu_efficiency_threshold']))
        # loop over jobs where a certain memory efficiency was not met and the user has not been emailed about these jobs
        all_jobs_ids = []
        all_number_of_cpus = []
        all_number_of_nodes = []
        all_cpu_eff = []
        all_users = []
        all_emails = []
        for eff in Efficiency.objects.filter(user__has_been_emailed=False).filter(emailed=False).filter(job_start__gte=options["start_time"]).filter(job_start__lte=options["end_time"]).filter(cpueff__lt=options['cpu_efficiency_threshold']).order_by('user'): 
            all_jobs_ids.append(eff.jobid)
            all_cpu_eff.append(eff.cpueff)
            all_number_of_cpus.append(eff.number_of_cpus)
            all_number_of_nodes.append(eff.number_of_nodes)
            all_users.append(eff.user.username)
            all_emails.append(eff.user.email)
        df = pandas.DataFrame({'jobid': all_jobs_ids, 'cpu_eff' : all_cpu_eff, 'user' : all_users, 'email': all_emails, 'number_of_cpus' : all_number_of_cpus, 'nnodes' : all_number_of_nodes})
        for (user, email), utilization in df.groupby(["user", "email"]):
            all_jobs = []  
            message_text="""
Dear Quest User,  
<br>
<br>
We are reaching out to inform you about the efficiency of some of your jobs on Quest and a possible opportunity for improving your wait times and more efficiently using computing resources. 
<br>
<br>
Once a month, we sample random Quest jobs to monitor the difference between the requested and utilized computing and memory resources. Our data show that at least one of your jobs, indicated below, requested a larger amount of resources than needed and may be affecting your wait times. 
<br>
<br>
"""
            # Only report full statistics on one job, otherwise simply list the other ones
            count = 0
            for jobid, cpu_eff, num_cpus, nnodes in zip(utilization.jobid, utilization.cpu_eff, utilization.number_of_cpus, utilization.nnodes):
                if count == 0:
                    message_text = message_text + """
\tJobID : {0}
<br>
\tCPUs : {1}
<br>
\tCPU Efficiency {2:.2f}
<br>
<br>
Requesting cpu resources closer to what is needed for your job can improve your priority, which will result in lower wait times. Many times low CPU usage is due to requesting CPUs that your program does not actually utilize. Most programs only run on a single CPU, unless explicitly coded otherwise. 
<br>
<br>
""".format(jobid, num_cpus, cpu_eff)
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
            send_allocation_email(["scottcoughlin2014@u.northwestern.edu", "Scott Coughlin", message_text])
            for ji in all_jobs:
                job_obj = Efficiency.objects.get(jobid=ji)
                job_obj.emailed = True
                job_obj.save()
            user_obj = job_obj.user
            user_obj.has_been_emailed = True
            user_obj.save()
            breakpoint()
