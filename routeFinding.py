import networkx as nx
from collections import deque
import colorsys
import random

# At each intersection, should we try to go as straight as possible?
# Set to False for task 1, then switch to True for task 2.
STRAIGHTER_PATH = False

# =================================
# Workout planning with length, bearing, and elevation
# You will debug and complete our implementation, including the following features:
# 1) find any path in the UBC graph whose total distance is > target using dfs
# 2) above plus: take the "straightest" direction out of any vertex
# 3) above plus: report total elevation gain

# Helper function that determines if edge (v,w) is a valid candidate for adding to the graph
def good(gst, d, v, w, graph, goal_dist):
    return (v not in gst.adj[w]
            and graph.edges[v, w, 0]['length'] > 0
            and d + graph.edges[v, w, 0]['length'] < goal_dist)



# Helper function that returns the absolute difference between any 2 given directions.
# Note that the value should never be more than 180, since a left turn of x is
# equivalent to a right turn of (360 - x).
def get_bearing_diff(b1, b2):
    bdiff = abs(b1-b2) % 360 # allows for neg and large bearings
    return bdiff



# Main dfs function. Given a start node, goal distance, and graph of distances,
# solve these 2 related questions:
# Part 1: return a subgraph whose edges are a trail with distance at least goal_distance
# Part 2: return a subgraph with the characteristics from Part 1, but change the definition
# of "neighbors" so that at every node, the direction of the next edge is as close as possible
# to the current direction. This feature changes the order in which the neighbors are considered.
def find_route(start, goal_dist, graph):
    # distances and feasible edges will come from 'graph', solution built in 'gstate'
    gstate = nx.DiGraph()
    gstate.add_nodes_from(graph)

    # need stack of: (gstate, prev node, curr node, totlen so far, number of edges in route so far)
    # init stack & push start vertex
    stack = deque()
    stack.append((gstate, start, start, 0, 0))
    # next two lines are necessary for part 2) so that every current bearing has a previous bearing to compare against
    graph.add_edge(start, start, 0)
    graph.edges[start, start, 0]['bearing'] = random.randint(0,360) # grab a random initial direction

    while stack:
        gst, prev, curr, lensofar, clock = stack.pop()  # gst, previous node, curr node, dist so far, edges so far

        if curr not in list(gst.neighbors(prev)):
            gst.add_edge(prev, curr)
            gst.edges[prev, curr]['time'] = clock # need this for path drawing

            # stopping criteria: if we've gone far enough, return our solution graph and the number of edges
            if lensofar > goal_dist:
                return gst, clock

            if STRAIGHTER_PATH:
                # neighbors for part 2 - the "straightest" path
                neighbors = sorted(graph.neighbors(curr),
                                    key=lambda x: get_bearing_diff(graph.edges[prev, curr, 0]['bearing'],
                                                                    graph.edges[curr, x, 0]['bearing']))
            else:
                # neighbors for part 1 - just finding a path
                neighbors = graph.neighbors(curr)

            for w in neighbors:
                if good(gst, lensofar, curr, w, graph, goal_dist):
                    gstnew = gst.copy() # copy the path so we don't have to deal w backtracking. ok for small graphs.
                    stack.append((gstnew, curr, w, lensofar + graph.edges[curr, w, 0]['length'], clock + 1))

# returns the total elevation gain in gr, over the route described by rt (list of vertices).
# edges whose elevation gain is negative should be ignored.
# you can refer to a node's elevation by: gr.nodes[rt[k]]['elevation'], where k is the kth element
# of the rt list.
def total_elevation_gain(gr, rt):
    # TODO your code here
    pass


# hsv color representation gives a rainbow from red and back to red over values 0 to 1.
# this function returns the color in rgb hex, given the current and total edge numbers
def shade_given_time(k, n):
    col = colorsys.hsv_to_rgb(k / n, 1.0, 1.0)
    tup = tuple((int(x * 256) for x in col)) # why doesn't this work???
    st = f"#{tup[0]:02x}{tup[1]:02x}{tup[2]:02x}"
    return st