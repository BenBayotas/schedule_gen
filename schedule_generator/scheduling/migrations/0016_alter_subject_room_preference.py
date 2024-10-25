# Generated by Django 5.1.1 on 2024-10-25 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0015_subject_room_preference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='room_preference',
            field=models.CharField(blank=True, choices=[('Lecture Room', 'Lecture Room'), ('PE Hall', 'PE Hall'), ('Gym Hall', 'Gym Hall'), ('Civil Engineering Lab', 'Civil Engineering Lab'), ('JEEP Start', 'JEEP Start'), ('JEEP Accelerate', 'JEEP Accelerate'), ('Nursing Lab', 'Nursing Lab'), ('Human Anatomy Simulation Center', 'Human Anatomy Simulation Center'), ('Computer Laboratory', 'Computer Laboratory'), ('EIRC', 'EIRC'), ('DSAC', 'DSAC'), ('TBI MOESIS', 'TBI MOESIS'), ('ETP Drawing Room', 'ETP Drawing Room'), ('Chemistry Lab', 'Chemistry Lab'), ('Biology Room', 'Biology Room'), ('Criminology Lab', 'Criminology Lab'), ('Criminology Lecture Room', 'Criminology Lecture Room'), ('Hotel de Saturnino', 'Hotel de Saturnino'), ('Physics Lab', 'Physics Lab'), ('Kitchen', 'Kitchen'), ('Drawing Room', 'Drawing Room')], max_length=64, null=True),
        ),
    ]