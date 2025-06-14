# Generated by Django 4.2.20 on 2025-06-13 12:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tool_name', models.TextField(blank=True, null=True)),
                ('course_id', models.TextField(blank=True, null=True)),
                ('course_name', models.TextField(blank=True, null=True)),
                ('user', models.IntegerField(blank=True, null=True)),
                ('status', models.TextField(default='Not Started')),
                ('chapters', models.IntegerField(default=0)),
                ('quiz', models.BooleanField(default=False)),
                ('quiz_retries', models.IntegerField(default=0)),
                ('score', models.IntegerField(default=0)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='tools_handson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tool_name', models.TextField(blank=True, null=True)),
                ('user', models.IntegerField(blank=True, null=True)),
                ('status', models.TextField(default='Not Started')),
                ('task_metadata', models.JSONField(blank=True, default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('certificates', models.JSONField(blank=True, default=list)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
