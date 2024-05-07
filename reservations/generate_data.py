"""
This file contains a small program used to populate the database with new Routes, Journeys,
Reservations, and Tickets automatically.
"""

import os
import django
import json
from datetime import datetime, timedelta
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reservations.settings")
django.setup()

from reservationsapp.models import Station, Client, Journey, Passager, generate_if_number

def generate_routes_and_journeys():
    """
    Generates random routes and journeys using existing stations in the database.
    """
    routes = []
    journeys = []
    stations = list(Station.objects.all())
    route_id = 40  # Starting ID for routes
    journey_id = 40  # Starting ID for journeys

    for i in range(route_id, route_id + 20):  # Generate 30 routes
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

        # Generate multiple journeys for each route
        start_date = datetime(2024, 5, 1)
        end_date = datetime(2024, 5, 31)
        current_date = start_date
        while current_date <= end_date:
            departure_time = datetime(current_date.year, current_date.month, current_date.day, 
                                      random.randint(6, 20), random.randint(0, 59))
            arrival_time = departure_time + timedelta(hours=random.randint(1, 3))
            journeys.append({
                "model": "reservationsapp.journey",
                "pk": journey_id,
                "fields": {
                    "route": i,
                    "departure_date_time": departure_time.strftime("%Y-%m-%dT%H:%M"),
                    "arrival_date_time": arrival_time.strftime("%Y-%m-%dT%H:%M")
                }
            })
            journey_id += 1
            current_date += timedelta(days=1)

    return routes, journeys

def generate_reservations_and_tickets():
    """
    Generates random reservations and tickets using existing clients and journeys.
    """
    reservations = []
    tickets = []
    all_journeys = list(Journey.objects.all())
    clients = list(Client.objects.all())
    reservation_id = 40
    ticket_id = 40

    for i in range(reservation_id, reservation_id + 100):  # Generate 200 reservations
        client = random.choice(clients)
        selected_journeys = random.sample(all_journeys, k=random.randint(1, 3))
        reservation_date = datetime(2024, 2, 1) + timedelta(days=random.randint(0, 90))

        reservations.append({
            "model": "reservationsapp.reservation",
            "pk": i,
            "fields": {
                "reservation_date": reservation_date.strftime("%Y-%m-%d"),
                "if_number": generate_if_number(),
                "client": client.id,
                "journeys": [j.id for j in selected_journeys]
            }
        })

        for journey in selected_journeys:
            passengers = Passager.objects.filter(user=client.user)
            for passenger in passengers:
                tickets.append({
                    "model": "reservationsapp.ticket",
                    "pk": ticket_id,
                    "fields": {
                        "if_number": generate_if_number(),
                        "passenger": passenger.id,
                        "car": random.randint(1, 15),
                        "seat": random.randint(1, 120),
                        "journey": journey.id,
                        "reservation": i
                    }
                })
                ticket_id += 1

    return reservations, tickets

def write_to_json():
    """
    Writes generated data into a JSON file.
    """
    routes, journeys = generate_routes_and_journeys()
    reservations, tickets = generate_reservations_and_tickets()
    data = routes + journeys + reservations + tickets
    with open('generated_data.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    write_to_json()