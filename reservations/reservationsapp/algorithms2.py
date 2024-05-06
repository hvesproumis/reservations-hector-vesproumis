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
            Initialise graph with stations, routes and weights or edges
            ->instead of passing through the routes, go by journeys given they're associated with routes
            ->start_point / end_point required for the algorithm
            ->start and end point correspond to a Station object
        """

        self.depart_date_time = depart_date_time
        self.stations = Station.objects.all()
        end_of_day = depart_date_time.replace(hour=23, minute=59, second=59, microsecond=999999)
        #filter the required journeys -> here only look till end of day
        self.journeys = Journey.objects.filter( #routes can be accessed through journey so no need to query routes
            departure_date_time__gte = depart_date_time,  #>=
            departure_date_time__lte = end_of_day #<=
        )

        self.G = nx.DiGraph()
        self.edges = defaultdict(dict) # avoids key errors #stored as dic of dics, key1 = depart, key2 = arrival, value = weight
        
        #populate the edge dictionary: contains list of tuples
        for journey in self.journeys:
            
            #check if departure and arrival in dic, if not then create dic or list
            if journey.route.departure_station not in self.edges:
                self.edges[journey.route.departure_station] = {}
            if journey.route.arrival_station not in self.edges[journey.route.departure_station]:
                self.edges[journey.route.departure_station][journey.route.arrival_station] = []
            
            #add the tuple to the list accordingly ->will have to iterate through list each time for the edges
            self.edges[journey.route.departure_station][journey.route.arrival_station].append((journey.route.distance, journey.departure_date_time, journey.arrival_date_time))
             
            self.G.add_edge(journey.route.departure_station,journey.route.arrival_station,weight=journey.route.distance, departureTime=journey.departure_date_time,arrivalTime = journey.arrival_date_time)
        #now we have self.journeys, so probs place in dictionary but careful with repeating edges at different times
        #populate the graph with edges based on distance only and then apply a time penalty
        
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
        # Get all journeys from current_station to next_station
        if current_station not in self.edges or next_station not in self.edges[current_station]:
            return float("inf")  # No valid journeys, high penalty
        
        possible_journeys = self.edges[current_station][next_station]
        min_penalty = float("inf")

        for journey in possible_journeys:
            distance, departure_datetime, arrival_time = journey

            if departure_datetime >= arrived_time:
                # Calculate the waiting time
                waiting_time = (departure_datetime - arrived_time).total_seconds() / 3600  # Convert to hours
                journey_duration = (arrival_time - departure_datetime).total_seconds() / 3600 #Converto to hours
                total_penalty = max(0, waiting_time) + journey_duration  # CHANGE THIS DEPENDING ON AVERAGE SPEED OF TRAINS

                ###########>> WILL NEED TO ENSURE ARRIVAL TIME IS IN PROPORTION TO DISTANCE IF NOT THIS DOESNT MAKE SENSE, WILL NEED TO CHANGE penaly from distance to travel time
                
                #replace penalty with correct value if non infinity
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
            # Insert at the beginning to maintain correct order (from start to end)
            path.insert(0, current_station)
            # Move to the predecessor node
            current_station = self.G.nodes[current_station]["predecessor"]

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

        # Set up the graph node attributes to default values
        for node in self.G.nodes:
            self.G.nodes[node]["distance"] = float("inf")
            self.G.nodes[node]["arrivalTime"] = datetime.min
            self.G.nodes[node]["predecessor"] = None

        # Initialize start station
        self.G.nodes[start_station]["distance"] = 0
        self.G.nodes[start_station]["arrivalTime"] = self.depart_date_time
        
        # Priority queue for A*
        priorityQueue = []
        heapq.heappush(priorityQueue, (0, start_station))

        while priorityQueue:
            _ , current_station = heapq.heappop(priorityQueue)

            if current_station == end_station:
                return self.reconstruct_path(current_station)  # Reconstructs the optimal path, probs change to include journey instead of station
            
            # Iterate over neighbors
            for neighbor in self.G.successors(current_station):
                if neighbor not in self.edges[current_station]:
                    continue  # No journeys defined for this edge, skip

                # Calculate time penalty
                penalty = self.time_penalty(current_station, neighbor, self.G.nodes[current_station]["arrivalTime"])

                # Calculate edge weight with the penalty
                edge_weight = self.G.edges[current_station, neighbor]["weight"]
                total_weight = edge_weight + penalty

                # Update the distance if this path is better
                current_distance = self.G.nodes[current_station]["distance"]
                new_distance = current_distance + total_weight

                if new_distance < self.G.nodes[neighbor]["distance"]:
                    self.G.nodes[neighbor]["distance"] = new_distance
                    self.G.nodes[neighbor]["arrivalTime"] = self.G.nodes[current_station]["arrivalTime"] + timedelta(hours=penalty)
                    self.G.nodes[neighbor]["predecessor"] = current_station

                    # Add to the priority queue with the heuristic
                    heapq.heappush(priorityQueue, (new_distance + self.heuristic(neighbor, end_station), neighbor))
        
        return None