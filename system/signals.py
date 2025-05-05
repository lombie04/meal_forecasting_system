from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import SystemLog
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    SystemLog.objects.create(user=user, action='login', description='User logged in')
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    SystemLog.objects.create(user=user, action='logout', description='User logged out')
