# Generated by Django 3.1.7 on 2021-04-09 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queueApp', '0006_qrcode_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='client_email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
