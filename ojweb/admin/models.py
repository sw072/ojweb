from django.db import models

# Create your models here.
class Dayrank(models.Model):
    rank = models.CommaSeparatedIntegerField(max_length=128)
    day = models.DateField()
    jointime = models.DateTimeField(auto_now_add=True)
    
class Monthrank(models.Model):
    rank = models.CommaSeparatedIntegerField(max_length=128)
    month = models.DateField()
    jointime = models.DateTimeField(auto_now_add=True)

class Sysconfig(models.Model):
    status = models.BooleanField(default=True)
    dayranknum = models.IntegerField(default=3)
    monthranknum = models.IntegerField(default=3)
