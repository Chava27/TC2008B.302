from model.model import TrafficModel
#from .agent import RobotState
import mesa
from mesa.visualization.modules import CanvasGrid, BarChartModule
from mesa.visualization.ModularVisualization import ModularServer

map = None
with open('./model/town_blocks.txt', 'r') as file:
    map = file.read()[:-1]

model_params = {"initial_cars":10, "map":map}
#number of steps before ending



server = ModularServer(TrafficModel, [], "Traffic Model", model_params)
                       
server.port = 8521 # The default
server.launch()