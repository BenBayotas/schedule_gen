# Generated by Django 5.1.1 on 2024-10-26 04:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0018_timeslot_subjectsession'),
    ]

    operations = [
        migrations.CreateModel(
            name='LectureRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.CharField(max_length=15, unique=True)),
                ('room_name', models.CharField(blank=True, max_length=64, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PEGymHall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hall_id', models.CharField(max_length=15, unique=True)),
                ('hall_name', models.CharField(blank=True, max_length=64, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Laboratories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lab_id', models.CharField(max_length=15, unique=True)),
                ('lab_name', models.CharField(blank=True, max_length=64, null=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scheduling.department')),
            ],
        ),
    ]
