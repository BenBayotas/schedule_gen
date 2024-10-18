# Generated by Django 5.1.1 on 2024-10-17 03:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0009_subject_semester_alter_subject_department_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='courses',
        ),
        migrations.RemoveField(
            model_name='room',
            name='priority',
        ),
        migrations.AddField(
            model_name='room',
            name='department_priority',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scheduling.department'),
        ),
    ]