# Generated by Django 5.1.6 on 2025-02-08 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rider', '0005_alter_rideshare_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='ride',
            name='distance',
            field=models.FloatField(default=0.0),
        ),
    ]
