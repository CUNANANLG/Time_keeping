# Generated by Django 4.1.7 on 2023-04-05 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_timerecord_overtime_hours_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='additional_deductions',
            name='pagibig',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='additional_deductions',
            name='philhealth',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]