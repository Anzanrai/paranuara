# Generated by Django 2.2.7 on 2019-12-03 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20191203_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='people_id',
            field=models.CharField(max_length=120),
        ),
    ]