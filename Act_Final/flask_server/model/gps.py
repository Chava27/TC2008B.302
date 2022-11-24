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
        print(self.graph)

    def valid_position(self, cell, other, cell_pos, other_pos):
        # dir_vector = (0, 1)
        # other_dir =  (0, 1)

        if cell == other and (cell != "S" or cell != "s"):
            return True
        
        if (cell == "s" or cell == "S") and (other == "s" or other == "S"): # handle s in other lanes
            return False
        
        if cell == ">" and (other == "^" or other == "v"):
            return True
        
        if cell == "v" and (other == "<" or other == ">"):
            return True

        if cell == "<" and (other == "^" or other == "v"):
            return True
        
        if cell == "^" and (other == "<" or other == ">"):
            return True

        if other == "D":
            return True

        return False

    def get_available_moves(self, pos,cell, rows):
        positions = set()
        for x in range(clamp(pos[0]-1, 0, self.width), clamp(pos[0]+1, 0, self.width)):
            for y in range(clamp(pos[1]-1, 0, self.height), clamp(pos[1] + 1, 0, self.height)):
                if x == pos[0] and y == pos[1]:
                    continue
                if self.valid_position(cell, rows[x][y], pos, [x,y]):
                    positions.add(f"({x},{y})")
        return positions

    def should_ignore(self,cell):
        if cell == "#":
            return True
                
    def populate_graph(self, rows):
        pos = [0,0]
        for row in rows:
            for cell in row:
                ##########################
                if self.should_ignore(cell):
                    pos[0] +=1
                    continue

                self.graph[f"({pos[0]},{pos[1]})"] = self.get_available_moves(pos, cell, rows)
                pos[0] +=1
            pos[1] +1

    def get_key(self, pos):
        return f"({pos[0]},{pos[1]})"

    def heuristic(self, pos, dest):
        return sum(abs(val1-val2) for val1, val2 in zip(pos,dest))

    def get_route(self,pos, dest):
        open_set = set(self.get_key(pos))
        closed_set = set()

        g = {}
        parents = {}

        g[self.get_key(pos)] = 0
        parents[self.get_key(pos)] = self.get_key(pos)


        while len(open_set) > 0:
            n = None
            for v in open_set:
                if n == None or g[self.get_key(pos)] + self.heuristic(v, dest) < g[self.get_key(pos)] + self.heuristic(n, dest):
                    n = v 
                
            if n == self.get_key(dest) or self.graph[n] == None:
                pass
            
            else:
                for (m, weight) in self.graph.get(n, None):
                    #nodes 'm' not in first and last set are added to first
                    #n is set its parent
                    if m not in open_set and m not in closed_set:
                        open_set.add(m)
                        parents[m] = n
                        g[m] = g[n] + weight
                    #for each node m,compare its distance from start i.e g(m) to the
                    #from start through n node
                    else:
                        if g[m] > g[n] + weight:
                            #update g(m)
                            g[m] = g[n] + weight
                            #change parent of m to n
                            parents[m] = n
                            #if m in closed set,remove and add to open
                            if m in closed_set:
                                closed_set.remove(m)
                                open_set.add(m)

            if n == None:
                print('Path does not exist!')
                return None

            if n == dest:
                path = []
                while parents[n] != n:
                    path.append(n)
                    n = parents[n]
                path.append(pos)
                path.reverse()
                print('Path found: {}'.format(path))
                return path
            # remove n from the open_list, and add it to closed_list
            # because all of his neighbors were inspected
            open_set.remove(n)
            closed_set.add(n)
            
        return None

