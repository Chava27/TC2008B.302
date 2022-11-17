from model import RandomModel, ObstacleAgent, BoxAgent, StorageAgent, RobotAgent
from agent import RobotState
import mesa
from mesa.visualization.modules import CanvasGrid, BarChartModule
from mesa.visualization.ModularVisualization import ModularServer

def agent_portrayal(agent):
    if agent is None: return
    
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 1,
                 "Color": "green",
                 "w": 0.5,
                 "h": 0.5}

    if (isinstance(agent, RobotAgent)):
        portrayal["Color"] = "green" if agent.state == RobotState.EXPLORE else "blue"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2

    if (isinstance(agent, ObstacleAgent)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2

    if (isinstance(agent, BoxAgent)):
        portrayal["Color"] = "brown"
        portrayal["Layer"] = 0
        portrayal["Shape"]= "rect"
        portrayal["w"]= .3
        portrayal["h"]= .3
    
    if (isinstance(agent, StorageAgent)):
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
        portrayal["Shape"]= "rect"
        portrayal["w"]= .7
        portrayal["h"]= .7
        portrayal["text"] = f"Count: {agent.box_count}"
        portrayal["text_color"] = "black"


    return portrayal

model_params = {"N":mesa.visualization.Slider("N", 1,1,10), "B":10, "width":10, "height":10, "vision_intensity":mesa.visualization.Slider("vision_intensity",1,1,10), "num_storage":mesa.visualization.Slider("num_storage",1,1,5)}
#number of steps before ending
model_params["max_time"] = 500

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

bar_chart_s = BarChartModule(
    [{"Label":"Steps", "Color":"#AA0000"}], 
    scope="agent", sorting="ascending", sort_by="Steps",canvas_height=200,
        canvas_width=400)
'''
bar_chart_t = BarChartModule(
    [{"Label":"Trash", "Color":"#72755E"}],
    scope="agent", sorting="ascending", sort_by="Trash",canvas_height=200,
        canvas_width=400)
'''


server = ModularServer(RandomModel, [grid, bar_chart_s], "Random Agents", model_params)
                       
server.port = 8521 # The default
server.launch()