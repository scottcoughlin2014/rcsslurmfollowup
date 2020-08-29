from django.db import models
from django.conf import settings

# Create your models here.

class Efficiency(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    jobid = models.IntegerField()
    number_of_cpus = models.IntegerField()
    cpueff = models.FloatField()
    mem_eff = models.FloatField()
    mem_used = models.FloatField()
    mem_requested = models.FloatField()
    emailed = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
