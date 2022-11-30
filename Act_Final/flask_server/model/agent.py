from mesa import Agent
import enum
import random
import math

class CarState(enum.IntEnum):
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

        # Calculate the agent's initial route
        dest = self.model.get_random_destination()
        self.destination = dest

        # Cant use recall route to get the route, because the agent is not in the grid yet
        self.route = self.model.gps.shortest_path((pos), dest)

        # assert we have valid route
        assert self.route != None and len(self.route) > 0

        # we ignore the first element, since it is the current position
        self.route.pop(0)


        self.state = CarState.MOVING

    @property
    def serialized(self) -> dict:
        return {**super().serialized, **{
        "state": self.state,
    }}

    def check_lane(self, pos):
        """
        Check if the lane is empty, not out of bounds and not occupied by another car
        """
        if self.model.grid.out_of_bounds(pos):
            return False

        cell_contents = self.model.grid.get_cell_list_contents([pos])
        if len(cell_contents) == 1 and ((isinstance(cell_contents[0], StopAgent) and not cell_contents[0].active)
        or isinstance(cell_contents[0], RoadAgent)):
            return True
    
        return False

    def recall_route(self, pos):
        """
        Ask gps to return the route to the destination
        """
        self.route = self.model.gps.shortest_path(pos, self.destination)

        # Ensure that the route is not empty
        assert self.route != None and len(self.route) > 0
        self.route.pop(0)
      

    def change_lane(self, next_pos):
        """
        Change lane if possible, spaghetti code ahead
        """
        # check other lane if is empty
        # if empty, move to other lane

        direction_vector = (next_pos[0] - self.pos[0], next_pos[1] - self.pos[1]) # (0,1)
        
        if direction_vector == (0,1):
            # check left
            left_pos = (self.pos[0] - 1, next_pos[1])
            right_pos = (self.pos[0] + 1, next_pos[1])

            if self.check_lane(left_pos):
                self.model.grid.move_agent(self, left_pos)
                # recalculate route
                self.recall_route(left_pos)
                self.state = CarState.MOVING
                return

            if self.check_lane(right_pos):
                self.model.grid.move_agent(self, right_pos)
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
                # recalculate route
                self.recall_route(left_pos)
                self.state = CarState.MOVING
                return

            if self.check_lane(right_pos):
                self.model.grid.move_agent(self, right_pos)
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
                # recalculate route
                self.recall_route(left_pos)
                self.state = CarState.MOVING
                return

            if self.check_lane(right_pos):
                self.model.grid.move_agent(self, right_pos)
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
                # recalculate route
                self.recall_route(left_pos)
                self.state = CarState.MOVING
                return

            if self.check_lane(right_pos):
                self.model.grid.move_agent(self, right_pos)
                # recalculate route
                self.recall_route(right_pos)
                self.state = CarState.MOVING
                return

        
        pass
    

    def waiting(self):
        """
        Check if the car can move, if it can, move it and change state to moving
        """
        assert len(self.route) > 0
        next_pos = self.route[0]
        
        cell_contents = self.model.grid.get_cell_list_contents([next_pos])

        # if no cars
        if (isinstance(cell_contents[0], StopAgent) and not cell_contents[0].active) or (isinstance(cell_contents[0], RoadAgent) and len(cell_contents) == 1) or (DestinationAgent in [ type(x) for x in cell_contents]):
            self.state = CarState.MOVING
            self.model.grid.move_agent(self, next_pos)

            if DestinationAgent in [type(x) for x in cell_contents]:
                self.state = CarState.ARRIVED
                return

            self.route.pop(0)
            return

        if isinstance(cell_contents[0], StopAgent) and cell_contents[0].active:
            self.change_lane(next_pos)
            return

        #  check if any cell contents is a car
        for cell_content in cell_contents:
            if isinstance(cell_content, CarAgent) and cell_content.state != CarState.ARRIVED:
                self.change_lane(next_pos)
                return

    def moving(self):
        if len(self.route) == 0 and isinstance(self.model.grid.get_cell_list_contents(self.pos)[0], DestinationAgent):
            self.state = CarState.ARRIVED
            return
        print(self.route)
        assert len(self.route) > 0
        # peek next route
        next_pos = self.route[0]

        #  check if position has no car
        cell_contents = self.model.grid.get_cell_list_contents([next_pos])
        
        if len(cell_contents) != 0:
            #  check if any cell contents is a car
            for cell_content in cell_contents:
                if isinstance(cell_content, CarAgent) and cell_content.state != CarState.ARRIVED:
                    self.state = CarState.WAITING
                    return

            if isinstance(cell_contents[0], StopAgent) and cell_contents[0].active:
                self.state = CarState.WAITING
                return

        # move to next position
        next_pos = self.route.pop(0)
        self.model.grid.move_agent(self, next_pos)

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen, handles state machine
        """            
        if self.state == CarState.ARRIVED:
            self.model.delete_queue.append(self) # add to delete queue, so the model can delete it next step
            return

        if self.state == CarState.WAITING:
            self.waiting()
            return

        if self.state == CarState.MOVING:
            self.moving()
            return

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

class Direction(enum.IntEnum):
    RIGHT = 0
    LEFT = 1
    UP = 2
    DOWN = 3

class RoadAgent(SerializeAgent):
    def __init__(self, unique_id, model, direction):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)

        if (direction == ">"):
            self.n_direction = Direction.RIGHT
        elif direction == "<":
            self.n_direction = Direction.LEFT
        elif direction == "^":
            self.n_direction = Direction.UP
        else:
            self.n_direction = Direction.DOWN

        self.direction = direction

    @property
    def serialized(self) -> dict:
        return {**super().serialized, **{
            "orientation": self.n_direction,
        }}
    
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
    def __init__(self, unique_id, model, initial_state, activation_time):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)

        if (initial_state == "S"):
            self.orientation = Direction.LEFT
        elif initial_state == "s":
            self.orientation = Direction.RIGHT
        elif initial_state == "x":
            self.orientation = Direction.UP
        else:
            self.orientation = Direction.DOWN

        self.active = initial_state == "s" or initial_state == "x"
        self.update_time = activation_time
        self.time = 0

    @property
    def serialized(self) -> dict:
        return {**super().serialized, **{
            "orientation": self.orientation,
            "active": self.active
        }}

    def step(self):
        if self.time == self.update_time:
            self.active = not self.active
            self.time = 0
        
        self.time += 1