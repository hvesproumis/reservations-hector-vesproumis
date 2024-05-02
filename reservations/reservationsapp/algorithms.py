"""
    File containing all the algorithm functions

"""
import sys
from .models import Gare, Journey, Route
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class Graph():
    """
            ->Class generates a graph object
            ->By generating multiple objects, with different weights corresponding
            To price, distance and potentially time, we can then output a range of solutions

    """
    def __init__(self, graph_edge_type):
        """
            Initialise graph with stations, routes and weights or edges
        """
        self.stations = Gare.objects.all()
        self.journeys = Journey.objects.all()
        self.routes = Route.objects.all()
        self.G = nx.DiGraph()
        self.edges = defaultdict(dict) # avoids key errors #stored as dic of dics, key1 = depart, key2 = arrival, value = weight
        try:
            #adding edges depending on distance, cost etc.
            if graph_edge_type == "distance":
                for route in self.routes:
                    self.edges[route.departure_station][route.arrival_station] = route.distance
            else:
                raise ValueError("Unsupported graph_edge_tyupe")
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