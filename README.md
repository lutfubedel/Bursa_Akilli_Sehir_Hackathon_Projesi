# 🚧 Smart Barrier System (Akıllı Bariyer Sistemi)

![Unity](https://img.shields.io/badge/Unity-2021.3%2B-black?style=flat&logo=unity)
![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-blue?style=flat&logo=python)
![React](https://img.shields.io/badge/Web-React%20%7C%20TypeScript-61DAFB?style=flat&logo=react)
![IoT](https://img.shields.io/badge/Hardware-IoT%20%28ESP32%2FArduino%29-red?style=flat&logo=arduino)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

**Smart Barrier System**, trafik yoğunluğunu gerçek zamanlı olarak analiz eden, fiziksel bariyerleri yöneten ve tüm süreci hem web arayüzünden hem de dijital ikiz (Unity) üzerinden takip etmeyi sağlayan entegre bir akıllı ulaşım çözümüdür.

---

## 🏗️ Sistem Mimarisi

Bu proje 4 ana modülden oluşmaktadır:

1.  **Görüntü İşleme (AI):** YOLOv8 ile trafik yoğunluğu ve araç sayımı yapılır.
2.  **IoT & Gömülü Sistem:** Fiziksel bariyerlerin kontrolü ve sensör verilerinin işlenmesi.
3.  **Web Arayüzü (Dashboard):** React & TypeScript ile sistem durumu izleme ve manuel kontrol.
4.  **Simülasyon (Digital Twin):** Unity ile sahadaki durumun 3D ortamda birebir simüle edilmesi.

*(Aşağıdaki alana sistemin blok diyagramını eklemeni öneririm)*
graph TD
    subgraph Field_Layer [Saha ve Donanım Katmanı]
        CAM[📹 IP Kamera / WebCam]
        ESP[📟 IoT Cihazı (ESP32/Arduino)]
        BAR[🚧 Fiziksel Bariyer / Motorlar]
    end

    subgraph Processing_Layer [İşleme ve Yapay Zeka]
        YOLO[🧠 Python & YOLOv8<br/>(Görüntü İşleme)]
        SERVER[🔄 Backend / MQTT Broker]
        DB[(🗄️ Veritabanı)]
    end

    subgraph Application_Layer [Kullanıcı ve Simülasyon]
        WEB[💻 React & TS Web Dashboard<br/>(Kontrol Paneli)]
        UNITY[🎮 Unity 3D Simülasyon<br/>(Digital Twin)]
    end

    %% Bağlantılar
    CAM -->|RTSP/Video Akışı| YOLO
    YOLO -->|Araç Sayısı & Yoğunluk| SERVER
    SERVER <-->|Veri Kaydı| DB
    
    ESP <-->|Sensör Verisi & Komut| SERVER
    ESP -->|PWM Sinyali| BAR
    
    WEB -->|Manuel Bariyer Komutu| SERVER
    SERVER -->|Canlı Veri| WEB
    
    SERVER -->|Gerçek Zamanlı Senkronizasyon| UNITY
    UNITY -->|Simülasyon Verisi (Test)| SERVER

    classDef hardware fill:#f9f,stroke:#333,stroke-width:2px;
    classDef ai fill:#bbf,stroke:#333,stroke-width:2px;
    classDef app fill:#bfb,stroke:#333,stroke-width:2px;
    
    class CAM,ESP,BAR hardware;
    class YOLO,SERVER,DB ai;
    class WEB,UNITY app;

---

## 🎥 Demo ve Ekran Görüntüleri

### 1. Web Dashboard & AI Tespiti
| Dashboard (React) | YOLOv8 Algılama |
|Coords:---|---|
| ![Web UI](https://via.placeholder.com/400x250?text=React+Dashboard+Screenshot) | ![YOLO Detection](https://via.placeholder.com/400x250?text=YOLOv8+Detection+Gif) |

### 2. Unity Simülasyonu & IoT Testi
| Unity Digital Twin | Fiziksel Prototip |
|---|---|
| ![Unity Sim](https://via.placeholder.com/400x250?text=Unity+Simulation+Gif) | ![IoT Hardware](https://via.placeholder.com/400x250?text=Physical+Device+Photo) |

---

## ✨ Özellikler

### 🧠 Yapay Zeka (Python & YOLOv8)
* Gerçek zamanlı araç tespiti ve sınıflandırma (Car, Truck, Bus).
* Şerit bazlı yoğunluk hesabı.
* Dinamik şerit yönetimi için karar mekanizması.

### 🌐 Web Arayüzü (React & TypeScript)
* Anlık trafik durumu görselleştirme.
* Bariyerlerin manuel kontrolü (Aç/Kapa/Yön Değiştir).
* Geçmiş trafik verileri ve loglar.
* Modern ve responsive UI tasarımı.

### 🎮 Simülasyon (Unity 3D)
* Gerçek dünya verilerinin 3D ortamda görselleştirilmesi (Digital Twin).
* Fiziksel bariyer kurulmadan önce senaryo testleri.
* Yapay zeka trafiği ile stres testleri.

### 🔌 IoT & Donanım
* Servo motorlar ile bariyer kontrolü.
* Sensör verilerinin sunucuya iletilmesi (MQTT/HTTP).
* Acil durum protokolleri.

---

## 🛠️ Teknoloji Yığını (Tech Stack)

| Alan | Teknolojiler |
|---|---|
| **Yapay Zeka** | Python, YOLOv8, OpenCV, NumPy |
| **Frontend** | React, TypeScript, TailwindCSS (veya kullandığın UI kütüphanesi) |
| **Backend / API** | Python (Flask/FastAPI) veya Node.js |
| **Simülasyon** | Unity 3D, C# Scripting |
| **Gömülü Sistem** | C++, Arduino IDE, ESP32/ESP8266 |
| **İletişim** | MQTT, WebSocket, HTTP REST API |

---

## 🚀 Kurulum ve Çalıştırma

Proje birden fazla parçadan oluştuğu için her modülün kurulumu aşağıda ayrı ayrı açıklanmıştır.

### 1. Repoyu Klonlayın
```bash
git clone [https://github.com/lutfubedel/Smart_Barrier_System.git](https://github.com/lutfubedel/Smart_Barrier_System.git)
cd Smart_Barrier_System
