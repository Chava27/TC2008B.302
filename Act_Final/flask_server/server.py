from model.model import TrafficModel
from model.agent import CarAgent,DestinationAgent, RoadAgent,ObstacleAgent, StopAgent
import mesa
from mesa.visualization.modules import CanvasGrid, BarChartModule
from mesa.visualization.ModularVisualization import ModularServer

map = None
with open('./model/town_blocks.txt', 'r') as file:
    map = file.read()[:-1]

model_params = {"initial_cars":10, "map":map}
#number of steps before ending

def agent_portrayal(agent):
    if agent is None: return
    
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 1,
                 "Color": "green",
                 "w": 0.5,
                 "h": 0.5}

    if (isinstance(agent, CarAgent)):
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2

    if (isinstance(agent, ObstacleAgent)):
        portrayal["Color"] = "black"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2

    if (isinstance(agent, DestinationAgent)):
        portrayal["Color"] = "yellow"
        portrayal["Layer"] = 0
        portrayal["Shape"]= "rect"
        portrayal["w"]= .3
        portrayal["h"]= .3
    
    if (isinstance(agent, RoadAgent)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 0
        portrayal["Shape"]= "rect"
        portrayal["w"]= 1
        portrayal["h"]= 1
        portrayal["text"] = agent.pos
        portrayal["text_color"]="black"

    if (isinstance(agent, StopAgent)):
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
        portrayal["Shape"]= "rect"
        portrayal["w"]= 1
        portrayal["h"]= 1
        portrayal["text"] = agent.pos
        portrayal["text_color"]="black"


    return portrayal


grid = CanvasGrid(agent_portrayal, 26, 26, 500, 500)


server = ModularServer(TrafficModel, [grid], "Traffic Model", model_params)
                       
server.port = 8522 # The default
server.launch()