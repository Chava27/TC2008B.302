using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SemaphoreLights : MonoBehaviour
{
    public bool active;
    [ColorUsage(true, true)]
    public Color Red;
    [ColorUsage(true, true)]
    public Color Green;
    [ColorUsage(true, true)]
    public Color Black;

    private Material[] materials;
    public void SetActive(bool active){
        if (active){
            materials[1].SetColor("_EmissionColor", Black);
            materials[2].SetColor("_EmissionColor", Red);
            materials[3].SetColor("_EmissionColor", Black);
            return;
        }
            materials[2].SetColor("_EmissionColor", Black);
            materials[3].SetColor("_EmissionColor", Green);
            materials[1].SetColor("_EmissionColor", Black);
            return;
    }
    // Start is called before the first frame update
    void Start()
    {
        materials = GetComponentInChildren<MeshRenderer>().materials;
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
