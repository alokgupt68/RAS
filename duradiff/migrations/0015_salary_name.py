# Generated by Django 2.0.4 on 2018-04-22 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('duradiff', '0014_auto_20180422_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='salary',
            name='name',
            field=models.CharField(default=' ', max_length=45),
        ),
    ]