from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Projects(models.Model):
    project_name = models.CharField(max_length=16)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class Tags(models.Model):
    tag_name = models.CharField(max_length=16)
    slug = models.SlugField(unique=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)


class ProjectObjects(models.Model):
    object_name = models.CharField(max_length=32)
    object_description = models.TextField()
    connections = models.ManyToManyField('self', symmetrical=False, related_name='connection')
    tags = models.ManyToManyField(Tags)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class Files(models.Model):
    file_name = models.CharField(max_length=16)
    file = models.FileField()
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tags)
    uploadedAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
