from typing import TypedDict
 
from flask import Flask, request
from uuid import uuid4

from pandas import DataFrame

from model.model import TrafficModel

app = Flask(__name__)


cache_sims: dict[str, "RandomModel"] = {}

maps = {}


@app.route("/api/v1/init", methods=["POST"])
def init():
    default_params = {
        "initial_cars": 1,
    }

    # Validate Data received
    data = request.get_json()

    map_key = data.get("map", "town")

    # merge dicts into default_params
    default_params.update((k, data[k]) for k in default_params.keys() & data.keys())
    

    # Create Model
    model = TrafficModel(**default_params, map=maps[map_key])

    # Generate a random ID for the modesl
    model_id = str(uuid4())

    # Save the model in the cache
    cache_sims[model_id] = model

    # Get data from agents 
    data = [
        {
            "x": x,
            "y": y,
            f"cell_contents": [ agent.serialized for agent in cell ]
        }
        for (cell, x, y) in model.grid.coord_iter() if cell is not None
    ]

    return {"init_values": default_params , "model_id": model_id, "initial_agents": data}, 201

@app.route("/api/v1/step/<model_id>", methods=["GET"])
def step(model_id):
    model = cache_sims.get(model_id, None)

    if model is None:
        return {"error": "Model not found"}, 404

    model.step()

    # Get data from agents
    data = [
        agent.serialized
        for (agent) in model.schedule.agent_buffer() if agent is not None
    ]


    return {"model_id": model_id, "agents": data}, 200
   
@app.route("/api/v1/statistics/<model_id>")
def statistics(model_id):
    # retun datacollector info 
    pass


if __name__ == "__main__":
    map = None
    with open('./model/town_blocks.txt', 'r') as file: # hardcoded map
        maps["town"] = file.read()[:-1]


    app.run(port=5000, debug=True)