using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TrafficManager : MonoBehaviour
{
    [Header("Genel Ayarlar")]
    [SerializeField] private Traffic trafficDensity;
    [SerializeField] private Transform carParent;

    [Header("Listeler")]
    [SerializeField] private List<Transform> spawnPoints = new List<Transform>();
    [SerializeField] private List<GameObject> carList = new List<GameObject>();

    [Header("Spawn Noktalarý")]
    [SerializeField] private Transform spawnPoint_1;
    [SerializeField] private Transform spawnPoint_2;
    [SerializeField] private Transform spawnPoint_3;
    [SerializeField] private Transform spawnPoint_4;

    [Header("Hareket Ayarlarý")]
    [SerializeField] private float moveDirection;
    [SerializeField] private float moveSpeed;

    [SerializeField] private string barrierStatus;

    private BarrierController cachedBarrierController;
    private string lastKnownStatus = "";
    private bool lastIsMoving = false;

    public enum Traffic
    {
        Low,
        Medium,
        High
    }

    private void Start()
    {
        GameObject managerObj = GameObject.FindWithTag("BarrierManager");
        if (managerObj != null)
        {
            cachedBarrierController = managerObj.GetComponent<BarrierController>();
        }
        else
        {
            Debug.LogError("BarrierManager bulunamadý!");
        }

        if (cachedBarrierController != null)
        {
            UpdateSpawnLanes(cachedBarrierController.barrierStatus, cachedBarrierController.isMoving);
        }

        StartCoroutine(SpawnTrafficRoutine());
    }

    private void Update()
    {
        if (cachedBarrierController == null) return;

        string currentStatus = cachedBarrierController.barrierStatus;
        bool currentMoving = cachedBarrierController.isMoving;

        if (currentStatus != lastKnownStatus || currentMoving != lastIsMoving)
        {
            barrierStatus = currentStatus;
            UpdateSpawnLanes(currentStatus, currentMoving);
            lastKnownStatus = currentStatus;
            lastIsMoving = currentMoving;
        }
    }


    public void NextTrafficDensity()
    {
        if (trafficDensity == Traffic.Low)
        {
            trafficDensity = Traffic.Medium;
        }
        else if (trafficDensity == Traffic.Medium)
        {
            trafficDensity = Traffic.High;
        }
        else // High ise
        {
            trafficDensity = Traffic.Low;
        }
    }

    public Traffic GetTrafficDensity()
    {
        return trafficDensity;
    }

    void UpdateSpawnLanes(string status, bool isMoving)
    {
        spawnPoints.Clear();

        // --- HAREKET DURUMU (KESÝN ÇÖZÜM) ---
        if (isMoving)
        {
            // Bariyerin hedeflediði yönü alýyoruz (BarrierController'dan public yaptýk)
            int barrierDir = cachedBarrierController.moveDirection;

            // Bariyer SAÐA (1) açýlýyorsa VE biz SAÐ (1) þeritteysek -> Geniþleyen Tarafýz
            if (barrierDir == 1 && moveDirection == 1)
            {
                AddPoints(spawnPoint_1, spawnPoint_2, spawnPoint_3);
            }
            // Bariyer SOLA (-1) açýlýyorsa VE biz SOL (-1) þeritteysek -> Geniþleyen Tarafýz
            else if (barrierDir == -1 && moveDirection == -1)
            {
                AddPoints(spawnPoint_1, spawnPoint_2);
            }
            // Diðer tüm durumlar (Daralan taraf veya Kapanma durumu) -> Güvenli Mod (2 Þerit)
            else
            {
                AddPoints(spawnPoint_1, spawnPoint_2, spawnPoint_3);
            }
            return;
        }

        // --- NORMAL DURUM (Hareket Bittiðinde) ---
        if (moveDirection == -1)
        {
            // TERS YÖN:
            if (status == "3-3")
            {
                AddPoints(spawnPoint_1, spawnPoint_2, spawnPoint_3);
            }
            else if (status == "4-2") // Geniþleme (4 Þerit)
            {
                AddPoints(spawnPoint_1, spawnPoint_2, spawnPoint_3, spawnPoint_4);
            }
            else // Daralma
            {
                AddPoints(spawnPoint_1, spawnPoint_2);
            }
        }
        else
        {
            // DÜZ YÖN:
            if (status == "3-3")
            {
                AddPoints(spawnPoint_1, spawnPoint_2, spawnPoint_3);
            }
            else if (status == "4-2") // Daralma
            {
                AddPoints(spawnPoint_1, spawnPoint_2);
            }
            else // Geniþleme (4 Þerit)
            {
                AddPoints(spawnPoint_1, spawnPoint_2, spawnPoint_3, spawnPoint_4);
            }
        }
    }

    void AddPoints(params Transform[] points)
    {
        spawnPoints.AddRange(points);
    }

    IEnumerator SpawnTrafficRoutine()
    {
        while (true)
        {
            float waitTime = GetSpawnDelay();
            yield return new WaitForSeconds(waitTime);
            SpawnCar();
        }
    }

    void SpawnCar()
    {
        if (spawnPoints.Count == 0 || carList.Count == 0) return;

        int randomSpawnIndex = Random.Range(0, spawnPoints.Count);
        Transform selectedLane = spawnPoints[randomSpawnIndex];

        int randomCarIndex = Random.Range(0, carList.Count);
        GameObject selectedCarPrefab = carList[randomCarIndex];

        Quaternion spawnRotation = selectedLane.rotation;
        if (moveDirection == -1)
        {
            spawnRotation = Quaternion.Euler(0, 180, 0);
        }

        GameObject newCar = Instantiate(selectedCarPrefab, selectedLane.position, spawnRotation, carParent);

        Car carScript = newCar.GetComponent<Car>();
        if (carScript != null)
        {
            carScript.speed = moveSpeed;
        }
    }

    float GetSpawnDelay()
    {
        switch (trafficDensity)
        {
            case Traffic.Low:
                return Random.Range(2f, 4f);
            case Traffic.Medium:
                return Random.Range(1f, 2f);
            case Traffic.High:
                return Random.Range(0.30f, 0.55f);
            default:
                return 2f;
        }
    }
}