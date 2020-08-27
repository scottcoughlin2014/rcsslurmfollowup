from django.db import models
from django.conf import settings

# Create your models here.

class Efficiency(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    jobid = models.IntegerField()
    cpueff = models.FloatField()
    memeff = models.FloatField()
    emailed = models.BoolField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
