from mesa import Agent
import enum
import random
import math

def sign(num):
    if num == 0:
        return 0
    return num//abs(num)

def manhattan(a, b):
    return sum(abs(val1-val2) for val1, val2 in zip(a,b))

class RobotState(enum.IntEnum):
    EXPLORE = 0
    DELIVER = 1

class DirectionsEnum(enum.IntEnum):
    UP=0
    DOWN=1
    RIGHT=2
    LEFT=3
    CENTER=4


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


class RobotAgent(SerializeAgent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model, vision_intensity):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.steps_taken = 0
        self.explore_steps = 0
        self.state= RobotState.EXPLORE
        self.initial_vision_intensity = vision_intensity
        self.vision_intensity = vision_intensity  
    
    @property
    def serialized(self):
        # merge with super
        return {**super().serialized, **{
            "state": self.state,
        }}

    def explore(self):
        #Reduce vision intensity if the robots gets to n steps without finding any box
        if self.explore_steps%50 == 0 and self.vision_intensity>1:
            self.vision_intensity -=1
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False) # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right)
        if self.pickup_closest_box(possible_steps):
            return
        direction= self.move_to_closest_box()
        if direction == DirectionsEnum.UP:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1]+1))
        elif direction == DirectionsEnum.DOWN:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1]-1))
        elif direction == DirectionsEnum.RIGHT:
            self.model.grid.move_agent(self, (self.pos[0]+1, self.pos[1]))
        elif direction == DirectionsEnum.LEFT:
            self.model.grid.move_agent(self, (self.pos[0]-1, self.pos[1]))
        self.explore_steps += 1

    def move_to_closest_box(self) ->  int:
    
        #UP, DOWN, RIGHT, LEFT
        score=[self.vision_intensity for i in range(4)]
        for y in range(self.pos[1]+1, self.pos[1]+self.vision_intensity+1):
            pos = (self.pos[0],y)
            if self.model.grid.is_cell_empty(pos):
                score[DirectionsEnum.UP]+=1
                continue

            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and not instance.picked:
                score[DirectionsEnum.UP]+= (y-self.pos[1]+1)*2
                break
            break
        for y in range(self.pos[1]-1, self.pos[1]-self.vision_intensity-1,-1):
            pos = (self.pos[0],y)
            if self.model.grid.is_cell_empty(pos):
                score[DirectionsEnum.DOWN]+=1
                continue
            
            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and not instance.picked:
                score[DirectionsEnum.DOWN]+= (self.pos[1]-y+1)*2
                break
            break
        for x in range(self.pos[0]+1, self.pos[0]+self.vision_intensity+1):
            pos = (x,self.pos[1])
            if self.model.grid.is_cell_empty(pos):
                score[DirectionsEnum.RIGHT]+=1
                continue

            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and not instance.picked:
                score[DirectionsEnum.RIGHT]+= (x-self.pos[0]+1)*2
                break
            break
        for x in range(self.pos[0]-1, self.pos[0]-self.vision_intensity-1,-1):
            pos = (x,self.pos[1])
            if self.model.grid.is_cell_empty(pos):
                score[DirectionsEnum.LEFT]+=1
                continue
            
            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and not instance.picked:
                score[DirectionsEnum.LEFT]+= (self.pos[0]-x+1)*2
                break
            break
        scores= list(filter(lambda x: x!=0, score)) 
        if len(scores)==0:
            return DirectionsEnum.CENTER
        direction = random.choice([i for i, x in enumerate(score) if x == max(score)])
        return direction
                   
    def pickup_closest_box(self,possible_steps) -> bool:
        for step in possible_steps:
            cell_container= self.model.grid.get_cell_list_contents(step)
            if not self.model.grid.is_cell_empty(step):
                instance = cell_container[0]
                if isinstance(instance,BoxAgent) and not instance.picked:
                    #Consider two agents taking the box at the same time
                    instance.picked = True
                    self.state = RobotState.DELIVER
                    self.explore_steps=0
                    self.vision_intensity = self.initial_vision_intensity
                    return True
        return False

    def get_closest_storage(self,storages):
        min_storage_distance= math.inf
        min_storage= None
        for storage in storages:
            distance= manhattan(storage.pos, self.pos)
            if distance < min_storage_distance:
                min_storage = storage
                min_storage_distance = distance
        if min_storage == None:
            return (0,0)
        return (min_storage.pos[0]-self.pos[0],min_storage.pos[1]-self.pos[1])



    def move_to_closest_storage(self, possible_steps):
        storages=filter(lambda x: isinstance(x,StorageAgent) and not x.is_full(), self.model.schedule.agents)

        closest_storage_cords= self.get_closest_storage(storages)
        if abs(closest_storage_cords[0]) > abs(closest_storage_cords[1]):
            target_pos=(self.pos[0]+sign(closest_storage_cords[0]),self.pos[1])
            if self.model.grid.is_cell_empty(target_pos):
                self.model.grid.move_agent(self,target_pos)
                return
        target_pos=(self.pos[0],self.pos[1]+sign(closest_storage_cords[1]))
        if self.model.grid.is_cell_empty(target_pos):
                self.model.grid.move_agent(self,target_pos)
                return
        available_pos = list(filter(lambda x: self.model.grid.is_cell_empty(x), possible_steps))

        if len(available_pos) == 0:
            return
        
        position = random.choice(available_pos)
        self.model.grid.move_agent(self,position)
        return
        

    def deliver(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False) # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right)
        if self.deposit_to_near_storage(possible_steps):
            return
        self.move_to_closest_storage(possible_steps)
        
        
        
    def deposit_to_near_storage(self,possible_steps):
        for step in possible_steps:
            cell_container= self.model.grid.get_cell_list_contents(step)
            if not self.model.grid.is_cell_empty(step):
                if isinstance(cell_container[0],StorageAgent):
                    #Consider two agents taking the box at the same time
                    try:
                        cell_container[0].add_box()
                        self.state = RobotState.EXPLORE
                        self.explore_steps = 0
                        self.vision_intensity = self.initial_vision_intensity
                        return True
                    except:
                        #Should not get here
                        continue
                    
        return False
        

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        if self.state == RobotState.EXPLORE:
            self.explore()

        elif self.state == RobotState.DELIVER:
            self.deliver()

        self.steps_taken+=1

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # self.direction = self.random.randint(0,8)
        # print(f"Agente: {self.unique_id} movimiento {self.direction}")
        self.move()

class BoxAgent(SerializeAgent):
    """
    Trash agent. Must be eliminated when interaction with Random Agent.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        self.picked = False

    def step(self):
        pass  
    
    @property
    def serialized(self):
        # merge with super
        return {**super().serialized, **{
            "picked": self.picked,
        }}

class StorageAgent(SerializeAgent):
    """
    Trash agent. Must be eliminated when interaction with Random Agent.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.box_count=0
        self.box_limit=5

    @property
    def serialized(self):
        # merge with super
        return {**super().serialized, **{
            "box_count": self.box_count,
        }}

    def add_box(self):
        if not self.is_full():
            self.box_count+=1
            return
        raise Exception("Reached Maximum Boxes")

    def is_full(self) -> bool:
        return self.box_count >= self.box_limit

    def step(self):
        pass  



class ObstacleAgent(SerializeAgent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass  
