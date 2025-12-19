# Smart Barrier System (Akıllı Bariyer Sistemi)

![Unity](https://img.shields.io/badge/Unity-2021.3%2B-black?style=for-the-badge&logo=unity)
![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/Web-React%20%7C%20TypeScript-61DAFB?style=for-the-badge&logo=react)
![IoT](https://img.shields.io/badge/Hardware-IoT%20%28ESP32%2FArduino%29-red?style=for-the-badge&logo=arduino)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Smart Barrier System**, trafik yoğunluğunu gerçek zamanlı olarak analiz eden, fiziksel bariyerleri yöneten ve tüm süreci hem web arayüzünden hem de dijital ikiz (Unity) üzerinden takip etmeyi sağlayan entegre bir akıllı ulaşım çözümüdür.

Bu proje, özellikle yoğun saatlerde (peak hours) trafik sıkışıklığını azaltmak için karşı şeridi kullanıma açan "Akıllı Şerit" mantığını simüle eder ve uygular.

---

## Sistem Mimarisi

Sistem, sahadan gelen verilerin işlenmesi, karar verilmesi ve fiziksel/dijital ortamlara yansıtılması prensibiyle çalışır.

```mermaid
graph LR
    %% Katman Başlıkları
    FL["Saha ve Donanım Katmanı"]
    PL["İşleme ve Yapay Zeka"]
    AL["Kullanıcı ve Simülasyon"]

    %% Saha
    CAM["IP Kamera / WebCam"]
    ESP["IoT Cihazı (ESP32 / Arduino)"]
    BAR["Fiziksel Bariyer / Motor"]

    %% İşleme
    YOLO["Python + YOLOv8"]
    SERVER["Backend / MQTT Broker"]
    DB["Veritabanı"]

    %% Uygulama
    WEB["React + TypeScript Dashboard"]
    UNITY["Unity 3D Digital Twin"]

    %% Akış
    CAM --> YOLO
    YOLO --> SERVER
    SERVER --> DB
    SERVER --> ESP
    ESP --> BAR
    WEB --> SERVER
    SERVER --> WEB
    SERVER --> UNITY
    UNITY --> SERVER

    %% Görsel Stil
    classDef title fill:#2b2b2b,color:#ffffff,stroke:#999,stroke-width:1px
    classDef node fill:#1e1e1e,color:#ffffff,stroke:#777

    class FL,PL,AL title
    class CAM,ESP,BAR,YOLO,SERVER,DB,WEB,UNITY node


```

---

## 🎥 Demo, Videolar ve Sunum

> **Not:** Bu projede statik ekran görüntüleri yerine doğrudan demo videoları kullanılmıştır.  
> Web arayüzü ve proje sunumu için ayrıca harici bağlantılar sağlanmıştır.

---

### 🌐 Web Dashboard & AI Tespiti

Bu bölümde, web tabanlı kontrol paneli üzerinden anlık trafik yoğunluğu takibi ve YOLOv8 tabanlı araç tespit süreci gösterilmektedir.

- Gerçek zamanlı trafik yoğunluğu analizi  
- YOLOv8 ile araç tespiti ve sınıflandırma  
- Otomatik ve manuel bariyer kontrolü  
- Karar mekanizmasının görsel çıktıları  

🎬 **Demo Videosu:**  
https://www.youtube.com/watch?v=WEB_AI_DEMO_VIDEO_ID  

🔗 **Web Dashboard Linki:**  
https://smart-barrier-demo-site-link  

---

### 🎮 Unity Digital Twin Simülasyonu

Bu video, gerçek trafik verilerinin Unity 3D ortamında dijital ikiz (Digital Twin) yaklaşımıyla nasıl simüle edildiğini göstermektedir.

- Dinamik şerit yönetimi  
- Bariyer animasyonları  
- Senaryo ve stres testleri  
- Gerçek zamanlı veri entegrasyonu  

🎬 **Unity Simülasyon Videosu:**  
https://www.youtube.com/watch?v=UNITY_SIMULATION_VIDEO_ID  

---

### 📊 Proje Sunumu

Projenin problem tanımı, sistem mimarisi, kullanılan teknolojiler ve elde edilen sonuçlar bu sunumda detaylı olarak ele alınmıştır.

- Problem tanımı ve motivasyon  
- Sistem mimarisi ve veri akışı  
- Yapay zeka modeli ve karar mekanizması  
- Demo senaryoları ve sonuçlar  

📑 **Sunum Linki:**  
https://presentation-link-buraya  


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
* `BarrierController` ve `TrafficManager` senaryoları ile dinamik akış.

### 🔌 IoT & Donanım
* Servo motorlar ile bariyer kontrolü.
* Sensör verilerinin sunucuya iletilmesi (MQTT/HTTP).
* Acil durum protokolleri.

---

## 🛠️ Teknoloji Yığını (Tech Stack)

| Alan | Teknolojiler |
|---|---|
| **Yapay Zeka** | Python, YOLOv8, OpenCV, NumPy |
| **Frontend** | React, TypeScript, TailwindCSS |
| **Backend / API** | Python (Flask/FastAPI) veya Node.js |
| **Simülasyon** | Unity 3D, C# Scripting |
| **Gömülü Sistem** | C++, Arduino IDE, ESP32/ESP8266 |
| **İletişim** | MQTT, WebSocket, HTTP REST API |

---

## 🚀 Kurulum ve Çalıştırma

Proje modüler bir yapıdadır. İlgili modülü çalıştırmak için aşağıdaki adımları izleyin.

### 1. Repoyu Klonlayın
```bash
git clone [https://github.com/lutfubedel/Smart_Barrier_System.git](https://github.com/lutfubedel/Smart_Barrier_System.git)
cd Smart_Barrier_System
```

### 2. Yapay Zeka (AI) Kurulumu
```bash
cd AI_Detection  # Klasör adını projenize göre güncelleyin
pip install -r requirements.txt
python main.py
```

### 3. Web Arayüzü (Frontend) Kurulumu
```bash
cd Web_Dashboard  # Klasör adını projenize göre güncelleyin
npm install
npm start
```

### 4. IoT (Gömülü Sistem)
* `Arduino` klasöründeki `.ino` dosyasını Arduino IDE ile açın.
* Kart ayarlarınızı yapın ve kodu yükleyin.

### 5. Unity Simülasyonu
* Unity Hub'ı açın.
* `Unity_Simulation` klasörünü proje olarak ekleyin ve başlatın.

---

## 📹 Video Tanıtımı

Projenin tüm detaylarını ve çalışma mantığını anlattığım videoya aşağıdan ulaşabilirsiniz:

[![Video Başlığı](https://img.youtube.com/vi/VIDEO_ID_BURAYA/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID_BURAYA)

---

## 🤝 Katkıda Bulunma

1.  Bu repoyu Fork'layın.
2.  Yeni bir özellik dalı (branch) oluşturun (`git checkout -b feature/YeniOzellik`).
3.  Değişikliklerinizi commit yapın (`git commit -m 'Yeni özellik eklendi'`).
4.  Branch'inizi pushlayın (`git push origin feature/YeniOzellik`).
5.  Bir Pull Request oluşturun.

---

## 📧 İletişim

Geliştirici: **Lütfü Bedel**
GitHub: [lutfubedel](https://github.com/lutfubedel)

*Bu proje MIT Lisansı ile lisanslanmıştır.*
