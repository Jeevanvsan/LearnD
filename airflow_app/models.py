
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    certificates = models.JSONField(default=list,blank=True) 

    def __str__(self):
        return self.user.username
    
class Course(models.Model):
    tool_name = models.TextField(null=True, blank=True)
    course_id = models.TextField(null=True, blank=True)
    course_name = models.TextField(null=True, blank=True)
    user = models.IntegerField(null=True,blank=True)
    status = models.TextField(default='Not Started') 
    chapters = models.IntegerField(default=0) 
    quiz = models.BooleanField(default=False) 
    quiz_retries = models.IntegerField(default=0) 
    score = models.IntegerField(default=0) 
    start_time = models.DateTimeField(default=timezone.now) 
    updated_time = models.DateTimeField(auto_now=True) 
    end_time = models.DateTimeField(blank=True, null=True) 

class tools_handson(models.Model):
    tool_name = models.TextField(null=True, blank=True)
    user = models.IntegerField(null=True,blank=True)
    status = models.TextField(default='Not Started') 
    task_metadata = models.JSONField(default=dict,blank=True) 


