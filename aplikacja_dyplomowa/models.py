from django.db import models
import uuid


# Create your models here.


class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    username = models.CharField(max_length=16)
    user_password = models.CharField(max_length=32)
    user_email = models.EmailField()

    def __str__(self):
        return f'Użytkownik {self.username} o id {self.id}, haśle {self.user_password} oraz mailu {self.user_email}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Projects(models.Model):
    project_name = models.CharField(max_length=16)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)


class Tags(models.Model):
    tag_name = models.CharField(max_length=16)
    slug = models.SlugField(unique=True)


class Objects(models.Model):
    object_name = models.CharField(max_length=32)
    object_description = models.TextField()
    connections = models.ManyToManyField('self', symmetrical=False)
    tags = models.ManyToManyField(Tags)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)


class Files(models.Model):
    file_name = models.CharField(max_length=16)
    file = models.FileField()
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tags)
