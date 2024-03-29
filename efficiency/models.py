from django.db import models
from django.conf import settings
from users.models import Account
# Create your models here.

class Efficiency(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        default=1,
    )
    jobid = models.CharField(max_length=100)
    number_of_cpus = models.IntegerField()
    number_of_nodes = models.IntegerField()
    cpueff = models.FloatField()
    mem_eff = models.FloatField()
    mem_used = models.FloatField()
    mem_requested = models.FloatField()
    emailed = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    job_start = models.DateTimeField()
    job_end = models.DateTimeField()
