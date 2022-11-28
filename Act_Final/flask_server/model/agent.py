from mesa import Agent
import enum
import random
import math

class CarState(enum.Enum):
    WAITING = 0
    MOVING = 1
    ARRIVED = 2

class SerializeAgent(Agent):
    @property
    def serialized(self) -> dict:
        return {
            "agent_id": str(self.unique_id),
            "agent_type": self.__class__.__name__,
            "agent_pos": {
                "x": self.pos[0],
                "y": self.pos[1]
            },
        }


class CarAgent(SerializeAgent):
    def __init__(self, unique_id, model, pos):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)

        dest = self.model.get_random_destination()
        self.destination = dest
        self.route = self.model.gps.shortest_path((pos), dest)

        self.invisible_time = 0

        # pop the first element
        if self.route is not None:
            self.route.pop(0)


        self.state = CarState.MOVING

        print("route", self.route)

    def check_lane(self, pos):
        if self.model.grid.out_of_bounds(pos):
            return False

        cell_contents = self.model.grid.get_cell_list_contents([pos])
        if len(cell_contents) == 1 and ((isinstance(cell_contents[0], StopAgent) and not cell_contents[0].active)
        or isinstance(cell_contents[0], RoadAgent)):
            return True
    
        return False

    def recall_route(self, pos):
        self.route = self.model.gps.shortest_path(pos, self.destination)
        # pop the first element
        if self.route is not None and len(self.route) > 0:
            self.route.pop(0)
        print("route", self.route)

    def reset(self):
        self.state = CarState.MOVING
        self.destination = self.model.get_random_destination()
        pos = self.model.get_random_position()
        self.route = self.model.gps.shortest_path(pos, self.destination)

        # move to random position
        self.model.grid.move_agent(self, pos)
        self.invisible_time = 5

        # pop the first element
        if self.route is not None and len(self.route) > 0:
            self.route.pop(0)
        


    def change_lane(self, next_pos):
        # check other lane if is empty
        # if empty, move to other lane

        direction_vector = (next_pos[0] - self.pos[0], next_pos[1] - self.pos[1]) # (0,1)
        
        if direction_vector == (0,1):
            # check left
            left_pos = (self.pos[0] - 1, next_pos[1])
            right_pos = (self.pos[0] + 1, next_pos[1])

            if self.check_lane(left_pos):
                self.model.grid.move_agent(self, left_pos)
                self.route.pop(0)
                # recalculate route
                self.recall_route(left_pos)
                self.state = CarState.MOVING
                return

            if self.check_lane(right_pos):
                self.model.grid.move_agent(self, right_pos)
                self.route.pop(0)
                # recalculate route
                self.recall_route(right_pos)
                self.state = CarState.MOVING
                return

        if direction_vector == (0,-1):
            # check left
            left_pos = (self.pos[0] - 1, next_pos[1])
            right_pos = (self.pos[0] + 1, next_pos[1])

            if self.check_lane(left_pos):
                self.model.grid.move_agent(self, left_pos)
                self.route.pop(0)
                # recalculate route
                self.recall_route(left_pos)
                self.state = CarState.MOVING
                return

            if self.check_lane(right_pos):
                self.model.grid.move_agent(self, right_pos)
                self.route.pop(0)
                # recalculate route
                self.recall_route(right_pos)
                self.state = CarState.MOVING
                return

        if direction_vector == (1,0):
            # check left
            left_pos = (next_pos[0], next_pos[1] + 1)
            right_pos = (next_pos[0], next_pos[1] - 1)

            if self.check_lane(left_pos):
                self.model.grid.move_agent(self, left_pos)
                self.route.pop(0)
                # recalculate route
                self.recall_route(left_pos)
                self.state = CarState.MOVING
                return

            if self.check_lane(right_pos):
                self.model.grid.move_agent(self, right_pos)
                self.route.pop(0)
                # recalculate route
                self.recall_route(right_pos)
                self.state = CarState.MOVING
                return
        
        if direction_vector == (-1,0):
            # check left
            left_pos = (next_pos[0], next_pos[1] + 1)
            right_pos = (next_pos[0], next_pos[1] - 1)

            if self.check_lane(left_pos):
                self.model.grid.move_agent(self, left_pos)
                self.route.pop(0)
                # recalculate route
                self.recall_route(left_pos)
                self.state = CarState.MOVING
                return

            if self.check_lane(right_pos):
                self.model.grid.move_agent(self, right_pos)
                self.route.pop(0)
                # recalculate route
                self.recall_route(right_pos)
                self.state = CarState.MOVING
                return

        
        pass
    
    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        
        if self.invisible_time > 0:
            self.invisible_time -= 1
            

        if self.route is None:
            return

        if self.state == CarState.ARRIVED:
            self.reset()
            return

        if self.state == CarState.WAITING:
            next_pos = self.route[0]
            
            cell_contents = self.model.grid.get_cell_list_contents([next_pos])

            if isinstance(cell_contents[0], StopAgent) and cell_contents[0].active:
                self.change_lane(next_pos)
                return

            #  check if any cell contents is a car
            for cell_content in cell_contents:
                if isinstance(cell_content, CarAgent) and cell_content.state == CarState.WAITING:
                    self.change_lane(next_pos)
                    return

            self.state = CarState.MOVING

            # pop the first element
            self.route.pop(0)
            self.model.grid.move_agent(self, next_pos)
       

        if self.state == CarState.MOVING:
            print(self.route)
            if len(self.route) == 0:
                self.state = CarState.ARRIVED
                return

            # peek next route
            next_pos = self.route[0]

            #  check if position has no car

            cell_contents = self.model.grid.get_cell_list_contents([next_pos])
            
            if len(cell_contents) != 0:
                #  check if any cell contents is a car
                for cell_content in cell_contents:
                    if isinstance(cell_content, CarAgent) and cell_content.state != CarState.ARRIVED:
                        print("moved to", next_pos)
                        self.state = CarState.WAITING
                        return

                if isinstance(cell_contents[0], StopAgent) and cell_contents[0].active:
                    print("moved to", next_pos)
                    self.state = CarState.WAITING
                    return

            next_pos = self.route.pop(0)
            self.model.grid.move_agent(self, next_pos)
            print("moved to", next_pos)

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # self.direction = self.random.randint(0,8)
        # 
        self.move()

class DestinationAgent(SerializeAgent):
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

class RoadAgent(SerializeAgent):
    def __init__(self, unique_id, model, direction):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)

        self.direction = direction
    
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

class ObstacleAgent(SerializeAgent):
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

class StopAgent(SerializeAgent):
    def __init__(self, unique_id, model, initial_state):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)

        self.active = initial_state == "s"
        self.update_time = 10
        self.time = 0

    def step(self):
        print("step", "stop agent") 
        if self.time == self.update_time:
            self.active = not self.active
            self.time = 0
        
        self.time += 1