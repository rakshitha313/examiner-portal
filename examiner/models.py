from django.db import models
from django.contrib.auth.models import User


class Examiner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)
    organization = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username
# Create your models here.
