# Generated by Django 2.0.7 on 2018-12-19 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0003_auto_20181219_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='action',
            field=models.CharField(choices=[('', 'Action'), ('buy', 'BUY'), ('sell', 'SELL')], help_text='"Buy" or "Sell"', max_length=4, verbose_name='Action'),
        ),
    ]
