# Generated by Django 3.1.2 on 2020-10-08 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medium_scrap', '0006_auto_20201008_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='url',
            field=models.URLField(),
        ),
    ]