# Generated by Django 4.2.20 on 2025-05-02 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airflow_app', '0003_remove_course_certificates_remove_course_user_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='tools_handson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tool_name', models.TextField(blank=True, null=True)),
                ('user', models.IntegerField(blank=True, null=True)),
                ('status', models.TextField(default='Not Started')),
                ('task_metadata', models.JSONField(blank=True, default=dict)),
            ],
        )
        
    ]
