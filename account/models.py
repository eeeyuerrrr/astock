from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE, related_name='userprofile')
    nickname = models.CharField(max_length=10, null=False, unique=True)
    activate_key = models.CharField(max_length=200, null=True)
    activate_key_expires = models.DateTimeField(null=True)
    reset_pw_key = models.CharField(max_length=200, null=True)
    reset_pw_key_expires = models.DateTimeField(null=True)


    def __str__(self):
        return 'user {}'.format(self.user.username)
