# Generated by Django 4.2 on 2023-05-06 22:26

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('aplikacja_dyplomowa', '0010_alter_files_user_alter_mainfiles_user_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tags',
            unique_together={('tag_name', 'project', 'user')},
        ),
        migrations.RemoveField(
            model_name='tags',
            name='slug',
        ),
    ]
