# Generated by Django 5.1.1 on 2024-10-17 02:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0008_alter_subject_timeslot'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='semester',
            field=models.CharField(choices=[('1st Semester', '1st Semester'), ('2nd Semester', '2nd Semester')], default='1st Semester', max_length=50),
        ),
        migrations.AlterField(
            model_name='subject',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scheduling.department'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='year_level',
            field=models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4)], null=True),
        ),
    ]