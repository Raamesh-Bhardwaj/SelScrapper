# Generated by Django 5.0.6 on 2024-06-19 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EntitiesMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('artist_name', models.CharField(max_length=100)),
                ('artist_role', models.CharField(max_length=100)),
                ('program_name', models.CharField(max_length=100)),
                ('Date', models.DateField(blank=True, null=True)),
                ('Time', models.TimeField(blank=True, null=True)),
                ('auditorium', models.CharField(max_length=100)),
            ],
        ),
    ]
