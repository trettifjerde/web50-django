# Generated by Django 4.0.6 on 2022-08-26 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0005_alter_listing_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='starting_bid',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
