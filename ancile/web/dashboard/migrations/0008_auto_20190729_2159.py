# Generated by Django 2.2.3 on 2019-07-29 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_remove_policy_read_only'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='predefinedpolicy',
            name='approved',
        ),
        migrations.AddField(
            model_name='permissiongroup',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]
