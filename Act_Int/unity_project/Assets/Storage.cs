using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Storage : MonoBehaviour
{  
    int stackedBoxes = 0;

    public GameObject boxPrefab;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void SetStackBoxes(int boxes) {
        Debug.Log("Set Stacked Boxes");
        for (int i = stackedBoxes; i < boxes; i++) {
            Debug.Log("Spawning box");
            Vector3 position = new Vector3(transform.localPosition.x, transform.localPosition.y + i + 1, transform.localPosition.z);
            Instantiate(boxPrefab, position, Quaternion.identity);
        }

        stackedBoxes = boxes;
    }   
}
