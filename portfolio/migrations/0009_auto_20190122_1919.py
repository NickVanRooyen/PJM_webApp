# Generated by Django 2.0.7 on 2019-01-22 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0008_auto_20190121_1927'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trade',
            old_name='broker',
            new_name='account',
        ),
        migrations.RenameField(
            model_name='tradehistory',
            old_name='broker',
            new_name='account',
        ),
        migrations.AddField(
            model_name='tradehistory',
            name='fxCharge',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
        migrations.AddField(
            model_name='tradehistory',
            name='transactionFee',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
    ]
