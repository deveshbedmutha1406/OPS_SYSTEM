from django.db import models
from django.contrib.auth.models import User

class Test(models.Model):
    testid = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
