from django.contrib import admin
from .models import Test, Section, Mcq, Subjective, RegisteredUser, McqSubmission, Coding, TestCases
# Register your models here.
admin.site.register(Test)
admin.site.register(Section)
admin.site.register(Mcq)
admin.site.register(Subjective)
admin.site.register(RegisteredUser)
admin.site.register(McqSubmission)
admin.site.register(Coding)
admin.site.register(TestCases)