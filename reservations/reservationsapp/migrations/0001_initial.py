# Generated by Django 4.2 on 2024-04-22 12:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Gare",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ville", models.CharField(max_length=200)),
                ("nomgare", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="Trajet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("depdh", models.DateTimeField(db_comment="Date et heure de départ")),
                ("arrdh", models.DateTimeField(db_comment="Date et heure d'arrivée")),
                (
                    "arrgare",
                    models.ForeignKey(
                        db_comment="Gare d'arrivée",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="arrivee_trajets",
                        to="reservationsapp.gare",
                    ),
                ),
                (
                    "depgare",
                    models.ForeignKey(
                        db_comment="Gare de départ",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="depart_trajets",
                        to="reservationsapp.gare",
                    ),
                ),
            ],
        ),
    ]
