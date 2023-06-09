from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.db.models import Sum
from django.urls import reverse
import datetime

class Additional_Deductions(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='edit_employee_profile'
        )
    late_tardiness = models.IntegerField(null=True, blank=True, default=0)
    sss = models.IntegerField(null=True, blank=True, default=0)
    overtime = models.IntegerField(null=True, blank=True, default=0)
    no_of_holiday = models.IntegerField(null=True, blank=True, default=0)
    pagibig = models.IntegerField(null=True, blank=True, default=0)
    philhealth = models.IntegerField(null=True, blank=True, default=0)




class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile')
    salary = models.IntegerField(null=True, blank=True)


class TotalPresent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    present_count = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.date.strftime('%B %Y')} - {self.present_count} present(s)"

class TimeRecord(models.Model):
    WORK_STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('undertime', 'Undertime'),
        ('overtime', 'Overtime'),
        ('halfday', 'Half Day'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    total_time = models.DurationField(null=True, blank=True)
    work_status = models.CharField(max_length=20, choices=WORK_STATUS_CHOICES, null=True, blank=True)
    total_present = models.ForeignKey('TotalPresent',null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    overtime_minutes = models.IntegerField(default=0)
    overtime_hours = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user} - {self.time_in}"
    
    def save(self, *args, **kwargs):
        if self.time_out and self.time_in:
            start_time = datetime.datetime.strptime('08:30:00', '%H:%M:%S').time()
            workday_start = datetime.datetime.combine(self.time_in.date(), start_time)

            if self.time_in < workday_start:
                self.work_status = 'Absent'
            else:
                self.total_time = self.time_out - self.time_in
                total_time_minutes = self.total_time.total_seconds() // 60
                if self.time_out is None:
                    self.work_status = ''
                elif total_time_minutes >= 300 and total_time_minutes < 540:
                    self.work_status = 'Undertime'
                elif total_time_minutes <= 240:
                    self.work_status = 'Half Day'
                elif total_time_minutes >= 540 and total_time_minutes < 600:
                    self.work_status = 'Present'
                elif total_time_minutes >= 600:
                    if self.user.id == 4:
                        self.work_status = 'Overtime'
                        excess_minutes = total_time_minutes - 600
                        self.overtime_minutes = excess_minutes
                        self.overtime_hours = excess_minutes / 60
                    else:
                        self.work_status = 'Overtime'
                        excess_minutes = total_time_minutes - 510
                        self.overtime_minutes = excess_minutes
                        self.overtime_hours = excess_minutes / 60

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
class MonthlyTotalPresent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_present = models.IntegerField()
    month = models.DateField()



class Position(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
