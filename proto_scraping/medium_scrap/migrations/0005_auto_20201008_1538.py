# Generated by Django 3.1.2 on 2020-10-08 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medium_scrap', '0004_article_sub_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='claps',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='responses',
            field=models.IntegerField(null=True),
        ),
    ]
