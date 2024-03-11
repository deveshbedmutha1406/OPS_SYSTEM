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

    class Meta:
        unique_together = ('test_id', 'qtype')

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
    embedding1 = models.TextField()    # this are face embeddings of user.
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


class SubjectiveSubmission(models.Model):
    subid = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    ques_id = models.ForeignKey(Subjective, on_delete=models.CASCADE)
    submitted_answer = models.TextField()

    class Meta:
        unique_together = ('user_id', 'test_id', 'ques_id')


class Coding(models.Model):
    qid = models.AutoField(primary_key=True)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    settersid = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=1)
    title = models.CharField(max_length=1003)
    body = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    constraints = models.TextField()
    sample_input = models.TextField()
    sample_output = models.TextField()
    time_limit = models.IntegerField(default=1)
    memory_limit = models.IntegerField(default=256)

    def __str__(self):
        return self.title


def user_directory_path_input(instance, filename):
    return "QuestionData/{0}/input/{1}".format(instance.test_id.testid, filename)


def user_directory_path_output(instance, filename):
    return "QuestionData/{0}/output/{1}".format(instance.test_id.testid, filename)

class TestCases(models.Model):
    tid = models.AutoField(primary_key=True)
    q_id = models.ForeignKey(Coding, on_delete=models.CASCADE)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    tc_input = models.FileField(upload_to=user_directory_path_input)
    tc_output = models.FileField(upload_to=user_directory_path_output)
