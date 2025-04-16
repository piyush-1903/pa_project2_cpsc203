import networkx as nx
from collections import deque
import colorsys
import random

# At each intersection, should we try to go as straight as possible?
# Set to False for task 1, then switch to True for task 2.
STRAIGHTER_PATH = True

# =================================
# Workout planning with length, bearing, and elevation
# You will debug and complete our implementation, including the following features:
# 1) find any path in the UBC graph whose total distance is > target using DFS
# 2) above plus: take the "straightest" direction out of any vertex
# 3) above plus: report total elevation gain

# Helper function that determines if edge (v, w) is a valid candidate for adding to the graph.
def good(gst, d, v, w, graph, goal_dist):
    return (
        not gst.has_edge(v, w)               # Ensure the edge from v to w isn't already in gst.
        and not gst.has_edge(w, v)              # Check for a backedge. 
        and graph.edges[v, w, 0]['length'] > 0 # Edge length must be positive.
        and d + graph.edges[v, w, 0]['length'] <= goal_dist * 1.1  # Do not exceed 110%.
    )


# Helper function that returns the absolute difference between any 2 given directions.
# Ensures the result is never more than 180.
def get_bearing_diff(b1, b2):
    diff = abs(b1 - b2) % 360
    if diff > 180:
        diff = 360 - diff
    return diff

# Main DFS function.
# Given a start node, goal distance, and a graph of distances,
# this function returns a subgraph whose edges form a trail with total distance 
# between goal_dist and goal_dist * 1.1.
def find_route(start, goal_dist, graph):
    # 'gstate' will hold our solution subgraph.
    gstate = nx.DiGraph()
    gstate.add_nodes_from(graph)

    # Stack elements: (gstate, previous node, current node, total length so far, number of edges so far)
    stack = deque()
    stack.append((gstate, start, start, 0, 0))
    
    # Initialize the "previous bearing" at the start node.
    graph.add_edge(start, start, 0)
    graph.edges[start, start, 0]['bearing'] = random.randint(0, 360)  # random initial direction

    while stack:
        gst, prev, curr, lensofar, clock = stack.pop()  # current DFS state

        if curr not in list(gst.neighbors(prev)):
            gst.add_edge(prev, curr)
            gst.edges[prev, curr]['time'] = clock  # for route drawing

            # Check if the current route is within the acceptable length range.
            if goal_dist <= lensofar <= goal_dist * 1.1:
                return gst, clock

            if STRAIGHTER_PATH:
                # For the "straightest" path, sort neighbors by how close their bearing is to current direction.
                neighbors = sorted(
                    graph.neighbors(curr),
                    key=lambda x: get_bearing_diff(
                        graph.edges[prev, curr, 0]['bearing'],
                        graph.edges[curr, x, 0]['bearing']
                    )
                )
            else:
                # Otherwise, consider all neighbors in arbitrary order.
                neighbors = graph.neighbors(curr)

            for w in neighbors:
                if good(gst, lensofar, curr, w, graph, goal_dist):
                    gstnew = gst.copy()  # make a copy for the new branch
                    new_length = lensofar + graph.edges[curr, w, 0]['length']
                    stack.append((gstnew, curr, w, new_length, clock + 1))

# Returns the total elevation gain over the route described by the list of vertices `rt`.
# Only positive differences (uphill segments) are accumulated.
def total_elevation_gain(gr, rt):
    gain = 0
    for i in range(1, len(rt)):
        diff = gr.nodes[rt[i]]['elevation'] - gr.nodes[rt[i-1]]['elevation']
        if diff > 0:
            gain += diff
    return gain

# hsv color representation gives a rainbow from red and back to red over values 0 to 1.
# This function returns the corresponding RGB hex code, given the current and total edge numbers.
def shade_given_time(k, n):
    col = colorsys.hsv_to_rgb(k / n, 1.0, 1.0)
    # Multiply by 255 (not 256) so the maximum value is 255.
    tup = tuple(int(x * 255) for x in col)
    st = f"#{tup[0]:02x}{tup[1]:02x}{tup[2]:02x}"
    return st
