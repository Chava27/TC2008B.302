from typing import List, Tuple
from mesa import Model, agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from functools import reduce
from .agent import CarAgent, RoadAgent, ObstacleAgent, DestinationAgent, StopAgent
from .gps import GPS

from uuid import uuid4

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
            "S": lambda id, model: StopAgent(id,model, "S")
        }     

        self.should_schedule = { "s", "S" }

        rows, height, width = self.parse_map(map)
        self.width = width
        self.height = height

        print("wdith",width, "height", height)

        self.grid = MultiGrid(width-1, height-1, torus=False)

        print(rows)
        self.spawn_agents(rows)

        self.gps = GPS(rows)

    def generate_agent_id(self):
        return uuid4()

    def spawn_agent(self,cell:str, pos):
        instancer = self.cell_to_agent.get(cell, None)

        if instancer is None:
            raise Exception("Invalid character: ", cell)
        
        agent_id = self.generate_agent_id()
        agent = instancer(id=agent_id, model=self)

        print(pos)
        self.grid.place_agent(agent, (pos[0], pos[1]))

        if cell in self.should_schedule:
            self.schedule.add(agent)


    def parse_map(self, map: str) -> Tuple[List[str], int, int]:
        lines = map.split("\n")
        print(lines)

        height = len(lines)

        assert height > 0

        width = len(lines[0])

        return lines, height, width

        
    #Parsing Map
    def spawn_agents(self, rows: List[str]):
        pos = [0,0]
        for row in rows:
            for cell in row:
                self.spawn_agent(cell, pos)
                pos[0] += 1
            pos[1] += 1
                

