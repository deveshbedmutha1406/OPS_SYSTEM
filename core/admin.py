from django.contrib import admin
from .models import Test, Section, Mcq, Subjective, RegisteredUser
# Register your models here.
admin.site.register(Test)
admin.site.register(Section)
admin.site.register(Mcq)
admin.site.register(Subjective)
admin.site.register(RegisteredUser)