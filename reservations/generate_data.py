"""
This file contains a small program used to populate the database with new Routes and Journeys automatically
"""

import os
import django
import json
from datetime import datetime, timedelta
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reservations.settings")
django.setup()

from reservationsapp.models import Station, Client, Journey, Passager, generate_if_number

def generate_reservations_and_tickets():
    """
    A function that generates random reservations and tickets using existing clients and passengers in the database

    Returns:
        reservations: The created reservations
        tickets: The created tickets
    """
    reservations = []
    tickets = []
    clients = Client.objects.all()
    start_date = datetime(2024, 3, 15)
    end_date = datetime(2024, 4, 28)
    
    all_journeys = Journey.objects.all()
    clients = Client.objects.all()
    n_ticket = 1

    for i in range(1, 201): # 200 reservations
        n_journeys = random.randint(1, 4) # number of journeys in a reservation
        journeys = []
        for _ in range(n_journeys):
            a_journey = random.choice(all_journeys)
            if a_journey not in journeys:
                journeys.append(a_journey)
        
        client = random.choice(clients)
        passengers = Passager.objects.all().filter(user=client.user)

        for passenger in passengers.all():
            for journey in journeys:
                tickets.append({
                    "model": "reservationsapp.ticket",
                    "pk": n_ticket,
                    "fields": {
                        "if_number": generate_if_number(),
                        "passenger": passenger.pk,
                        "car": random.randint(1, 14),
                        "seat": random.randint(1, 120),
                        "reservation": i,
                        "journey": journey.pk
                    }
                })
                n_ticket += 1
                
        year = random.randint(start_date.year, end_date.year)
        month = random.randint(start_date.month, end_date.month)
        day = random.randint(start_date.day, end_date.day)
        reservation_time = datetime(year, month, day, 0, 0)
        reservations.append({
            "model": "reservationsapp.reservation",
            "pk": i,
            "fields": {
                "reservation_date": reservation_time.strftime("%Y-%m-%d"),
                "if_number": generate_if_number(),
                "client" : client.pk,
                "journeys": [journey.pk for journey in journeys]
            }
        })

    return reservations, tickets


def generate_routes_and_journeys():
    """
    A function that generates random routes and journeys using existing stations in the database

    Returns:
        routes: The created routes
        journeys: The created journeys
    """
    routes = []
    journeys = []
    stations = Station.objects.all()
    start_date = datetime(2024, 5, 15)
    end_date = datetime(2024, 5, 31)

    for i in range(1, 21): # 20 routes
        departure_station = random.choice(stations)
        arrival_station = random.choice(stations)
        while departure_station == arrival_station:
            arrival_station = random.choice(stations)

        routes.append({
            "model": "reservationsapp.route",
            "pk": i,
            "fields": {
                "departure_station": departure_station.id,
                "arrival_station": arrival_station.id
            }
        })

        current_date = start_date
        while current_date <= end_date:
            for _ in range(4):  # 4 departures a day
                departure_time = datetime(current_date.year, current_date.month, current_date.day, random.randint(0, 23), random.randint(0, 59))
                journeys.append({
                    "model": "reservationsapp.journey",
                    "pk": len(journeys) + 1,
                    "fields": {
                        "route": i,
                        "departure_date_time": departure_time.strftime("%Y-%m-%dT%H:%M"),
                        "arrival_date_time": (departure_time + timedelta(hours=random.randint(1, 5))).strftime("%Y-%m-%dT%H:%M")
                    }
                })
            current_date += timedelta(days=1)

    return routes, journeys

def write_to_json():
    """
    Writes routes and journeys into a json file
    """
    routes, journeys = generate_routes_and_journeys()
    reservations, tickets = generate_reservations_and_tickets()
    data =  routes + journeys + reservations + tickets
    with open('add_data.json', 'w') as f:
        json.dump(data, f, indent=4)

write_to_json()