# Generated by Django 2.0.1 on 2018-04-14 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('duradiff', '0009_auto_20180414_1308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salary',
            name='netbasic',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ]