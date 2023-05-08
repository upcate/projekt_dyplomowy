from django.contrib import admin
from .models import Projects, Tags, ProjectObjects

# Register your models here.
admin.site.register(Projects)
admin.site.register(Tags)
admin.site.register(ProjectObjects)