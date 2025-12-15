using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BarrierController : MonoBehaviour
{
    [Header("Barriers")]
    [SerializeField] private List<GameObject> barrierList = new List<GameObject>();
    [SerializeField] private GameObject firstBarrier;

    [Header("Movement Settings")]
    [SerializeField] private float moveSpeed = 5f;

    // TrafficManager eriþimi için public
    [Range(-1, 1)]
    public int moveDirection;

    [Header("Rotation Settings")]
    [SerializeField] private float rotationSpeed = 50f;
    [SerializeField] private float rotateAngle = 25f;

    // --- Kayýt Deðiþkenleri ---
    private List<Vector3> startPositions = new List<Vector3>();
    private Quaternion firstBarrierStartRotation;
    private Vector3 firstBarrierStartPosition;

    // --- Durum Kontrol Deðiþkenleri ---
    private int openBarrierIndex = 0;
    private int closeBarrierIndex;
    private bool openRotationDone = false;

    private bool firstBarrierAligned = false;
    private bool firstBarrierReturned = false;

    public string barrierStatus = "3-3";
    public bool isMoving = false;

    private void Start()
    {
        if (firstBarrier != null)
        {
            firstBarrierStartRotation = firstBarrier.transform.localRotation;
            firstBarrierStartPosition = firstBarrier.transform.localPosition;
        }

        foreach (GameObject barrier in barrierList)
        {
            startPositions.Add(barrier != null ? barrier.transform.localPosition : Vector3.zero);
        }

        closeBarrierIndex = barrierList.Count - 1;
    }

    private void Update()
    {
        // Hareket baþladýðý an true yapýyoruz
        isMoving = true;

        if (moveDirection == 0)
        {
            PerformCloseSequence();

            // Açýlma deðiþkenlerini sýfýrla
            openBarrierIndex = 0;
            openRotationDone = false;
            firstBarrierAligned = false;
            barrierStatus = "3-3";
        }
        else
        {
            PerformOpenSequence();

            // Kapanma deðiþkenlerini sýfýrla
            closeBarrierIndex = barrierList.Count - 1;
            firstBarrierReturned = false;
        }
    }

    private void PerformOpenSequence()
    {
        if (!openRotationDone)
        {
            RotateFirstBarrier(true);
        }
        else if (openBarrierIndex < barrierList.Count)
        {
            MoveBarriersOpen();
        }
        else
        {
            AlignFirstBarrier();
        }
    }

    // --- DEÐÝÞÝKLÝK BURADA YAPILDI ---
    private void PerformCloseSequence()
    {
        // 1. ADIM: Önce listedeki diðer bariyerler (sondan baþa) yerine dönsün
        if (closeBarrierIndex >= 0)
        {
            MoveBarriersClose();
        }
        // 2. ADIM: Liste bitince, First Barrier pozisyonuna (X ekseninde) geri dönsün
        else if (!firstBarrierReturned)
        {
            ReturnFirstBarrierToStart();
        }
        // 3. ADIM: En son First Barrier dönerek (Rotasyon) kapansýn
        else
        {
            RotateFirstBarrier(false);
        }
    }

    // --- ÖZEL FONKSÝYONLAR ---

    private void RotateFirstBarrier(bool isOpening)
    {
        if (firstBarrier == null)
        {
            if (isOpening) openRotationDone = true;
            else isMoving = false; // Kapanma tamamen bitti
            return;
        }

        Quaternion targetRot;
        if (isOpening)
        {
            float targetY = (moveDirection == 1) ? rotateAngle : -rotateAngle;
            targetRot = Quaternion.Euler(0, targetY, 0);
        }
        else
        {
            targetRot = firstBarrierStartRotation;
        }

        firstBarrier.transform.localRotation = Quaternion.RotateTowards(
            firstBarrier.transform.localRotation,
            targetRot,
            rotationSpeed * Time.deltaTime
        );

        if (Quaternion.Angle(firstBarrier.transform.localRotation, targetRot) < 0.1f)
        {
            firstBarrier.transform.localRotation = targetRot;

            if (isOpening) openRotationDone = true;
            else isMoving = false; // Kapanma iþlemi bitti, isMoving false oldu.
        }
    }

    private void MoveBarriersOpen()
    {
        GameObject currentBarrier = barrierList[openBarrierIndex];
        if (currentBarrier == null) { openBarrierIndex++; return; }

        float targetX = (moveDirection == 1) ? 4.75f : -4.75f;
        Vector3 targetPos = new Vector3(targetX, currentBarrier.transform.localPosition.y, currentBarrier.transform.localPosition.z);

        currentBarrier.transform.localPosition = Vector3.MoveTowards(currentBarrier.transform.localPosition, targetPos, moveSpeed * Time.deltaTime);

        if (Vector3.Distance(currentBarrier.transform.localPosition, targetPos) < 0.001f)
        {
            currentBarrier.transform.localPosition = targetPos;
            openBarrierIndex++;
        }
    }

    private void AlignFirstBarrier()
    {
        if (firstBarrier == null) { isMoving = false; return; }

        float targetX = (moveDirection == 1) ? 4.75f : -4.75f;
        Vector3 targetPos = new Vector3(targetX, firstBarrierStartPosition.y, firstBarrierStartPosition.z);
        Quaternion targetRot = firstBarrierStartRotation;

        firstBarrier.transform.localPosition = Vector3.MoveTowards(firstBarrier.transform.localPosition, targetPos, moveSpeed * Time.deltaTime);
        firstBarrier.transform.localRotation = Quaternion.RotateTowards(firstBarrier.transform.localRotation, targetRot, rotationSpeed * Time.deltaTime);

        if (Vector3.Distance(firstBarrier.transform.localPosition, targetPos) < 0.001f &&
            Quaternion.Angle(firstBarrier.transform.localRotation, targetRot) < 0.1f)
        {
            firstBarrier.transform.localPosition = targetPos;
            firstBarrier.transform.localRotation = targetRot;

            barrierStatus = (moveDirection == 1) ? "4-2" : "2-4";
            firstBarrierAligned = true;
            isMoving = false;
        }
    }

    private void ReturnFirstBarrierToStart()
    {
        if (firstBarrier == null) { firstBarrierReturned = true; return; }

        Vector3 targetPos = firstBarrierStartPosition;
        firstBarrier.transform.localPosition = Vector3.MoveTowards(firstBarrier.transform.localPosition, targetPos, moveSpeed * Time.deltaTime);

        if (Vector3.Distance(firstBarrier.transform.localPosition, targetPos) < 0.001f)
        {
            firstBarrier.transform.localPosition = targetPos;
            firstBarrierReturned = true;
        }
    }

    private void MoveBarriersClose()
    {
        if (closeBarrierIndex < 0) return;

        GameObject currentBarrier = barrierList[closeBarrierIndex];
        if (currentBarrier == null) { closeBarrierIndex--; return; }

        Vector3 targetPos = startPositions[closeBarrierIndex];

        currentBarrier.transform.localPosition = Vector3.MoveTowards(currentBarrier.transform.localPosition, targetPos, moveSpeed * Time.deltaTime);

        if (Vector3.Distance(currentBarrier.transform.localPosition, targetPos) < 0.001f)
        {
            currentBarrier.transform.localPosition = targetPos;
            closeBarrierIndex--;
        }
    }
}