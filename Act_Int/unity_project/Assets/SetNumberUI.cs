using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
 
public class SetNumberUI : MonoBehaviour
{

    TextMeshProUGUI text;
    public string prefixText;

    public void SetNumberText(int number) {
        text.text = prefixText + number.ToString();
    }
}
