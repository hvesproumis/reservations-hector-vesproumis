# Generated by Django 4.2 on 2024-05-06 06:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reservationsapp", "0003_alter_gare_station_name"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Gare",
            new_name="Station",
        ),
    ]
