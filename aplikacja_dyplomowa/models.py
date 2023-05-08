from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Projects(models.Model):
    project_name = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['project_name', 'user']

    def __repr__(self):
        return f'{self.project_name}'

    def __str__(self):
        return self.__repr__()


class Tags(models.Model):
    tag_name = models.CharField(max_length=16)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['tag_name', 'project', 'user']

    def __repr__(self):
        return f'{self.tag_name}'

    def __str__(self):
        return self.__repr__()


class ProjectObjects(models.Model):
    object_name = models.CharField(max_length=32)
    object_description = models.TextField()
    connections = models.ManyToManyField('self', symmetrical=False, related_name='connection')
    tags = models.ManyToManyField(Tags)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['object_name', 'project', 'user']

    def __str__(self):
        return f'{self.object_name}'


class Files(models.Model):
    file_name = models.CharField(max_length=16)
    file = models.FileField()
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tags)
    uploadedAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['file_name', 'project', 'user']


class MainFiles(models.Model):
    file_name = models.CharField(max_length=16)
    file = models.FileField()
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    uploadedAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['file_name', 'project', 'user']
