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


class Mcq(models.Model):
    qid = models.AutoField(primary_key=True)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    qno = models.IntegerField()
    settersid = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.TextField()
    optionA = models.TextField()
    optionB = models.TextField()
    optionC = models.TextField()
    optionD = models.TextField()
    correct_option = models.CharField(max_length=2, choices=[
        ('A', 'a'), ('B', 'b'), ('C', 'c'), ('D', 'd')
    ])


class Subjective(models.Model):
    qid = models.AutoField(primary_key=True)
    setters_id = models.ForeignKey(User, on_delete=models.CASCADE)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    statement = models.TextField()


class RegisteredUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    embedding1 = models.TextField()
    embedding2 = models.TextField()

    class Meta:
        unique_together = ('user_id', 'test_id')  # Composite Primary Key


class McqSubmission(models.Model):
    subid = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    ques_id = models.ForeignKey(Mcq, on_delete=models.CASCADE)
    marked_option = models.CharField(max_length=2)

    class Meta:
        unique_together = ('user_id', 'test_id', 'ques_id')