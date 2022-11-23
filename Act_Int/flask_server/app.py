from typing import TypedDict
 
from flask import Flask, request
from uuid import uuid4

from pandas import DataFrame

from mesa_model.model import RandomModel

app = Flask(__name__)


cache_sims: dict[str, "RandomModel"] = {}


@app.route("/api/v1/init", methods=["POST"])
def init():
    default_params = {
        "num_robots": 1,
        "num_boxes": 10,
        "max_time": 500,
        "width": 10,
        "height": 10,
        "vision_intensity": 1,
        "num_storage": 1
    }

    # Validate Data received
    data = request.get_json()

    # merge dicts into default_params
    default_params.update((k, data[k]) for k in default_params.keys() & data.keys())
    

    # Create Model
    model = RandomModel(**default_params)

    # Generate a random ID for the modesl
    model_id = str(uuid4())

    # Save the model in the cache
    cache_sims[model_id] = model

    return {"init_values": default_params , "model_id": model_id}, 201

@app.route("/api/v1/step/<model_id>", methods=["GET"])
def step(model_id):
    model = cache_sims[model_id]
    model.step()

    # Get data from agents
    data = [
        agent.serialized
        for (agent, x, y) in model.grid.coord_iter() if agent is not None
    ]


    return {"model_id": model_id, "agents": data}, 200
   
@app.route("/api/v1/statistics/<model_id>")
def statistics(model_id):
    # retun datacollector info 
    model = cache_sims[model_id]
    df: DataFrame = model.datacollector.get_agent_vars_dataframe()

    result_dict = { 
        "max_steps": model.max_time,
        "current_time": model.time,
        "finished": not model.running,
        "boxes_collected": sum(map(lambda x: x.box_count, model.storages)),
        "total_boxes": model.num_box
     }

    last_rows = df[-model.num_agents:]
    agents_data = []
    for (index, row) in last_rows.iterrows():
        agents_data.append({
            "agent_id": index[1], # index => (Step, AgentID)
            "steps": int(row["Steps"])
        })

    result_dict["robots_collected_data"] = agents_data

    return result_dict, 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)