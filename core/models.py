from django.db import models
from django.contrib.auth.models import User

class Test(models.Model):
    testid = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class Section(models.Model):
    TYPE_CHOICES = [
        ('MCQ', 'Multiple Choice Question (MCQ)'),
        ('CODING', 'Coding'),
        ('SUBJECTIVE', 'Subjective')
    ]

    sid = models.AutoField(primary_key=True)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    qtype = models.CharField(max_length=10, choices=TYPE_CHOICES)
