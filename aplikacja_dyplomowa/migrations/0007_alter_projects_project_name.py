# Generated by Django 4.2 on 2023-05-06 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aplikacja_dyplomowa', '0006_alter_projects_user_delete_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projects',
            name='project_name',
            field=models.CharField(max_length=64),
        ),
    ]
