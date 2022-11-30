import math
from typing import List
from queue import PriorityQueue


def clamp(val, min, max):
    if val < min:
        return min
    
    if val > max: 
        return max
    
    return val

class Graph:
    def __init__(self, map: dict):
        self.map = map

        self.cache = {}

    def shortest_path(self, start, end):
        #     // Create a priority queue to store vertices that
        pq = PriorityQueue()
        distances = [math.inf] * len(self.map.keys())

        pq.put((0, start))
        distances = {start: 0}

        # check cache    
        if start in self.cache and end in self.cache[start] and len(self.cache[start][end]) != 0:
            print("Cache HIT",  self.cache[start][end])
    
            return self.cache[start][end][::]

        paths = {start: [start]}

        #      /* Looping till priority queue becomes empty (or all
        # distances are not finalized) */
        while not pq.empty():
            #     // The first vertex in pair is the minimum distance
            # // vertex, extract it from priority queue.
            # // vertex label is stored in second of pair (it
            # // has to be done this way to keep the vertices
            # // sorted distance (distance must be first item
            # // in pair)
            u = pq.get()[1] # pops
            
            # pop the vertex with the minimum distance
            for v in self.map.get(u, []):
                # // If there is shorted path to v through u.                                                                                                                    
                if distances.get(v, math.inf) > distances.get(u, math.inf)+1: # ignore weight as it is 1
                    # // Updating distance of v
                    # use cache for storing paths
                    distances[v] = distances[u] + 1
                    pq.put((distances[v], v))
                    paths[v] = paths[u] + [v]   
                
        if end not in paths:
            return None

        # update cache
        if start not in self.cache:
            self.cache[start] = {}

        for key, path in paths.items():
            if len(path) == 0 or (path[-1] != end):
                continue
            
            assert path != []
            self.cache[start][key] = path
        
        res = self.cache[start].get(end)

        if res is not None:
            return res[::]

        return None

           

class Node:
    def __init__(self) -> None:
        self.edges = []


class GPS:
    def __init__(self, rows: List[str]) -> None:
        self.height = len(rows)
        self.width = len(rows[0]) # review
        self.graph = {}

        self.populate_graph(rows)

        self.graph_class = Graph(self.graph)

    def valid_position(self, cell, other, cell_pos, other_pos):

        otherIsRight = (other == ">" or other == "s")
        otherIsLeft = (other == "<" or other == "S")
        otherIsUp = (other == "^" or other == "x")
        otherIsDown = (other == "v" or other == "X")

        cellIsRight = (cell == ">" or cell == "s")
        cellIsLeft = (cell == "<" or cell == "S")
        cellIsUp =   (cell == "^" or cell == "x")
        cellIsDown = (cell == "v" or cell == "X")

        xIsGreater = cell_pos[0] > other_pos[0]
        yIsGreater = cell_pos[1] > other_pos[1]

        xOtherIsGreater = other_pos[0] > cell_pos[0]
        yOtherIsGreater = other_pos[1] > cell_pos[1]

        yIsGreater = cell_pos[1] > other_pos[1]
        yIsGreaterOrEqual = cell_pos[1] >= other_pos[1]

        validUp = (otherIsUp and not yIsGreater)
        validDown = (otherIsDown and  yIsGreaterOrEqual)
        validLeft = (otherIsLeft and xIsGreater)
        validRight = (otherIsRight and not xIsGreater)
        
        if cellIsRight and ((validUp or validDown or otherIsRight ) and xOtherIsGreater):
            return True
        
        if cellIsDown and ((validLeft or validRight or otherIsDown) and yIsGreater):
            return True

        if cellIsLeft and ((validUp or otherIsDown or otherIsLeft) and xIsGreater): # GOOD
            return True
        
        if cellIsUp and ((validLeft or validRight or otherIsUp) and  yOtherIsGreater):
            return True

        if other == "D":
            return True

        return False

    def get_available_moves(self, pos,cell, rows):
        positions = set()
        for x in range(clamp(pos[0]-1, 0, self.width), clamp(pos[0]+2, 0, self.width)):
            for y in range(clamp(pos[1]-1, 0, self.height), clamp(pos[1] + 2, 0, self.height)):
                if x == pos[0] and y == pos[1]:
                    continue
      
                if self.valid_position(cell, rows[x][y], pos, [x,y]):
                    positions.add((x,y))
        return positions

    def should_ignore(self,cell):
        if cell == "#":
            return True
                
    def populate_graph(self, rows):
        for y in range(self.height):
            for x in range(self.width):
                cell = rows[x][y]
                if self.should_ignore(cell):
                    continue
                self.graph[(x,y)] = self.get_available_moves((x,y), cell, rows)

    def shortest_path(self, start, end):
        return self.graph_class.shortest_path(start, end)