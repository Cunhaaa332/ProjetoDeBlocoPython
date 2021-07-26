from django.db import models

# Create your models here.

class SchedTime(models.Model):
    start_time = models.CharField(max_length=200)
    stop_time = models.CharField(max_length=200)