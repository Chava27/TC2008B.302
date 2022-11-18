from mesa import Model, agent
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector
from .agent import RobotAgent, ObstacleAgent, BoxAgent, StorageAgent

class RandomModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, num_robots, num_boxes, max_time, width, height, vision_intensity, num_storage):
        self.max_time=max_time
        self.time = 0
        self.num_agents = num_robots
        self.num_box= num_boxes
        self.grid = Grid(width,height,torus = False) 
        self.schedule = RandomActivation(self)
        self.running = True 
        self.num_storage = num_storage


        self.datacollector = DataCollector( 
        agent_reporters={
            "Steps": lambda a: a.steps_taken if isinstance(a, RobotAgent) else 0
            }
        )

        # Creates the border of the grid
        border = [(x,y) for y in range(height) for x in range(width) if y in [0, height-1] or x in [0, width - 1]]

        for i,pos in enumerate(border):
            obs = ObstacleAgent(i, self)
            self.grid.place_agent(obs, pos)

        for i in range(self.num_storage):
            a = StorageAgent(i+1000,self)
            cord = self.grid.find_empty()
            self.grid.place_agent(a, cord)
            self.schedule.add(a)
        
        # Add the agent to a random empty grid cell
        for i in range(self.num_agents):
            a = RobotAgent(i+2000, self, vision_intensity) 
            cord = self.grid.find_empty()
            self.grid.place_agent(a, cord)
            self.schedule.add(a)
        
        # Add the trash to a random empty grid cell
        for i in range(self.num_box):
            a= BoxAgent(i+3000, self)
            cord = self.grid.find_empty()
            #Define possible position of box, not counting the borders
            self.grid.place_agent(a, cord)
           
        self.datacollector.collect(self) #collect the data from the steps  

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.datacollector.collect(self)
        self.time +=1
        if self.time == self.max_time - 1:
            self.running = False