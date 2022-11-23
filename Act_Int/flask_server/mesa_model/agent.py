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
        #[[Empty pos], [Invalid BOX Pos] [box pos]]  
        self.map = [set(),set(),set()]
    
    @property
    def serialized(self):
        # merge with super
        return {**super().serialized, **{
            "state": self.state,
        }}

    def explore(self):
        #Reduce vision intensity if the robots gets to n steps without finding any box
        #if self.explore_steps%(self.initial_vision_intensity*2) == 0 and self.vision_intensity>1:
            #self.vision_intensity -=1
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False) # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right)
        if self.inspect_steps(possible_steps):
            return
        #if len(self.map[2])>0:
            #print("Box List:", self.map[2])
            #print("Moving to Known Box")
            #no tiene sentido guardar en variable no retorna nada  <-----
            #self.move_to_closest_known_box(possible_steps)
            #return
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

    #no falta ignorar los boxes invalidados??? <----- CHECK
    def move_to_closest_box(self) ->  int:
        print("Vision Intensity",self.vision_intensity)
        #UP, DOWN, RIGHT, LEFT
        score=[self.vision_intensity for i in range(4)]
        for y in range(self.pos[1]+1, self.pos[1]+self.vision_intensity+1):
            pos = (self.pos[0],y)
            #Modificar self.model.grid_is_cell_empty(pos) <------
            if self.is_empty(pos):
                score[DirectionsEnum.UP]+=1
                continue
            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and instance.picked:
                self.map[1].add(instance.pos)
                self.map[2] = self.map[2].difference(self.map[1])
                score[DirectionsEnum.UP]+=1
            if isinstance(instance,BoxAgent) and not instance.picked:
                score[DirectionsEnum.UP]+= (self.vision_intensity-abs(y-self.pos[1])+1)*self.vision_intensity
                break
            break
        for y in range(self.pos[1]-1, self.pos[1]-self.vision_intensity-1,-1):
            pos = (self.pos[0],y)
            if self.is_empty(pos):
                score[DirectionsEnum.DOWN]+=1
                continue
            
            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and instance.picked:
                self.map[1].add(instance.pos)
                self.map[2] = self.map[2].difference(self.map[1])
                score[DirectionsEnum.DOWN]+=1
            if isinstance(instance,BoxAgent) and not instance.picked:
                score[DirectionsEnum.DOWN]+= (self.vision_intensity-abs(y-self.pos[1])+1)*self.vision_intensity
                break
            break
        for x in range(self.pos[0]+1, self.pos[0]+self.vision_intensity+1):
            pos = (x,self.pos[1])
            if self.is_empty(pos):
                score[DirectionsEnum.RIGHT]+=1
                continue

            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and instance.picked:
                self.map[1].add(instance.pos)
                self.map[2] = self.map[2].difference(self.map[1])
                score[DirectionsEnum.RIGHT]+=1
            if isinstance(instance,BoxAgent) and not instance.picked:
                score[DirectionsEnum.RIGHT]+= (self.vision_intensity-abs(y-self.pos[1])+1)*self.vision_intensity
                break
            break
        for x in range(self.pos[0]-1, self.pos[0]-self.vision_intensity-1,-1):
            pos = (x,self.pos[1])
            if self.is_empty(pos):
                score[DirectionsEnum.LEFT]+=1
                continue
            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and instance.picked:
                self.map[1].add(instance.pos)
                self.map[2] = self.map[2].difference(self.map[1])
                score[DirectionsEnum.LEFT]+=1
            if isinstance(instance,BoxAgent) and not instance.picked:
                score[DirectionsEnum.LEFT]+= (self.vision_intensity-abs(y-self.pos[1])+1)*self.vision_intensity
                break
            break
        scores= list(filter(lambda x: x!=0, score)) 
        print("Scores:",scores)
        if len(scores)==0:
            return DirectionsEnum.CENTER
        direction = random.choice([i for i, x in enumerate(score) if x == max(score)])
        print("Direction:",direction)
        return direction
                   
    def inspect_steps(self,possible_steps) -> bool:
        for step in possible_steps:
            cell_container= self.model.grid.get_cell_list_contents(step)
            if not self.model.grid.is_cell_empty(step):
                instance = cell_container[0]
                if isinstance(instance,BoxAgent) and not instance.picked:
                    #Consider two agents taking the box at the same time
                    instance.picked = True
                    self.state = RobotState.DELIVER
                    #Store Box Postion to invalid
                    self.map[1].add(step)
                    self.map[2] = self.map[2].difference(self.map[1])
                    self.explore_steps=1
                    self.vision_intensity = self.initial_vision_intensity
                    return True
                #if the box is already picked, add coor to invalid coord
                if isinstance(instance,BoxAgent) and instance.picked:
                    self.map[1].add(step)
                    self.map[2] = self.map[2].difference(self.map[1])
                    continue
                #if robots get to know each other. Share Map
                if isinstance(instance,RobotAgent):
                    self.map=self.share_map(instance)
                    continue
        #????  <----- 
        if not self.model.grid.is_cell_empty(self.pos):
            cell_container= self.model.grid.get_cell_list_contents(self.pos)
            instance= cell_container[0]
            if isinstance(instance,BoxAgent) and instance.picked:
                self.map[1].add(step)
                self.map[2] = self.map[2].difference(self.map[1])
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

    def get_closest_box(self):
        min_box_distance = math.inf
        min_box = None
        for box in self.map[2]:
            distance = manhattan(box, self.pos)
            if distance < min_box_distance:
                min_box = box
                min_box_distance = distance
        if min_box == None:
            return(0,0)
        return (min_box[0]-self.pos[0], min_box[1] - self.pos[1])
        

    def move_to_closest_storage(self, possible_steps):
        storages=filter(lambda x: isinstance(x,StorageAgent) and not x.is_full(), self.model.schedule.agents)
        closest_storage_cords= self.get_closest_storage(storages)
        if abs(closest_storage_cords[0]) > abs(closest_storage_cords[1]):
            target_pos=(self.pos[0]+sign(closest_storage_cords[0]),self.pos[1])
            if self.is_empty(target_pos):
                self.model.grid.move_agent(self,target_pos)
                return
        target_pos=(self.pos[0],self.pos[1]+sign(closest_storage_cords[1]))
        if self.is_empty(target_pos):
                self.model.grid.move_agent(self,target_pos)
                return
        available_pos = list(filter(lambda x: self.is_empty(x), possible_steps))

        if len(available_pos) == 0:
            return
        
        position = random.choice(available_pos)
        self.model.grid.move_agent(self,position)
        return

    def is_empty(self,coord):
        cell_container= self.model.grid.get_cell_list_contents(coord)
        return self.model.grid.is_cell_empty(coord) or (isinstance(cell_container[0],BoxAgent) and (coord not in self.map[1]))
    
    #Implement Priority Que that upates distances each steps
    def move_to_closest_known_box(self, possible_steps):
        closest_box_cords= self.get_closest_box()
        if abs(closest_box_cords[0]) > abs(closest_box_cords[1]):
            target_pos=(self.pos[0]+sign(closest_box_cords[0]),self.pos[1])
            if self.is_empty(target_pos):
                self.model.grid.move_agent(self,target_pos)
                return
        target_pos=(self.pos[0],self.pos[1]+sign(closest_box_cords[1]))
        if self.is_empty(target_pos):
                self.model.grid.move_agent(self,target_pos)
                return
        available_pos = list(filter(lambda x: self.is_empty(x), possible_steps))

        if len(available_pos) == 0:
            return
        
        position = random.choice(available_pos)
        self.model.grid.move_agent(self,position)
        return

    def share_map(self, robot_agent):
        empty_coords = self.map[0].union(robot_agent.map[0])
        invalid_box_coords = self.map[1].union(robot_agent.map[1])
        valid_box_coords = self.map[2].union(robot_agent.map[2]).difference(invalid_box_coords)
        return [empty_coords, invalid_box_coords, valid_box_coords]

    def look_for_neighbours(self,possible_steps):
        for step in possible_steps:
            cell_container= self.model.grid.get_cell_list_contents(step)
            if not self.is_empty(step):
                instance = cell_container[0]
                if isinstance(instance,RobotAgent):
                    self.map=self.share_map(instance)
    #NO SERIA BUENA IDEA QUE DETECTE SI LA CAJA ES INVALIDA Y AGREGARLA AL MAPA <---------- check
    def update_map(self):
        for y in range(self.pos[1]+1, self.pos[1]+self.vision_intensity+1):
            pos = (self.pos[0],y)
            if self.model.grid.is_cell_empty(pos):
                continue

            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and not instance.picked:
                self.map[2].add(instance.pos)
                break
            if isinstance(instance,BoxAgent) and instance.picked:
                self.map[1].add(instance.pos)
                self.map[2] = self.map[2].difference(self.map[1])
            break
        for y in range(self.pos[1]-1, self.pos[1]-self.vision_intensity-1,-1):
            pos = (self.pos[0],y)
            if self.is_empty(pos):
                continue
            
            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and not instance.picked:
                self.map[2].add(instance.pos)
                break
            if isinstance(instance,BoxAgent) and instance.picked:
                self.map[1].add(instance.pos)
                self.map[2] = self.map[2].difference(self.map[1])
            break
        for x in range(self.pos[0]+1, self.pos[0]+self.vision_intensity+1):
            pos = (x,self.pos[1])
            if self.is_empty(pos):
                continue

            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and not instance.picked:
                self.map[2].add(instance.pos)
                break
            if isinstance(instance,BoxAgent) and instance.picked:
                self.map[1].add(instance.pos)
                self.map[2] = self.map[2].difference(self.map[1])
            break
        for x in range(self.pos[0]-1, self.pos[0]-self.vision_intensity-1,-1):
            pos = (x,self.pos[1])
            if self.is_empty(pos):
                continue
            
            instance = self.model.grid.get_cell_list_contents(pos)[0]
            if isinstance(instance,BoxAgent) and not instance.picked:
                self.map[2].add(instance.pos)
                break
            if isinstance(instance,BoxAgent) and instance.picked:
                self.map[1].add(instance.pos)
                self.map[2] = self.map[2].difference(self.map[1])
            break
        return


    def deliver(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False) # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right)
        self.update_map()
        self.look_for_neighbours(possible_steps)
        if self.deposit_to_near_storage(possible_steps):
            return
        self.move_to_closest_storage(possible_steps)
        
        
        
    def deposit_to_near_storage(self,possible_steps):
        for step in possible_steps:
            cell_container= self.model.grid.get_cell_list_contents(step)
            if not self.is_empty(step):
                if isinstance(cell_container[0],StorageAgent):
                    #Consider two agents taking the box at the same time
                    try:
                        cell_container[0].add_box()
                        self.state = RobotState.EXPLORE
                        self.explore_steps = 1
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
        print("Current Pos:",self.pos)
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
        # 
        self.move()