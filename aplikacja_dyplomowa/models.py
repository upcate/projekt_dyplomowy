from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=16)
    user_password = models.CharField(max_length=32)
    user_email = models.EmailField()

    def __str__(self):
        return f'Użytkownik {self.username} o id {self.id}, haśle {self.user_password} oraz mailu {self.user_email}'

