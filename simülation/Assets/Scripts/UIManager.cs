using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
public class UIManager : MonoBehaviour
{
    [SerializeField] private TMP_Text buttonLeft_text;
    [SerializeField] private TMP_Text buttonRight_text;

    [SerializeField] TrafficManager trafficManagerLeft;
    [SerializeField] TrafficManager trafficManagerRight;

    private void Update()
    {
        WriteTrafficDensity();
    }

    private void WriteTrafficDensity()
    {
        if (trafficManagerLeft != null && buttonLeft_text != null)
        {
            string trafficDensity = trafficManagerLeft.GetTrafficDensity().ToString();

            if (trafficDensity == "Low") buttonLeft_text.text = "Az Yoðun";
            if (trafficDensity == "Medium") buttonLeft_text.text = "Orta Yoðun";
            if (trafficDensity == "High") buttonLeft_text.text = "Çok Yoðun";

        }

        if (trafficManagerRight != null && buttonRight_text != null)
        {
            string trafficDensity = trafficManagerRight.GetTrafficDensity().ToString();

            if (trafficDensity == "Low") buttonRight_text.text = "Az Yoðun";
            if (trafficDensity == "Medium") buttonRight_text.text = "Orta Yoðun";
            if (trafficDensity == "High") buttonRight_text.text = "Çok Yoðun";
        }
    }


    public void ChangeTrafficStaution()
    {
        GameObject tiklananButon = EventSystem.current.currentSelectedGameObject;

        if (tiklananButon.tag == "Button_Left")
        {
            trafficManagerLeft.NextTrafficDensity();
        }
        else
        {
            trafficManagerRight.NextTrafficDensity();
        }
    }

    public void IncreaseMoveDirection()
    {
        if(GameObject.FindWithTag("BarrierManager").GetComponent<BarrierController>().moveDirection < 1)
            GameObject.FindWithTag("BarrierManager").GetComponent<BarrierController>().moveDirection += 1;
    }

    public void DecreaseMoveDirection()
    {
        if (GameObject.FindWithTag("BarrierManager").GetComponent<BarrierController>().moveDirection > -1)
            GameObject.FindWithTag("BarrierManager").GetComponent<BarrierController>().moveDirection -= 1;
    }


}
