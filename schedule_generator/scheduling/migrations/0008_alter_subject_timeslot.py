# Generated by Django 5.1.1 on 2024-10-17 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0007_alter_subject_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='timeslot',
            field=models.CharField(default='7:30AM - 9:00AM', max_length=50),
        ),
    ]