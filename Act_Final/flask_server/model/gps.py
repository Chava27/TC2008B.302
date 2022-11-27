from typing import List


def clamp(val, min, max):
    if val < min:
        return min
    
    if val > max: 
        return max
    
    return val

class Graph:
    pass

class Node:
    def __init__(self) -> None:
        self.edges = []


class GPS:
    def __init__(self, rows: List[str]) -> None:
        self.height = len(rows)
        self.width = len(rows[0]) # review
        self.graph = {}

        self.populate_graph(rows)
        print(self.get_route((0,0)))

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
        
        if cell == ">" and (other == "^" or other == "v" or (other==">" and other_pos[0]>cell_pos[0])):
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
        for x in range(clamp(pos[0]-1, 0, self.width), clamp(pos[0]+1, 0, self.width)+1):
            for y in range(clamp(pos[1]-1, 0, self.height), clamp(pos[1] + 1, 0, self.height)+1):
                if x == pos[0] and y == pos[1]:
                    continue
                if self.valid_position(cell, rows[x][y], pos, [x,y]):
                    positions.add(f"({x},{y})")
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
                self.graph[(x,y)] = self.get_available_moves((18,16), cell, rows)


    def minDistance(self, dist, sptSet):
 
        # Initialize minimum distance for next node
        min = 1e7
 
        # Search not nearest vertex not in the
        # shortest path tree
        for v in self.graph.keys():
            if dist[v] < min and sptSet[v] == False:
                min = dist[v]
                min_index = v
 
        return min_index
    
    def printSolution(self, dist):
        print("Vertex \t Distance from Source")
        for node in range(self.V):
            print(node, "\t\t", dist[node])

    def get_route(self, src):
        dist = {}
        dist[src] = 0
        sptSet = {}
 
        for cout in range(len(self.graph.keys())):
 
            # Pick the minimum distance vertex from
            # the set of vertices not yet processed.
            # u is always equal to src in first iteration
            u = self.minDistance(dist, sptSet)
 
            # Put the minimum distance vertex in the
            # shortest path tree
            sptSet[u] = True
 
            # Update dist value of the adjacent vertices
            # of the picked vertex only if the current
            # distance is greater than new distance and
            # the vertex in not in the shortest path tree
            for v in self.graph.keys():
                if ( v in self.graph[u] and
                   sptSet[v] == False and
                   dist[v] > dist[u] + 1):
                    dist[v] = dist[u] + 1
 
        self.printSolution(dist)
