# Generated by Django 4.0.6 on 2022-08-29 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0007_alter_bid_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='starting_bid',
            field=models.IntegerField(),
        ),
    ]
