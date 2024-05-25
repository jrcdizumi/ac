# Generated by Django 5.0.6 on 2024-05-25 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='fan_speed',
            field=models.IntegerField(choices=[(1, 'LOW'), (2, 'MIDDLE'), (3, 'HIGH')], default=2, verbose_name='风速'),
        ),
    ]