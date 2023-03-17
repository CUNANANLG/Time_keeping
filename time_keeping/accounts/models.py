from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager


class TimeRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    total_time = models.DurationField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.time_out and self.time_in:
            self.total_time = self.time_out - self.time_in
        super().save(*args, **kwargs)
    
    def total_time_display(self):
        if self.time_out and self.time_in:
            duration = self.time_out - self.time_in
            hours, minutes, seconds = duration.seconds // 3600, (duration.seconds // 60) % 60, duration.seconds % 60
            return f"{hours} hours, {minutes} minutes"
        return ""
    
    total_time_display.short_description = 'Total time'


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, id, position, **extra_fields):
        if not first_name or not last_name or not id or not position:
            raise ValueError('First name, last name, id, and position fields must be set')
        username = f"{id}-{first_name}-{last_name}"
        user = self.model(username=username, position=position, **extra_fields)
        user.set_password(str(id))
        user.save()
        return user

    def create_superuser(self, first_name, last_name, id, position, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(first_name, last_name, id, position, password=password, **extra_fields)

    def normalize_username(self, username):
        return username.strip().lower()


class User(AbstractUser):
    username=models.CharField(max_length=150,unique=True, blank=False)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    id = models.CharField(max_length=255,unique=True,primary_key=True)
    position = models.ForeignKey('Position', on_delete=models.PROTECT, related_name='users', blank=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'position']

    objects = UserManager()


class Position(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
