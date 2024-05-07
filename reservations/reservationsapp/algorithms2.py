"""
    File containing all the algorithm functions

"""
import sys
import math
from math import sin, cos, acos, radians
from .models import Station, Journey, Route
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime, timedelta
import heapq

class Graph():
    """
        ->Contains a graph, initialised with the data base
        ->Contains methods able to route the best path using the A* search algorithm
            ->Implementing the A* greatly reduces costs despite there being a chance of not returning the best possible path
            ->This implementation works on taking into account train waiting times 


    """

    def __init__(self, start_point, end_point, depart_date_time):
        """
        Initialize the graph with stations, routes, and journey weights.
        This constructor limits the journeys to the provided day from `depart_date_time` to end of the day.

        Args:
        - start_point: Start station object (Station).
        - end_point: End station object (Station).
        - depart_date_time: Starting datetime object for the journeys (datetime).
        """
        self.depart_date_time = depart_date_time
        self.G = nx.DiGraph()
        self.edges = defaultdict(lambda: defaultdict(list))


        # Setting the end of day limit for the given date
        end_of_day = depart_date_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Fetch journeys within the date range
        self.journeys = Journey.objects.filter(
            departure_date_time__gte=depart_date_time,
            departure_date_time__lte=end_of_day
        )

        # Adding edges and the respective stations as nodes to the graph from journeys
        for journey in self.journeys:
            departure_station = journey.route.departure_station
            arrival_station = journey.route.arrival_station
            self.edges[departure_station][arrival_station].append((journey.route.distance, journey.departure_date_time, journey.arrival_date_time))
            # Add edge and ensure nodes are automatically added
            self.G.add_edge(departure_station, arrival_station,
                            weight=journey.route.distance,
                            departure_time=journey.departure_date_time,
                            arrival_time=journey.arrival_date_time)

        # Explicitly adding start and end stations as nodes may be redundant but ensure they are included
        self.G.add_node(start_point)
        self.G.add_node(end_point)



    def heuristic(self, departure_station, arrival_station):
        """
            ->Takes two Station objects as inputs :  it is designed to guide the search in the right direction
            This heuristic has to mantain admissibility: to not miss the optimum
            ->Function defining the criterion telling the algorithm what node to go for based on a cost estimation
            ->Could add a combination of the time weight too but can keep simple with distance for now
        """
        lat1 = departure_station.latitude
        long1 = departure_station.longitude
        lat2 = arrival_station.latitude
        long2 = arrival_station.longitude

        lat1_rad =  radians(lat1)
        long1_rad = radians(long1)
        lat2_rad = radians(lat2)
        long2_rad = radians(long2)

        return acos(sin(lat1_rad)*sin(lat2_rad)+cos(lat1_rad)*cos(lat2_rad)*cos(long2_rad-long1_rad))*6371
    

    def time_penalty(self, current_station, next_station, arrived_time):
        """
        Calculate a time-based penalty for transitioning from current_station to next_station.
        The penalty accounts for waiting time and journey duration.

        Args:
        - current_station: The current node/station.
        - next_station: The next node/station.
        - arrived_time: The arrival time at the current node (from the previous journey).

        Returns:
        - The minimum penalty (in hours) for the journey to the next node, considering waiting time and journey duration.
        """
        # Verify that there are journeys defined for the current to next station transition
        if current_station not in self.edges or next_station not in self.edges[current_station]:
            return float("inf")  # Return a high penalty if no valid journeys exist

        possible_journeys = self.edges[current_station][next_station]
        min_penalty = float("inf")

        # Calculate the penalty for each possible journey
        for distance, departure_datetime, arrival_time in possible_journeys:
            if departure_datetime >= arrived_time:
                waiting_time = (departure_datetime - arrived_time).total_seconds() / 3600
                journey_duration = (arrival_time - departure_datetime).total_seconds() / 3600
                total_penalty = max(0, waiting_time) + journey_duration  # Ensuring no negative penalties

                # Find the minimum penalty among all possible journeys
                min_penalty = min(min_penalty, total_penalty)

        return min_penalty


    ###########################################################################################################

    def reconstruct_path(self, end_station):
        """
        Reconstructs the optimal path from the end station to the start station,
        following the predecessor chain set during the A* search.

        Args:
        - end_station: The end station (final node in the path).

        Returns:
        - A list of station names (or objects), representing the optimal path from start to end.
        """
        path = []
        current_station = end_station
        
        # Traverse the predecessor chain to build the path from end to start
        while current_station:
            node = self.G.nodes[current_station]
            if 'predecessor' in node:
                predecessor = node['predecessor']
                journey = self.get_journey(predecessor, current_station)
                path.insert(0, {'station': current_station, 'departure': journey.departure_date_time, 
                            'arrival': journey.arrival_date_time})
        current_station = predecessor
        return path
    


    def find_optimal_path(self, start_station, end_station):
        """
        Find the optimal path between start_station and end_station using the A* algorithm.

        Args:
        - start_station: The starting station (as a Station object).
        - end_station: The ending station (as a Station object).

        Returns:
        - The optimal path as a list of station names, or None if no valid path is found.
        """
        # Check for direct routes first
        direct_journeys = Journey.objects.filter(
            route__departure_station=start_station,
            route__arrival_station=end_station
        ).order_by('departure_date_time')
        if direct_journeys.exists():
            return [{'station': j.route.departure_station.station_name, 'departure': j.departure_date_time, 
                    'arrival': j.arrival_date_time} for j in direct_journeys]

        # Setup for A* algorithm
        for node in self.G.nodes:
            self.G.nodes[node]['distance'] = float('inf')
            self.G.nodes[node]['predecessor'] = None
            self.G.nodes[node]['arrivalTime'] = datetime.min
        self.G.nodes[start_station]['distance'] = 0
        self.G.nodes[start_station]['arrivalTime'] = self.depart_date_time

        # Priority queue
        priorityQueue = [(0, start_station)]  # (cost, station)

        while priorityQueue:
            current_cost, current_station = heapq.heappop(priorityQueue)

            if current_station == end_station:
                return self.reconstruct_path(end_station)

            for neighbor in self.G.neighbors(current_station):
                penalty = self.time_penalty(current_station, neighbor, self.G.nodes[current_station]["arrivalTime"])
                edge_weight = self.G[current_station][neighbor]['weight']
                total_cost = current_cost + edge_weight + penalty

                if total_cost < self.G.nodes[neighbor]['distance']:
                    self.G.nodes[neighbor]['distance'] = total_cost
                    self.G.nodes[neighbor]['predecessor'] = current_station
                    self.G.nodes[neighbor]['arrivalTime'] = self.G.nodes[current_station]['arrivalTime'] + timedelta(hours=penalty)
                    heapq.heappush(priorityQueue, (total_cost + self.heuristic(neighbor, end_station), neighbor))

        return None  # No path found


    
    def get_journey(self, from_station, to_station):
    # Assuming journeys are directly associated with routes
        return Journey.objects.filter(
            route__departure_station=from_station, 
            route__arrival_station=to_station
        ).order_by('departure_date_time').first()
