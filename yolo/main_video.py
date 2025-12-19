import cv2
import sys
import numpy as np
from ultralytics import YOLO
import time

sys.path.append(r"D:\Github Repo\Bursa_Akilli_Sehir_Hackathon_Projesi\iot")
from Transmission2 import MQTTClient, StateBarrier, DirectionBarrier, MQTTConfig

# --- AYARLAR ---
SKIP_RATE = 1
CONFIDENCE = 0.25

# --- YOĞUNLUK EŞİKLERİ ---
LIMIT_LOW = 4
LIMIT_MID = 10

# --- BARIYER KONTROL EŞİKLERİ ---
# Bir taraf yoğunken, diğer tarafın bariyerini aç
BARRIER_THRESHOLD = 8  # Bu sayının üstündeki yoğunluk bariyer açılmasını tetikler

# --- GÜNCEL YAYIN LİNKİ ---
SOURCE_URL = "vehicle-counting.mp4"
OUTPUT_FILENAME = "trafik_analiz_sonucu.mp4"

# --- RENK PALETİ (BGR) ---
COLOR_LEFT = (255, 191, 0)
COLOR_RIGHT = (0, 165, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_RED = (0, 0, 255)
COLOR_WHITE = (255, 255, 255)

# 1. MODEL VE VİDEO BAŞLATMA
print("Model yükleniyor...")
model = YOLO('yolov8n.pt')

print(f"Video kaynağı okunuyor: {SOURCE_URL}")
cap = cv2.VideoCapture(SOURCE_URL, cv2.CAP_FFMPEG)

# --- VİDEO KAYIT AYARLARI ---
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
original_fps = cap.get(cv2.CAP_PROP_FPS)

if original_fps == 0:
    original_fps = 30

print(f"Kayıt başlatılıyor... Çözünürlük: {frame_width}x{frame_height}, FPS: {original_fps}")

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(OUTPUT_FILENAME, fourcc, original_fps, (frame_width, frame_height))

target_classes = [2, 3, 5, 7]

# Değişkenler
prev_frame_time = 0
frame_counter = 0
memory_boxes = []
memory_ids = []

# --- MQTT İStemcisi Başlat ---
print("MQTT bağlantısı kuruluyor...")
mqtt_client = MQTTClient(
    broker=MQTTConfig.BROKER,
    port=MQTTConfig.PORT,
    topic=MQTTConfig.TOPIC
)

if not mqtt_client.connect():
    print("UYARI: MQTT bağlantısı kurulamadı. Sistem MQTT olmadan devam edecek.")
    mqtt_enabled = False
else:
    print("MQTT bağlantısı başarılı!")
    mqtt_enabled = True

# Bariyer durumu takibi (gereksiz mesaj göndermeyi önlemek için)
last_left_barrier_state = None
last_right_barrier_state = None
last_mqtt_send_time = 0
MQTT_SEND_INTERVAL = 2  # En az 2 saniyede bir mesaj gönder


# --- YARDIMCI FONKSİYONLAR ---
def draw_transparent_box(img, x, y, w, h, color, alpha=0.5):
    try:
        sub_img = img[y:y + h, x:x + w]
        white_rect = np.full(sub_img.shape, color, dtype=np.uint8)
        res = cv2.addWeighted(sub_img, 1 - alpha, white_rect, alpha, 1.0)
        img[y:y + h, x:x + w] = res
    except:
        pass


def get_status_and_color(count):
    if count <= LIMIT_LOW:
        return "AKICI", COLOR_GREEN
    elif count <= LIMIT_MID:
        return "NORMAL", COLOR_YELLOW
    else:
        return "YOGUN", COLOR_RED


def control_barriers(left_count, right_count, current_time):
    """Trafik yoğunluğuna göre bariyer kontrolü"""
    global last_left_barrier_state, last_right_barrier_state, last_mqtt_send_time

    if not mqtt_enabled:
        return

    # Minimum gönderim aralığını kontrol et
    if current_time - last_mqtt_send_time < MQTT_SEND_INTERVAL:
        return

    # Sol taraf yoğun mu?
    if left_count > BARRIER_THRESHOLD:
        # Sol taraf yoğun -> Sağ bariyeri aç (sağdan gelen trafiği yavaşlat)
        new_right_state = StateBarrier.MOVE
        if new_right_state != last_right_barrier_state:
            mqtt_client.SendOrder(StateBarrier.MOVE, DirectionBarrier.RIGHT)
            last_right_barrier_state = new_right_state
            last_mqtt_send_time = current_time
            print(f"🚦 SAĞ BARİYER AÇILDI (Sol taraf yoğun: {left_count} araç)")
    else:
        # Sol taraf yoğun değil -> Sağ bariyeri kapat
        new_right_state = StateBarrier.STOP
        if new_right_state != last_right_barrier_state:
            mqtt_client.SendOrder(StateBarrier.STOP, DirectionBarrier.RIGHT)
            last_right_barrier_state = new_right_state
            last_mqtt_send_time = current_time
            print(f"🚦 SAĞ BARİYER KAPATILDI (Sol taraf normal: {left_count} araç)")

    # Sağ taraf yoğun mu?
    if right_count > BARRIER_THRESHOLD:
        # Sağ taraf yoğun -> Sol bariyeri aç (soldan gelen trafiği yavaşlat)
        new_left_state = StateBarrier.MOVE
        if new_left_state != last_left_barrier_state:
            mqtt_client.SendOrder(StateBarrier.MOVE, DirectionBarrier.LEFT)
            last_left_barrier_state = new_left_state
            last_mqtt_send_time = current_time
            print(f"🚦 SOL BARİYER AÇILDI (Sağ taraf yoğun: {right_count} araç)")
    else:
        # Sağ taraf yoğun değil -> Sol bariyeri kapat
        new_left_state = StateBarrier.STOP
        if new_left_state != last_left_barrier_state:
            mqtt_client.SendOrder(StateBarrier.STOP, DirectionBarrier.LEFT)
            last_left_barrier_state = new_left_state
            last_mqtt_send_time = current_time
            print(f"🚦 SOL BARİYER KAPATILDI (Sağ taraf normal: {right_count} araç)")


# --- ANA DÖNGÜ ---
try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Video tamamlandı veya okunamadı.")
            break

        frame_counter += 1
        height, width, _ = frame.shape
        mid_x = width // 2

        # FPS Hesaplama
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time) if (new_frame_time - prev_frame_time) > 0 else 0
        prev_frame_time = new_frame_time

        # --- TESPİT (ByteTrack) ---
        if frame_counter % SKIP_RATE == 0:
            results = model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                verbose=False,
                classes=target_classes,
                conf=CONFIDENCE,
                imgsz=640
            )

            if results[0].boxes.id is not None:
                memory_boxes = results[0].boxes.xyxy.cpu().tolist()
                memory_ids = results[0].boxes.id.int().cpu().tolist()
            else:
                memory_boxes = []
                memory_ids = []

        # --- HESAPLAMA ---
        instant_left = 0
        instant_right = 0

        for box in memory_boxes:
            x1, y1, x2, y2 = map(int, box)
            cx = int((x1 + x2) / 2)
            if cx < mid_x:
                instant_left += 1
            else:
                instant_right += 1

        status_text_L, status_color_L = get_status_and_color(instant_left)
        status_text_R, status_color_R = get_status_and_color(instant_right)

        # --- BARİYER KONTROLÜ (MQTT GÖNDERİMİ) ---
        control_barriers(instant_left, instant_right, new_frame_time)

        # --- GÖRSELLEŞTİRME ---
        # 1. Ortadaki Çizgi
        cv2.line(frame, (mid_x, 0), (mid_x, height), (200, 200, 200), 2, cv2.LINE_AA)

        # 2. Araç Kutuları
        for box, track_id in zip(memory_boxes, memory_ids):
            x1, y1, x2, y2 = map(int, box)
            cx = int((x1 + x2) / 2)
            box_color = COLOR_LEFT if cx < mid_x else COLOR_RIGHT
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2, cv2.LINE_AA)
            cv2.putText(frame, f"#{track_id}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2, cv2.LINE_AA)

        # 3. Bilgi Paneli
        box_x, box_y = 0, 0
        draw_transparent_box(frame, box_x, box_y, 330, 200, (0, 0, 0), alpha=0.85)

        cv2.putText(frame, "BOLGESEL TRAFIK ANALIZI", (box_x + 15, box_y + 25), cv2.FONT_HERSHEY_DUPLEX, 0.6,
                    COLOR_WHITE, 1, cv2.LINE_AA)
        cv2.line(frame, (box_x + 15, box_y + 35), (box_x + 315, box_y + 35), (150, 150, 150), 1, cv2.LINE_AA)

        # Sol Taraf
        line_y_1 = box_y + 65
        cv2.putText(frame, "SOL SERIT", (box_x + 15, line_y_1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_LEFT, 1,
                    cv2.LINE_AA)
        cv2.putText(frame, f"Arac: {instant_left}", (box_x + 130, line_y_1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE,
                    1, cv2.LINE_AA)
        cv2.putText(frame, status_text_L, (box_x + 230, line_y_1), cv2.FONT_HERSHEY_DUPLEX, 0.7, status_color_L, 2,
                    cv2.LINE_AA)

        # Sağ Taraf
        line_y_2 = box_y + 105
        cv2.putText(frame, "SAG SERIT", (box_x + 15, line_y_2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_RIGHT, 1,
                    cv2.LINE_AA)
        cv2.putText(frame, f"Arac: {instant_right}", (box_x + 130, line_y_2), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    COLOR_WHITE, 1, cv2.LINE_AA)
        cv2.putText(frame, status_text_R, (box_x + 230, line_y_2), cv2.FONT_HERSHEY_DUPLEX, 0.7, status_color_R, 2,
                    cv2.LINE_AA)

        # FPS ve MQTT Durumu
        line_y_3 = box_y + 135
        cv2.line(frame, (box_x + 15, line_y_3), (box_x + 315, line_y_3), (150, 150, 150), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Sistem FPS: {int(fps)}", (box_x + 15, line_y_3 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (200, 200, 200), 1, cv2.LINE_AA)

        mqtt_status = "Aktif" if mqtt_enabled else "Devre Disi"
        mqtt_color = COLOR_GREEN if mqtt_enabled else COLOR_RED
        cv2.putText(frame, f"MQTT: {mqtt_status}", (box_x + 15, line_y_3 + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    mqtt_color, 1, cv2.LINE_AA)

        # --- KAYIT İŞLEMİ ---
        out.write(frame)

        if frame_counter % 30 == 0:
            print(
                f"Kare işleniyor: {frame_counter} (Anlık FPS: {int(fps)}) | Sol: {instant_left}, Sağ: {instant_right}")

except KeyboardInterrupt:
    print("\n\nKullanıcı tarafından durduruldu.")

finally:
    # --- TEMİZLİK ---
    print("İşlem tamamlandı. Dosya kaydedildi.")
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    if mqtt_enabled:
        mqtt_client.disconnect()
        print("MQTT bağlantısı kapatıldı.")