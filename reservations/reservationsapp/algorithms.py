"""
    File containing all the algorithm functions

"""
import sys
from .models import Station, Journey, Route
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import datetime

class Graph():
    """
            ->Class generates a graph object
            ->By generating multiple objects, with different weights corresponding
            To price, distance and potentially time, we can then output a range of solutions

    """
    def __init__(self, graph_edge_type,start_point,end_point,depart_date_time):
        """
            Initialise graph with stations, routes and weights or edges
            Clean all the arcs that are infeasible within the specified time window etc.
            ->instead of passing through the routes, go by journeys given they're associated with routes
            ->specify the edge type to see what weight to associate to graph
            ->start_point / end_point required for the efficient creation of a cleaner graph
            ->start and end point correspond to a Gare object
        """
        self.stations = Station.objects.all()
        self.journeys = Journey.objects.all() #route obj with times
        self.routes = Route.objects.all()
        self.G = nx.DiGraph()
        
        self.edges = defaultdict(dict) # avoids key errors #stored as dic of dics, key1 = depart, key2 = arrival, value = weight
        self.edges_times_dist = defaultdict(dict) #will be the one storing the removed infeasible arcs
        
        
        #clean this so that the dictionary containg everything is reduced and within logical context
        try:
            #adding edges depending on distance, cost etc.
            if graph_edge_type == "distance":
                #BEFORE
                for route in self.routes:
                    self.edges[route.departure_station][route.arrival_station] = route.distance
                ##################NEW###################
                #get the components of depart_date_time:
                latest_departure_date_time = datetime.datetime(depart_date_time.year,depart_date_time.month,depart_date_time.day,23,59,59,0)            
                
                start_point_arrival_times = []
                
                for journey in self.journeys:
                    #create a list containing the earliest arrival from the start node
                    #need to ensure that you are above the requested time and within 24 hours
                    if (journey.route.departure_station == start_point) and (journey.departure_date_time >= depart_date_time) and (journey.departure_date_time <= latest_departure_date_time ):
                        start_point_arrival_times.append(journey.arrival_date_time)
                
                earliest_departure = min(start_point_arrival_times)
                
                for journey in self.journeys:
                    #Here we add edges to the dictionary
                    #here apply time conditions to all non first branches
                    if journey.route.departure_station == start_point:
                        #now contains a tuple with departure and arrival times as well as the distace
                        self.edges_times_dist[journey.route.departure_station][journey.route.arrival_station] = (journey.departure_date_time,journey.arrival_date_time,journey.route.distance)
                        #start filtering based on a 24 hour time frame as well as nothing earlier than the earliest arrival from the departure station
                    else:
                        #apply a first filter so no earlier than first edge fastest completion but also not later than midnight
                        if (journey.departure_date_time >= earliest_departure) and (journey.departure_date_time <= latest_departure_date_time):
                            self.edges_times_dist[journey.route.departure_station][journey.route.arrival_station] = (journey.departure_date_time,journey.arrival_date_time,journey.route.distance)
                    
            else:       
                raise ValueError("Unsupported graph_edge_type")
        except Exception as e:
            print(f"Error occurred while initializing the graph: {e}")

    def generate_graph(self):
        """
           Implement the solver algorithms to return the best solutions
        """  
        #add nodes
        stations_list = list(self.stations)
        self.G.add_nodes_from(stations_list)
        #add edges -need to be given as a three tuple : (1,2,w)
        weighted_edges = []
        # Iterate over the outer dictionary
        for departure_station, connections in self.edges.items():
             # Iterate over the inner dictionary
            for arrival_station, weight in connections.items():
                # Create a tuple (departure, arrival, weight) and add it to the list
                edge_tuple = (departure_station, arrival_station, weight)
                weighted_edges.append(edge_tuple)

        self.G.add_weighted_edges_from(weighted_edges)
        
        return self.G
    
    def solve_graph_shortest_path(self,start_point,end_point):
        """
           Implement the solver algorithms to return the best solutions
           ->Takes start_point and end_point as parameters
           ->these must be within the database

           ->Returns a single list of nodes in a shortest path from the source to the target 
        """
        if start_point not in self.G.nodes or end_point not in self.G.nodes:
            raise ValueError("Start or end point is not in the graph.")

        return nx.shortest_path(self.G, source = start_point, target = end_point)



#If need symmetry in graph:   
#https://www.udacity.com/blog/2021/10/implementing-dijkstras-algorithm-in-python.html