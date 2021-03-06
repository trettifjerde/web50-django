# Generated by Django 3.2.8 on 2022-07-17 17:29

import datetime
from django.db import migrations, models
import django.utils.timezone
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_bid_category_comment_listing'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listing',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2022, 7, 17, 17, 29, 31, 457968, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
