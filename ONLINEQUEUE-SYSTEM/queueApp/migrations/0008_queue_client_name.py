# Generated by Django 3.1.7 on 2021-04-10 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queueApp', '0007_queue_client_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='client_name',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
