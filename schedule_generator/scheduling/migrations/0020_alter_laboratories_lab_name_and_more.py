# Generated by Django 5.1.1 on 2024-10-26 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0019_lectureroom_pegymhall_laboratories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='laboratories',
            name='lab_name',
            field=models.CharField(default='Laboratory', max_length=64),
        ),
        migrations.AlterField(
            model_name='lectureroom',
            name='room_name',
            field=models.CharField(default='Lecture Room', max_length=64),
        ),
        migrations.AlterField(
            model_name='pegymhall',
            name='hall_name',
            field=models.CharField(default='PE Hall', max_length=64),
        ),
    ]