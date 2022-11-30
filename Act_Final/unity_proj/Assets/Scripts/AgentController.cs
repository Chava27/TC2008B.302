// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// Stephan Guingor y Salvador 

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;

[Serializable]

public class AgentPos {
    public float x, y;
}

[Serializable]
public class AgentData
{
    public string agent_id, agent_type;
    public AgentPos agent_pos;
     // Robot
    public int orientation;
    public int state;
    public bool active;
}

[Serializable]

public class AgentsData<T> where T : AgentData
{
    public List<T> agents;

    public AgentsData() => this.agents = new List<T>();
}

[Serializable]
public class InitRequest {
    public int initial_cars;
    public string map_name;
    public int max_cars;
    public int freq;
    public int activation_time;
}

[Serializable]
public class BlockData {
    public int x,y;
    public List<AgentData> cell_contents;
}

[Serializable]
public class InitResponse {
    public string model_id;
    public List<BlockData> initial_agents;

    public int width, height;
}

public class AgentController : MonoBehaviour
{
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    public string serverUrl = "http://localhost:5000";
    public string sendConfigEndpoint = "/api/v1/init";
    public string stepEndpoint = "/api/v1/step";

    Dictionary<string, GameObject> semaphores;
    Dictionary<string, GameObject> cars;
    Dictionary<string, Vector3> currPositions;

    string modelID;

    bool updated = false, started = false;

    public GameObject roadPrefab, semaphorePrefab, destinationAgent;

    public GameObject[] buildingPrefabs;
    public GameObject[] carPrefabs;

    public int nCars;
    public string mapName;
    public int max_cars;
    public int freq;
    public int activation_time;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    [SerializeField] int tileSize;

    AgentsData<AgentData> bufferedNextData;



    void Start()
    {
        currPositions = new Dictionary<string, Vector3>();

        cars = new Dictionary<string, GameObject>();
        semaphores = new Dictionary<string, GameObject>();
        
        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    private void Update() 
    {
        if(timer <= 0)
        {
            Debug.Log("Reset Timer");
            timer = timeToUpdate;
            updated = false;

            foreach(var car in cars) {
                car.Value.GetComponent<CarController>().StartMove();
            }

             StartCoroutine(StepSimulation());
        }

        if (updated)
        {
    
            timer -= Time.deltaTime;
            if (timer < 0){
                timer = 0;
            }
            else{
            dt = 1.0f - (timer / timeToUpdate);

            foreach(var car in cars)
            {

               car.Value.GetComponent<CarController>().MoveTo(currPositions[car.Key], dt, timer);
            }
            }
        }
    }


    Quaternion getOrientationFromEnum(int enumOrientation, bool invert) {
        Debug.LogFormat("Rot {0}", enumOrientation);
        if (enumOrientation == 0) {
            return Quaternion.Euler(0, 180 * (-1 * Convert.ToInt32(invert)), 0);
        }

        if (enumOrientation == 1) {
            return Quaternion.Euler(0, 0 * (-1 *Convert.ToInt32(invert)), 0);
        }

        if (enumOrientation == 2) {
            return Quaternion.Euler(0, -90 * (-1 * Convert.ToInt32(invert)), 0);
        }

        if (enumOrientation == 3) {
            return Quaternion.Euler(0, 90 * (-1 * Convert.ToInt32(invert)), 0);
        }

        return Quaternion.identity;
    }
    
    
    GameObject? instanceGameObjectFromAgent(AgentData data, Vector3 position) {
        switch (data.agent_type) {
            case "ObstacleAgent":
                return Instantiate(buildingPrefabs[UnityEngine.Random.Range(0, buildingPrefabs.Length)], position, Quaternion.identity);
            case "CarAgent":
                 cars[data.agent_id] = Instantiate(carPrefabs[UnityEngine.Random.Range(0, carPrefabs.Length)], position, Quaternion.identity);
                 currPositions[data.agent_id] = position;
                 return cars[data.agent_id];
            case "RoadAgent":
                return Instantiate(roadPrefab, position, getOrientationFromEnum(data.orientation, true));
            case "StopAgent":
                Debug.LogFormat("Stop SIGN: {0}", getOrientationFromEnum(data.orientation, true));
                Debug.Log(data.agent_id);
                semaphores[data.agent_id] = Instantiate(semaphorePrefab, position,  getOrientationFromEnum(data.orientation, true));
                return semaphores[data.agent_id];
            case "DestinationAgent":
                return Instantiate(destinationAgent, position, Quaternion.identity);
        }

        Debug.LogFormat("Unknown agent: {0}", data.agent_type);

        return null;

    }
    public void CreateCity(List<BlockData> blocks, int width, int height) {
        Vector3 position;
        GameObject? tile;

        foreach (BlockData block in blocks) {
            foreach (AgentData agent in block.cell_contents) { // should be at most one at city creation
                position = new Vector3(block.x * tileSize, 0, block.y * tileSize);

                tile = instanceGameObjectFromAgent(agent, position);

                if ( tile != null ) {
                    tile.transform.parent = transform;
                }
            }
           
        }

    }

    IEnumerator SendConfiguration()
    {
        InitRequest initRequest = new InitRequest();
        initRequest.initial_cars = nCars;
        initRequest.map_name = mapName;

    
        string jsonData = JsonUtility.ToJson(initRequest, true);

       var request = new UnityWebRequest(serverUrl + sendConfigEndpoint, "POST");
       byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
       request.uploadHandler = (UploadHandler) new UploadHandlerRaw(bodyRaw);
       request.downloadHandler = (DownloadHandler) new DownloadHandlerBuffer();
       request.SetRequestHeader("Content-Type", "application/json");

       yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            InitResponse response = JsonUtility.FromJson<InitResponse>(request.downloadHandler.text);
            modelID = response.model_id;


            Debug.Log("Configuration upload complete!");
            Debug.Log(modelID);
            Debug.Log("Getting Agents positions");
            
            CreateCity(response.initial_agents, response.width, response.height);
            Debug.Log("City Created!!");
        }

        started = true;
        updated = true;

        StartCoroutine(StepSimulation());
    }

    IEnumerator StepSimulation() {
         UnityWebRequest www;
         AgentsData<AgentData> agentsData;
        //if (bufferedNextData == null)  {
            www = UnityWebRequest.Get(serverUrl + stepEndpoint + "/" + modelID);
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success) {
                Debug.Log(www.error);
                yield return null;
            }

            agentsData = JsonUtility.FromJson<AgentsData<AgentData>>(www.downloadHandler.text);
            bufferedNextData = agentsData;
        //}

        Vector3 newPosition;

        foreach(AgentData agent in bufferedNextData.agents) {
            switch (agent.agent_type) {
                case "CarAgent":
                    newPosition = new Vector3(agent.agent_pos.x * tileSize, 1, agent.agent_pos.y * tileSize);

                    // destroy car if arrived
                    if (agent.state == 2) {
                        Destroy(cars[agent.agent_id]);
                        cars.Remove(agent.agent_id);
                        currPositions.Remove(agent.agent_id);
                        continue;
                    }

                     // try to get car from cache if not instantiate it
                    if (cars.ContainsKey(agent.agent_id)) {
                        currPositions[agent.agent_id] = newPosition;
                    } else {
                        cars[agent.agent_id] = Instantiate(carPrefabs[UnityEngine.Random.Range(0, carPrefabs.Length)], newPosition, Quaternion.identity);
                        currPositions[agent.agent_id] = newPosition;
                    }
    
                    Debug.LogFormat("Next Pos: {0},{1},{2}", newPosition.x, newPosition.y,  newPosition.z);
                    break;
                case "StopAgent":
                    Debug.Log(agent.agent_id);
                    semaphores[agent.agent_id].GetComponent<SemaphoreLights>().SetActive(agent.active);
                    break;
            }

        }
        

        updated = true;
/*
        www = UnityWebRequest.Get(serverUrl + stepEndpoint + "/" + modelID);
        yield return www.SendWebRequest();

         if (www.result != UnityWebRequest.Result.Success) {
            Debug.Log(www.error);
            yield return null;
        }

        agentsData = JsonUtility.FromJson<AgentsData<AgentData>>(www.downloadHandler.text);
        bufferedNextData = agentsData;
*/
  
    }
}
