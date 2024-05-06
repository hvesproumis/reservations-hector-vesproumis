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

from reservationsapp.models import Station, Journey, Route


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
    data =  routes + journeys
    with open('add_data.json', 'w') as f:
        json.dump(data, f, indent=4)

write_to_json()