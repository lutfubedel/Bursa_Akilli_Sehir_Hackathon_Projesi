using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Car : MonoBehaviour
{
    [Header("Temel Ayarlar")]
    public float speed = 10f;
    [SerializeField] private float destroyTime = 10f;

    [Header("Þerit Deðiþtirme / Kaçýnma")]
    [SerializeField] private float detectionDistance = 8f;   // Engeli görme mesafesi
    [SerializeField] private float dodgeSpeed = 5f;          // Saða kayma hýzý
    [SerializeField] private float totalShiftAmount = 4.5f;  // Toplam ne kadar saða kaysýn?
    [SerializeField] private LayerMask barrierLayer;         // Bariyer katmaný

    // --- Durum Deðiþkenleri ---
    private float currentShift = 0f;    // Þu ana kadar ne kadar kaydýk?
    private bool isDodging = false;     // Þu an kaçýnma manevrasý yapýyor mu?

    void Start()
    {
        Destroy(gameObject, destroyTime);
    }

    void Update()
    {
        // 1. Her zaman ileri git
        transform.Translate(Vector3.forward * speed * Time.deltaTime);

        // 2. Eðer hedeflediðimiz (4.5 birim) kayma miktarýna henüz ulaþmadýysak kontrol et
        if (currentShift < totalShiftAmount)
        {
            // Raycast Kaynaðý
            Vector3 rayOrigin = transform.position + Vector3.up * 0.5f;

            // Eðer manevra zaten baþladýysa (isDodging) VEYA yeni bir engel gördüysek
            if (isDodging || Physics.Raycast(rayOrigin, transform.forward, out RaycastHit hit, detectionDistance, barrierLayer))
            {
                PerformLaneChange();
            }
        }
    }

    void PerformLaneChange()
    {
        // Manevra baþladý olarak iþaretle (Böylece raycast temasý kesilse bile hareketi tamamlar)
        isDodging = true;

        // Bu frame'de ne kadar saða gideceðimizi hesapla
        float moveStep = dodgeSpeed * Time.deltaTime;

        // Eðer bu adýmda 4.5 birimi geçeceksek, sadece kalan miktar kadar git
        if (currentShift + moveStep > totalShiftAmount)
        {
            moveStep = totalShiftAmount - currentShift;
        }

        // Saða kaydýr
        transform.Translate(Vector3.right * moveStep);

        // Kaydedilen miktarý güncelle
        currentShift += moveStep;

        // Eðer 4.5 birim tamamlandýysa manevrayý bitir
        if (currentShift >= totalShiftAmount)
        {
            isDodging = false; // Artýk yeni þeritte düz gitmeye devam eder
        }
    }

    private void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        Vector3 rayOrigin = transform.position + Vector3.up * 0.5f;
        Gizmos.DrawRay(rayOrigin, transform.forward * detectionDistance);
    }
}