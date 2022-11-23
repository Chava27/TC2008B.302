from mesa import Agent
import enum
import random
import math

class Coord:
    def __init__(self, pos) -> None:
        self.pos = pos

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
        self.explore_steps = 1
        self.state= RobotState.EXPLORE
        self.initial_vision_intensity = vision_intensity
        self.vision_intensity = vision_intensity  
        self.known_boxes = {} # (x,y) => bool
    
    @property
    def serialized(self):
        # merge with super
        return {**super().serialized, **{
            "state": self.state,
        }}

    def decrease_vision(self): 
        if (self.explore_steps % (self.initial_vision_intensity+1)) == 0 and self.vision_intensity > 1:
            self.vision_intensity -= 1
            self.explore_steps = 1

    def move_to_closest_known_box(self, known_boxes, possible_steps):
        
        closest = self.get_closest_instance(known_boxes)
        self.move_to_coord(closest, possible_steps)


    def explore(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False) # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right)
        self.update_from_near_robots(possible_steps)

        if self.pickup_closest_box(possible_steps):
            return

        known_boxes = list(map(lambda x: Coord(x[0]), list(filter(lambda picked: not picked[1], self.known_boxes.items()))))

        if (len(known_boxes) > 0):
            self.move_to_closest_known_box(known_boxes, possible_steps)
            self.steps_taken+=1
            return

        #Reduce vision intensity if the robots gets to n steps without finding any box
        self.decrease_vision()

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
        self.steps_taken+=1

 
    def move_to_closest_box(self) ->  int:
        
        #UP, DOWN, RIGHT, LEFT
        score=[self.vision_intensity for i in range(4)]
        for y in range(self.pos[1]+1, self.pos[1]+self.vision_intensity+1):
            pos = (self.pos[0],y)
            #Modificar self.model.grid_is_cell_empty(pos) <------
            if self.model.grid.is_cell_empty(pos):
                score[DirectionsEnum.UP]+=1
                continue

            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance, BoxAgent):
                self.known_boxes[instance.pos] = instance.picked

                if instance.picked: # eq to empty
                    score[DirectionsEnum.UP]+=1

                score[DirectionsEnum.UP]+= (self.vision_intensity-abs(y-self.pos[1])+1)*self.vision_intensity
                break
            break
        for y in range(self.pos[1]-1, self.pos[1]-self.vision_intensity-1,-1):
            pos = (self.pos[0],y)
            if  self.model.grid.is_cell_empty(pos):
                score[DirectionsEnum.DOWN]+=1
                continue
            
            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent):

                self.known_boxes[instance.pos] = instance.picked

                if instance.picked: # eq to empty
                    score[DirectionsEnum.DOWN]+=1

                score[DirectionsEnum.DOWN]+= (self.vision_intensity-abs(self.pos[1]-y)+1)*self.vision_intensity
                break
            break
        for x in range(self.pos[0]+1, self.pos[0]+self.vision_intensity+1):
            pos = (x,self.pos[1])
            if  self.model.grid.is_cell_empty(pos):
                score[DirectionsEnum.RIGHT]+=1
                continue

            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent):

                self.known_boxes[instance.pos] = instance.picked

                if instance.picked: # eq to empty
                    score[DirectionsEnum.RIGHT]+=1

                score[DirectionsEnum.RIGHT]+= (self.vision_intensity-abs(x-self.pos[0])+1)*self.vision_intensity
                break
            break
        for x in range(self.pos[0]-1, self.pos[0]-self.vision_intensity-1,-1):
            pos = (x,self.pos[1])
            if  self.model.grid.is_cell_empty(pos):
                score[DirectionsEnum.LEFT]+=1
                continue
            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and not instance.picked:

                self.known_boxes[instance.pos] = instance.picked

                if instance.picked: # eq to empty
                    score[DirectionsEnum.LEFT]+=1

                score[DirectionsEnum.LEFT]+= (self.vision_intensity-abs(self.pos[0]-x)+1)*self.vision_intensity
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
               
                if isinstance(instance,BoxAgent):
                    self.known_boxes[instance.pos] = instance.picked

                    if instance.picked:
                        continue

                    #Consider two agents taking the box at the same time
                    instance.picked = True
                    self.state = RobotState.DELIVER
                    self.explore_steps = 0
                    self.vision_intensity = self.initial_vision_intensity
                    self.known_boxes[instance.pos] = True
                    return True
        return False

    def get_closest_instance(self,instances):
        min_storage_distance= math.inf
        min_storage= None
        for instance in instances:
            
            distance= manhattan(instance.pos, self.pos)
            if distance < min_storage_distance:
                min_storage = instance
                min_storage_distance = distance
        if min_storage == None:
            return (0,0)
        return (min_storage.pos[0]-self.pos[0],min_storage.pos[1]-self.pos[1])

    def move_to_coord(self, coord, possible_steps):
        if abs(coord[0]) > abs(coord[1]):
            target_pos=(self.pos[0]+sign(coord[0]),self.pos[1])
            if self.model.grid.is_cell_empty(target_pos):
                self.model.grid.move_agent(self,target_pos)
                return
        target_pos=(self.pos[0],self.pos[1]+sign(coord[1]))
        if self.model.grid.is_cell_empty(target_pos):
                self.model.grid.move_agent(self,target_pos)
                return
        available_pos = list(filter(lambda x: self.model.grid.is_cell_empty(x), possible_steps))

        if len(available_pos) == 0:
            return
        
        position = random.choice(available_pos)
        self.model.grid.move_agent(self,position)
        return

    def move_to_closest_storage(self, possible_steps):
        storages=filter(lambda x: isinstance(x,StorageAgent) and not x.is_full(), self.model.schedule.agents)
        closest_storage_cords= self.get_closest_instance(storages)
        self.move_to_coord(closest_storage_cords, possible_steps)
    
    def update_map(self):
        for y in range(self.pos[1]+1, self.pos[1]+self.vision_intensity+1):
            pos = (self.pos[0],y)
            if self.model.grid.is_cell_empty(pos):
                continue

            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance, BoxAgent):
                self.known_boxes[instance.pos] = instance.picked

        for y in range(self.pos[1]-1, self.pos[1]-self.vision_intensity-1,-1):
            pos = (self.pos[0],y)
            if  self.model.grid.is_cell_empty(pos):
                continue
            
            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent):
                self.known_boxes[instance.pos] = instance.picked
            break
        for x in range(self.pos[0]+1, self.pos[0]+self.vision_intensity+1):
            pos = (x,self.pos[1])
            if  self.model.grid.is_cell_empty(pos):
                continue

            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent):
                self.known_boxes[instance.pos] = instance.picked
            break
        for x in range(self.pos[0]-1, self.pos[0]-self.vision_intensity-1,-1):
            pos = (x,self.pos[1])
            if  self.model.grid.is_cell_empty(pos):
                continue

            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent):
                self.known_boxes[instance.pos] = instance.picked
            break
    
    def update_map(self, other: "RobotAgent"):
        for (key, value) in other.known_boxes.items():
            if (self.known_boxes.get(key, False)):
                continue
                
            self.known_boxes[key] = value

    def update_from_near_robots(self, neighborhood):
        for block in neighborhood:
            if not self.model.grid.is_cell_empty(block):
                cell_container = self.model.grid.get_cell_list_contents(block)

                if isinstance(cell_container[0], RobotAgent):
                    self.update_map(cell_container[0])

    def deliver(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False) # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right)
        self.update_map()
        self.update_from_near_robots(possible_steps)

        if self.deposit_to_near_storage(possible_steps):
            return

        self.move_to_closest_storage(possible_steps)
        self.steps_taken+=1
        
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

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # self.direction = self.random.randint(0,8)
        # 
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
