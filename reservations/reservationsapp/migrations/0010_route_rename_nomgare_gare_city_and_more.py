# Generated by Django 4.2 on 2024-05-03 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("reservationsapp", "0009_journey_remove_reservation_car_number_and_more"),
    ]

    operations = [
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
            ],
        ),
        migrations.RenameField(
            model_name="gare",
            old_name="nomgare",
            new_name="city",
        ),
        migrations.RenameField(
            model_name="gare",
            old_name="ville",
            new_name="station_name",
        ),
        migrations.RenameField(
            model_name="reservation",
            old_name="dateresa",
            new_name="reservation_date",
        ),
        migrations.RemoveField(
            model_name="reservation",
            name="trajet",
        ),
        migrations.AddField(
            model_name="gare",
            name="latitude",
            field=models.FloatField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="gare",
            name="longitude",
            field=models.FloatField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="journey",
            name="arrival_date_time",
            field=models.DateTimeField(
                db_comment="Date et heure d'arrivée", default=None
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="journey",
            name="departure_date_time",
            field=models.DateTimeField(
                db_comment="Date et heure de départ", default=None
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="reservation",
            name="journeys",
            field=models.ManyToManyField(
                related_name="reservations",
                to="reservationsapp.journey",
                verbose_name="Trajet",
            ),
        ),
        migrations.DeleteModel(
            name="Trajet",
        ),
        migrations.AddField(
            model_name="route",
            name="arrival_station",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="arrival_station",
                to="reservationsapp.gare",
            ),
        ),
        migrations.AddField(
            model_name="route",
            name="departure_station",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="departure_station",
                to="reservationsapp.gare",
            ),
        ),
        migrations.AddField(
            model_name="journey",
            name="route",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="route",
                to="reservationsapp.route",
            ),
            preserve_default=False,
        ),
    ]