# Generated by Django 4.1.7 on 2023-04-05 10:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Additioanl_Deductions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('late_tardiness', models.IntegerField(blank=True, null=True)),
                ('sss', models.IntegerField(blank=True, null=True)),
                ('overtime', models.IntegerField(blank=True, null=True)),
                ('no_of_holiday', models.IntegerField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='edit_employee_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]