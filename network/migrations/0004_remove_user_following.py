# Generated by Django 3.1.1 on 2020-09-18 22:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_auto_20200918_2212'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='following',
        ),
    ]