"""
This file contains all the models used in the application

Models :
    Station
    Route
    Journey
    Reservation
    Ticket
    Passenger
    Client
"""

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import random
from math import sin, cos, acos, radians

def generate_if_number():
    """
    A function used to generate random reservation and ticket numbers

    Returns:
        string: A string of random letters and numbers
    """
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Station(models.Model):
    """
    A model representing a station with its coordinates
    
    Fields:
        city (Char): The name of the city where the station is
        station_name (Char): The name of the station
        longitude (Float): Longitude of the station in degrees
        latitude (Float): Latitude of the station in degrees
    """

    city = models.CharField(max_length=200)
    station_name = models.CharField(max_length=200, null=True, blank=True)
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
    """
    A model of a passenger, attributed to a client account.

    Fields:
        user (User): The user the passenger is attributed to
        first_name (Char): The passenger's first name
        last_name (Char): The passenger's last name
        date_of_birth (Date): The passenger's birth date
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='passagers')
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    date_of_birth = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Route(models.Model):
    """
    A model that represents a route operated by the company
    
    Fields:
        departure_station (Station): The departure station
        arrival_station (Station): The arrival station
    Attributes:
        distance (float): contains the distance between the stations in km
    """
    departure_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='departure_station')
    arrival_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='arrival_station')
    
    def get_distance(self):
        """
        A function to compute the distance bewteen the departure and arrival stations, as the crow flies.
        Latitudes are assumed in degrees so they are changed to rads.

        Returns:
            float: The distance in km
        """
        lat1 = self.departure_station.latitude
        long1 = self.departure_station.longitude
        lat2 = self.arrival_station.latitude
        long2 = self.arrival_station.longitude

        lat1_rad =  radians(lat1)
        long1_rad = radians(long1)
        lat2_rad = radians(lat2)
        long2_rad = radians(long2)

        return acos(sin(lat1_rad)*sin(lat2_rad)+cos(lat1_rad)*cos(lat2_rad)*cos(long2_rad-long1_rad))*6371
    
    # Variable to store the distance between the stations
    distance = property(get_distance)
    
    def __str__(self):
        return f"{self.departure_station} - {self.arrival_station}"

class Journey(models.Model):
    """
    A model that represent a journey made on a route, at a sepcififc date and time
    
    Fields:
        route (Route): A route offered by the company
        departure_date_time (DateTime): The departure time and date
        arrival_date_time (DateTime): The arrival time and date

    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE,related_name='route')
    departure_date_time = models.DateTimeField(help_text="Date et heure de départ",)
    arrival_date_time = models.DateTimeField(help_text="Date et heure d'arrivée",)
    
    def __str__(self):
        return f"Trajet de {self.route.departure_station} à {self.route.arrival_station} le {self.departure_date_time.strftime('%Y-%m-%d %H:%M')} - Arrivée le {self.arrival_date_time.strftime('%Y-%m-%d %H:%M')}"


class Reservation(models.Model):
    """
    A model representing a reservation made by a client for multiple journeys.

    Fields:
        reservation_date (Date): The date when the reservation was made
        if_number (Char): The id of the reservation
        journeys (Journey): The journeys booked
        client (Client): The client that made the reservation      
    """
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
        passenger (Passenger): The passenger on the ticket
        car (Integer): The train car the passenger is in
        seat (Integer): The seat the passenger is in
        journey (Journey): The journey the passenger travels
        reservation (Reservation): The reservation that generated the ticket        
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