# Generated by Django 4.1.7 on 2023-03-27 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_totalpresent'),
    ]

    operations = [
        migrations.AddField(
            model_name='totalpresent',
            name='time_record',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='accounts.timerecord'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='totalpresent',
            name='date',
            field=models.DateField(),
        ),
    ]