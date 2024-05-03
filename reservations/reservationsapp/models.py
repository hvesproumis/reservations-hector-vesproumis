from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import random
from math import sin, cos, acos, radians
def generate_if_number():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Gare(models.Model):
    """
    city: charField storing the name of the city [prev: ville] 
    station_name: charField with name of station [nomGare]
    longitude: Float in degrees
    latitude: FLoat in degrees

    """

    city = models.CharField(max_length=200)
    station_name = models.CharField(max_length=200)
    longitude = models.FloatField(max_length=10,null = True, blank=True)
    latitude = models.FloatField(max_length=10,null = True, blank=True)
    def __str__(self):
        return f"{self.city} {self.station_name}"

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


class Route(models.Model):
    """
    departure_station: gets the departure station from the Gare model
    arrival_station: gets the arrival station from ''
    distance: contains the distance between the stations in km 
        with the distance computed as the crow flies
    get_distance: function computing the 
        distance using longitudes and lat.. of the stations
        we take the two point and use the formula:
        =acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*6371
    ->latitudes are assumed in degrees so change to rads
    """
    departure_station = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='departure_station')
    arrival_station = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='arrival_station')
    def get_distance(self):
        lat1 = self.departure_station.latitude()
        long1 = self.departure_station.longitude()
        lat2 = self.arrival_station.latitude()
        long2 = self.arrival_station.longitude()

        lat1_rad =  radians(lat1)
        long1_rad = radians(long1)
        lat2_rad = radians(lat2)
        long2_rad = radians(long2)

        return acos(sin(lat1_rad)*sin(lat2_rad)+cos(lat1_rad)*cos(lat2_rad)*cos(long2_rad-long1_rad))*6371
    distance = property(get_distance)
    
    def __str__(self):
        return f"{self.departure_station} - {self.arrival_station}"

class Journey(models.Model):
    """
    route: stores the corresponding route 1to1 relation
    departure_DateTime: stores the departure time and date
    arrival_DateTime: '' for arrival

    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE,related_name='route')
    departure_date_time = models.DateTimeField(db_comment="Date et heure de départ",)
    arrival_date_time = models.DateTimeField(db_comment="Date et heure d'arrivée",)
    def __str__(self):
        return f"Trajet de {self.route.departure_station} à {self.route.arrival_station} le {self.departure_date_time.strftime('%Y-%m-%d %H:%M')} - Arrivée le {self.arrival_date_time.strftime('%Y-%m-%d %H:%M')}"



class Reservation(models.Model):
    reservation_date = models.DateField(auto_now_add=True, verbose_name="Date de la réservation")
    if_number = models.CharField(max_length=6, default=generate_if_number, unique=True, verbose_name="Numéro de la réservation")
    journeys = models.ManyToManyField(Journey, related_name='reservations', verbose_name="Trajet")
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
    car = models.IntegerField(blank=True, null=True, verbose_name="Numéro de voiture")
    seat = models.IntegerField(blank=True, null=True, verbose_name="Numéro de place")
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name='tickets', verbose_name="Trajet")
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='tickets', verbose_name="Réservation")
    
    def save(self, *args, **kwargs):
        if not self.pk:  
            self.seat = random.randint(1, 120)
            self.car = random.randint(1, 14)
        super(Ticket, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Billet {self.if_number} pour {self.passenger.first_name} {self.passenger.last_name}"