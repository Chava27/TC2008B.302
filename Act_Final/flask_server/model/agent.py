from mesa import Agent
import enum
import random
import math

class CarAgent(Agent):
    def __init__(self, unique_id, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
    
    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        pass

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # self.direction = self.random.randint(0,8)
        # 
        self.move()

class DestinationAgent(Agent):
    def __init__(self, unique_id, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
    
    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        pass

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # self.direction = self.random.randint(0,8)
        # 
        self.move()

class RoadAgent(Agent):
    def __init__(self, unique_id, model, direction):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
    
    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        pass

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # self.direction = self.random.randint(0,8)
        # 
        self.move()

class ObstacleAgent(Agent):
    def __init__(self, unique_id, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
    
    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        pass

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # self.direction = self.random.randint(0,8)
        # 
        self.move()

class StopAgent(Agent):
    def __init__(self, unique_id, model, initial_state):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
    
    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        pass

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # self.direction = self.random.randint(0,8)
        # 
        self.move()