import random
from typing import List, Tuple
from mesa import Model, agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from functools import reduce
from .agent import CarAgent, RoadAgent, ObstacleAgent, DestinationAgent, StopAgent
from .gps import GPS

from uuid import uuid4

def clamp(val, min, max):
    if val < min:
        return min
    
    if val > max: 
        return max
    
    return val

class TrafficModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, map, initial_cars) -> None:
        self.initial_cars = initial_cars
        self.schedule = RandomActivation(self)
        self.running = True
        self.cell_to_agent = {
            "<": lambda id, model: RoadAgent(id,model,"<"),
            ">": lambda id, model: RoadAgent(id,model, ">"),
            "v": lambda id, model: RoadAgent(id,model, "v"),
            "^": lambda id, model: RoadAgent(id,model, "^"),
            "#": lambda id, model: ObstacleAgent(id,model),
            "D": lambda id, model: DestinationAgent(id,model),
            "s": lambda id, model: StopAgent(id,model, "s"),
            "S": lambda id, model: StopAgent(id,model, "S"),
            "x": lambda id, model: StopAgent(id,model, "x"),
            "X": lambda id, model: StopAgent(id,model, "X"),
        }     

        self.destinations = []

        self.should_schedule = { "s", "S", "x", "X" }

        rows, height, width = self.parse_map(map)
        self.width = width
        self.height = height
        self.map=[["" for i in range(self.width) ] for i in range(self.height)]
        self.rows = rows
        self.time = 0
        self.max_time = 1000

        self.grid = MultiGrid(width, height, torus=False)

        self.road_positions = []

        self.spawn_agents(rows)

        self.gps = GPS(self.map)

        # spawn car
        # sample road positions

        self.place_cars()


    def place_cars(self):
        positions = random.sample(self.road_positions, self.initial_cars)

        for coord in positions:
            agent_id = self.generate_agent_id()

            agent = CarAgent(agent_id, self, coord)

            self.schedule.add(agent)
            self.grid.place_agent(agent, coord)
        

    def generate_agent_id(self):
        return uuid4()
        
    def spawn_agent(self,cell:str, pos):
        instancer = self.cell_to_agent.get(cell, None)

        if instancer is None:
            raise Exception("Invalid character: ", cell)
        
        agent_id = self.generate_agent_id()
        agent = instancer(id=agent_id, model=self)
        self.grid.place_agent(agent, (pos[0],pos[1]))

        if cell in self.should_schedule:
            self.schedule.add(agent)

        if cell == "D":
            self.destinations.append(agent)
        
        if cell in {">", "<", "v", "^"}:
            self.road_positions.append(pos)
        
    def get_random_position(self):
        positions = random.sample(self.road_positions, 1)
        return positions[0]

    def get_random_destination(self):
        return random.choice(self.destinations).pos

    def parse_map(self, map: str) -> Tuple[List[str], int, int]:
        lines = map.split("\n")

        height = len(lines)

        assert height > 0

        width = len(lines[0])

        return lines, height, width

        
    #Parsing Map
    def spawn_agents(self, rows: List[str]):
        for y in range(self.height):
            for x in range(self.width):
                self.spawn_agent(rows[y][x], (x,self.height-1-y))
                self.map[x][self.height-1-y] = rows[y][x]

    def step(self):
        '''Advance the model by one step.'''
        if not self.running:
            return

        self.schedule.step()
        self.time +=1
        if self.time == self.max_time:
            self.running = False

