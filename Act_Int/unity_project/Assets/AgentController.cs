// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2021

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

    // Box
    public bool picked;

    // Storage
     public int box_count;

     // Robot
      public int state;
}

[Serializable]

public class AgentsData<T> where T : AgentData
{
    public List<T> agents;

    public AgentsData() => this.agents = new List<T>();
}

[Serializable]
public class InitRequest {
    public int num_robots, num_boxes, width, height, vision_intensity, num_storage;
}

[Serializable]
public class InitResponse {
    public string model_id;
}

public class AgentController : MonoBehaviour
{
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:5000";
    string sendConfigEndpoint = "/api/v1/init";
    string stepEndpoint = "/api/v1/step";

    AgentsData<AgentData> obstaclesData;
    AgentsData<AgentData> robotsData;
    AgentsData<AgentData> storagesData;
    AgentsData<AgentData> boxesData;

    Dictionary<string, GameObject> agents;
    Dictionary<string, Vector3> prevPositions, currPositions;

    string modelID;

    bool updated = false, started = false;

    public GameObject agentPrefab, obstaclePrefab, floor, storagePrefab, boxPrefab;
    public int nRobots,nBoxes,maxTime, visionIntensity, nStorages, width, height;
    public float timeToUpdate = 5.0f;
    private float timer, dt;


    void Start()
    {
        obstaclesData =  new AgentsData<AgentData>();
        robotsData = new AgentsData<AgentData>();
        storagesData = new AgentsData<AgentData>();
        boxesData = new AgentsData<AgentData>();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();

        floor.transform.localScale = new Vector3((float)width/10, 1, (float)height/10);
        floor.transform.localPosition = new Vector3((float)width/2-0.5f, 0, (float)height/2-0.5f);
        
        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    private void Update() 
    {
        if(timer < 0)
        {
            Debug.Log("Reset Timer");
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(StepSimulation());
        }

        if (updated)
        {
    
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach(var agent in currPositions)
            {
                Debug.Log("UpdatePositions");
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                Debug.Log(interpolated);

                agents[agent.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);


            }

            // set new properties

            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
        }
    }
 
    IEnumerator SendConfiguration()
    {
        InitRequest initRequest = new InitRequest();
        initRequest.num_robots = nRobots;
        initRequest.num_boxes = nBoxes;
        initRequest.num_storage = nStorages;
        initRequest.width = width;
        initRequest.height = height;
        initRequest.vision_intensity = visionIntensity;
       
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
            StartCoroutine(StepSimulation());
        }
    }

    IEnumerator StepSimulation() {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + stepEndpoint + "/" + modelID);
        yield return www.SendWebRequest();

         if (www.result != UnityWebRequest.Result.Success) {
            Debug.Log(www.error);
            yield return null;
        }

        AgentsData<AgentData> agentsData = JsonUtility.FromJson<AgentsData<AgentData>>(www.downloadHandler.text);

        foreach(AgentData agent in agentsData.agents) {
            Debug.Log(agent);
            Vector3 newPosition = new Vector3(agent.agent_pos.x, 1, agent.agent_pos.y);

            if (!started) {
                // instantiate
                prevPositions[agent.agent_id] = newPosition;

                var prefab = agentPrefab;
                Debug.Log(agent.agent_type);
                switch (agent.agent_type) {
                   
                    case "RobotAgent":
                        prefab = agentPrefab;
                        break;
                    case "ObstacleAgent":
                        prefab = obstaclePrefab;
                        break;
                    case "StorageAgent":
                        prefab = storagePrefab;
                        break;
                    case "BoxAgent":
                        prefab = boxPrefab;
                        break;
                }

                agents[agent.agent_id] = Instantiate(prefab, newPosition, Quaternion.identity);
            } else {
                 Vector3 currentPosition = new Vector3();

                 if(currPositions.TryGetValue(agent.agent_id, out currentPosition))
                        prevPositions[agent.agent_id] = currentPosition;
                 currPositions[agent.agent_id] = newPosition;

                switch (agent.agent_type) {
                    case "RobotAgent":
                        agents[agent.agent_id].GetComponent<Robot>().ActivateMiniBox(agent.state == 1);
                        break;
                    case "ObstacleAgent":
                        
                        break;
                    case "StorageAgent":
                        agents[agent.agent_id].GetComponent<Storage>().SetStackBoxes(agent.box_count);
                        break;
                    case "BoxAgent":
                        // BoxAgent agentT = (BoxAgent) agent;
                         agents[agent.agent_id].SetActive(!agent.picked);

                        break;
                }
            }

        }

        updated = true;
    }
}
