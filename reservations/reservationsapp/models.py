from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import random

def generate_if_number():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
class Gare(models.Model):
    ville = models.CharField(max_length=200)
    nomgare = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.ville} {self.nomgare}"

class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client')
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    address = models.CharField(max_length=255, verbose_name="Adresse")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Passager(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='passagers')
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    date_of_birth = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Trajet(models.Model):
    depgare = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='depart_trajets', db_comment="Gare de départ")
    arrgare = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='arrivee_trajets', db_comment="Gare d'arrivée")
    depdh = models.DateTimeField(db_comment="Date et heure de départ",)
    arrdh = models.DateTimeField(db_comment="Date et heure d'arrivée",)
    def __str__(self):
        return f"Trajet de {self.depgare} à {self.arrgare} le {self.depdh.strftime('%Y-%m-%d %H:%M')} - Arrivée le {self.arrdh.strftime('%Y-%m-%d %H:%M')}"

class Reservation(models.Model):
    dateresa = models.DateField(auto_now_add=True, verbose_name="Date de la réservation")
    if_number = models.CharField(max_length=6, default=generate_if_number, unique=True, verbose_name="Numéro de la réservation")
    seat_number = models.IntegerField(blank=True, null=True, verbose_name="Numéro de place")
    car_number = models.IntegerField(blank=True, null=True, verbose_name="Numéro de voiture")
    trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name='reservations', verbose_name="Trajet")
    passager = models.ForeignKey(Passager, on_delete=models.PROTECT, related_name='reservations', verbose_name="Passager")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reservations', verbose_name="Client")
    
    def save(self, *args, **kwargs):
        if not self.pk:  
            self.seat_number = random.randint(1, 120)
            self.car_number = random.randint(1, 14)
        super(Reservation, self).save(*args, **kwargs)
    def __str__(self):
        return f"Réservation {self.if_number} pour {self.passager.first_name} {self.passager.last_name}"