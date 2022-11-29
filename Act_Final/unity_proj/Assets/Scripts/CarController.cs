using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CarController : MonoBehaviour
{

    public Vector3 currentDestination;
    float timer,dt;
    float timeToUpdate = 1f;

    Quaternion startingRotation;

    public float speed = 5;
    public float percentSteerComplete = 0.5f;

    float distance;

    bool hasTarget;

    public float carLength;

    // Start is called before the first frame update
    void Start()
    {
       carLength =  Vector3.Scale(transform.localScale, GetComponentInChildren<MeshRenderer>().bounds.size).z;
       Debug.LogFormat("Car Length: {0}", carLength);
    }    


    // Update is called once per frame
    void Update()
    {
        // if (Input.GetMouseButtonDown(0)) {  
        //     RaycastHit hit;
        //     Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);

        //     if (Physics.Raycast(ray, out hit, 500)) {
        //         Vector3 point = hit.point;
                
        //         // Do something with the object that was hit by the raycast.
        //         startingRotation = transform.rotation;
        //         currentDestination = point;
        //         timer = timeToUpdate;

        //         Debug.LogFormat("updated destination: {0}", currentDestination);

        //         hasTarget = true;
        //     }
            
        // }

        // if(timer <= 0)
        // {
        //     Debug.Log("Reset Timer");
        //     timer = timeToUpdate;
        //     startingRotation = transform.rotation;

        //     // updated = false;
        //     // StartCoroutine(StepSimulation());
        //     hasTarget = false;
        //     return;
        // }

        // if (!hasTarget) return;

        // timer -= Time.deltaTime;
        // dt = 1.0f - (timer / timeToUpdate);

   

        // MoveTo(currentDestination, dt, timer);
    }

    public void StartMove() {
         startingRotation = transform.rotation;
    }

    public void MoveTo(Vector3 destination, float dt, float timer) {
        //Debug.LogFormat("Called MoveTo {0}", destination);
        Vector3 relativeDir = (destination - transform.position);
        relativeDir.Normalize();

        Quaternion finalRotation = Quaternion.LookRotation(relativeDir, Vector3.up);
        transform.rotation = Quaternion.Slerp(startingRotation, finalRotation, dt * 1f + percentSteerComplete);
    
        distance = Vector3.Distance(transform.position, destination) - carLength/2f;
         //Debug.LogFormat("Position {0}", transform.position);
        //Debug.LogFormat("Distance {0}", distance);

        speed = distance / timer;

        transform.Translate(Vector3.forward * speed * Time.deltaTime, Space.Self);


    }


}
