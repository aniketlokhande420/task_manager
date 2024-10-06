from django.db import models
# Create your models here.

from django.contrib.auth.models import User
from django.utils import timezone

# UserProfile model to extend the default Django User model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=True, null=True)  # Field for OTP
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.email

# Task model for handling user tasks
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
