# Generated by Django 4.2 on 2023-04-22 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aplikacja_dyplomowa', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='user_id',
        ),
    ]
