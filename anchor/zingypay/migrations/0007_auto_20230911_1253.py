# Generated by Django 3.2.20 on 2023-09-11 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zingypay', '0006_auto_20230911_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='code',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='currency',
            name='name',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='currency',
            name='symbol',
            field=models.CharField(max_length=100),
        ),
    ]
