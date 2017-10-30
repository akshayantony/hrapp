from django.contrib import admin

from .models import Candidate,Jobs

admin.site.register(Candidate)
admin.site.register(Jobs)