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


class Journey(models.Model):
    ...

class Reservation(models.Model):
    dateresa = models.DateField(auto_now_add=True, verbose_name="Date de la réservation")
    if_number = models.CharField(max_length=6, default=generate_if_number, unique=True, verbose_name="Numéro de la réservation")
    trajet = models.ManyToManyField(Trajet, related_name='reservations', verbose_name="Trajet")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reservations', verbose_name="Client")
    
    def __str__(self):
        return f"Réservation {self.if_number} pour {self.client.user.first_name} {self.client.user.last_name}"


class Ticket(models.Model):
    """
    A model to link a passenger to a specific journey, in a specific reservation.

    Fields:
        if_number (Char): An id of the ticket
        passenger (Passager) : The passenger on the ticket
        car_number (Integer) : The train car the passenger is in
        seat (Integer) : The seat the passenger is in
        journey (Journey) : The journey the passenger travels
        reservation (Reservation) : The reservation that generated the ticket        
    """
    if_number = models.CharField(max_length=6, default=generate_if_number, unique=True, verbose_name="Numéro du ticket")
    passenger = models.ForeignKey(Passager, on_delete=models.PROTECT, related_name='tickets', verbose_name="Passager")
    car_number = models.IntegerField(blank=True, null=True, verbose_name="Numéro de voiture")
    seat = models.IntegerField(blank=True, null=True, verbose_name="Numéro de place")
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name='tickets', verbose_name="Trajet")
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='tickets', verbose_name="Réservation")
    
    def save(self, *args, **kwargs):
        if not self.pk:  
            self.seat_number = random.randint(1, 120)
            self.car_number = random.randint(1, 14)
        super(Ticket, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Billet {self.if_number} pour {self.passenger.first_name} {self.passenger.last_name}"