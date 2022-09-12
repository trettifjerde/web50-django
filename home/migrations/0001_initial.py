# Generated by Django 4.0.6 on 2022-08-30 19:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('short_description', models.CharField(max_length=140)),
                ('description', models.TextField(blank=True)),
                ('frontend', models.CharField(blank=True, max_length=200)),
                ('backend', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Pic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desktop', models.ImageField(blank=True, upload_to='')),
                ('mobile', models.ImageField(blank=True, upload_to='')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pics', to='home.project')),
            ],
        ),
    ]
