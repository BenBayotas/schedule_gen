# Generated by Django 5.1.1 on 2024-10-17 04:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0010_remove_room_courses_remove_room_priority_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='weekly_duration',
        ),
    ]
