from django.db import models
from django.contrib.auth.hashers import make_password
import uuid


# Create your models here.


class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    username = models.CharField(max_length=16)
    user_password = models.CharField(max_length=128)
    user_email = models.EmailField()
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Użytkownik {self.username} o id {self.id}, haśle {self.user_password} oraz mailu {self.user_email}. Konto zostało założone: {self.createdAt}'

    def save(self, *args, **kwargs):
        self.user_password = make_password(self.user_password)
        super().save(*args, **kwargs)


class Projects(models.Model):
    project_name = models.CharField(max_length=16)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
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
