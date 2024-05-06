# Generated by Django 4.2 on 2024-04-23 16:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("reservationsapp", "0005_client_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="passager",
            name="user",
            field=models.ForeignKey(
                default="1",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="passagers",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="client",
            name="first_name",
            field=models.CharField(max_length=100, verbose_name="Prénom"),
        ),
        migrations.AlterField(
            model_name="client",
            name="last_name",
            field=models.CharField(max_length=100, verbose_name="Nom"),
        ),
        migrations.AlterField(
            model_name="client",
            name="user",
            field=models.OneToOneField(
                default="1",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="client",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="passager",
            name="first_name",
            field=models.CharField(max_length=100, verbose_name="Prénom"),
        ),
        migrations.AlterField(
            model_name="passager",
            name="last_name",
            field=models.CharField(max_length=100, verbose_name="Nom"),
        ),
    ]