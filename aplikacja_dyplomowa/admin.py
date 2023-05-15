from django.contrib import admin
from .models import Projects, Tags, ProjectObjects, Files, MainFiles

# Register your models here.
admin.site.register(Projects)
admin.site.register(Tags)
admin.site.register(ProjectObjects)
admin.site.register(Files)
admin.site.register(MainFiles)
