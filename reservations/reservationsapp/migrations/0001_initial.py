# Generated by Django 4.2 on 2024-05-03 11:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import reservationsapp.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Client",
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
                ("first_name", models.CharField(max_length=100, verbose_name="Prénom")),
                ("last_name", models.CharField(max_length=100, verbose_name="Nom")),
                ("email", models.EmailField(max_length=254, verbose_name="Email")),
                ("address", models.CharField(max_length=255, verbose_name="Adresse")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="client",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
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
                ("city", models.CharField(max_length=200)),
                ("station_name", models.CharField(max_length=200)),
                ("longitude", models.FloatField(blank=True, max_length=10, null=True)),
                ("latitude", models.FloatField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Journey",
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
                (
                    "departure_date_time",
                    models.DateTimeField(db_comment="Date et heure de départ"),
                ),
                (
                    "arrival_date_time",
                    models.DateTimeField(db_comment="Date et heure d'arrivée"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Passager",
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
                ("first_name", models.CharField(max_length=100, verbose_name="Prénom")),
                ("last_name", models.CharField(max_length=100, verbose_name="Nom")),
                (
                    "date_of_birth",
                    models.DateField(
                        blank=True, null=True, verbose_name="Date de naissance"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="passagers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Reservation",
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
                (
                    "reservation_date",
                    models.DateField(
                        auto_now_add=True, verbose_name="Date de la réservation"
                    ),
                ),
                (
                    "if_number",
                    models.CharField(
                        default=reservationsapp.models.generate_if_number,
                        max_length=6,
                        unique=True,
                        verbose_name="Numéro de la réservation",
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to="reservationsapp.client",
                        verbose_name="Client",
                    ),
                ),
                (
                    "journeys",
                    models.ManyToManyField(
                        related_name="reservations",
                        to="reservationsapp.journey",
                        verbose_name="Trajet",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Ticket",
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
                (
                    "if_number",
                    models.CharField(
                        default=reservationsapp.models.generate_if_number,
                        max_length=6,
                        unique=True,
                        verbose_name="Numéro du ticket",
                    ),
                ),
                (
                    "car_number",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Numéro de voiture"
                    ),
                ),
                (
                    "seat",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Numéro de place"
                    ),
                ),
                (
                    "journey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tickets",
                        to="reservationsapp.journey",
                        verbose_name="Trajet",
                    ),
                ),
                (
                    "passenger",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tickets",
                        to="reservationsapp.passager",
                        verbose_name="Passager",
                    ),
                ),
                (
                    "reservation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tickets",
                        to="reservationsapp.reservation",
                        verbose_name="Réservation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Route",
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
                (
                    "arrival_station",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="arrival_station",
                        to="reservationsapp.gare",
                    ),
                ),
                (
                    "departure_station",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="departure_station",
                        to="reservationsapp.gare",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="journey",
            name="route",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="route",
                to="reservationsapp.route",
            ),
        ),
    ]
