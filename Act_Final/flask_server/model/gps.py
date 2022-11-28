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
        if start in self.cache and end in self.cache[start]:
            return self.cache[start][end]

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
                
   
        # update cache
        if start not in self.cache:
            self.cache[start] = {}

            for key, path in paths.items():
                self.cache[start][key] = path
        
        if end not in self.cache[start]:
            return None

        return self.cache[start][end]

           

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
        if ((cell == "S" or cell=="s") and (other== ">" and other_pos[0]> cell_pos[0])):
            return True
        
        if ((cell == "S" or cell=="s") and (other== "v" and other_pos[1]< cell_pos[1])):
            return True

        if ((cell == "S" or cell=="s") and (other== "<" and other_pos[0]< cell_pos[0])):
            return True

        if ((cell == "S" or cell=="s") and (other== "^" and other_pos[1]> cell_pos[1])):
            return True

        if (abs(cell_pos[0] - other_pos[0]) > 0) and (abs(cell_pos[1] - other_pos[1]) > 0) and cell != other:
            return False
        
        if other == "s" or other == "S":
            return True
        
        if cell == ">" and ((other == "^" and cell_pos[1] < other_pos[1]) or other == "v" or (other==">" and other_pos[0]>cell_pos[0])):
            return True
        
        if cell == "v" and (other == "<" or other == ">" or (other=="v" and cell_pos[1]> other_pos[1])):
            return True

        if cell == "<" and (other == "^" or other == "v" or (cell_pos[0]>other_pos[0])):
            return True
        
        if cell == "^" and (other == "<" or other == ">" or (other=="^" and other_pos[1]>cell_pos[1])):
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