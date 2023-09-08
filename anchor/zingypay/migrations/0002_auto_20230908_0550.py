# Generated by Django 3.2.20 on 2023-09-08 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zingypay', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='federation_address',
            field=models.CharField(default=(), max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mnemonic',
            field=models.TextField(default=()),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='stellar_secret_key',
            field=models.CharField(default=(), max_length=56),
            preserve_default=False,
        ),
    ]
