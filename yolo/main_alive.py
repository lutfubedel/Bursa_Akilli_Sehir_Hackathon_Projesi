import cv2
import numpy as np
from ultralytics import YOLO
import time

# --- AYARLAR ---
SKIP_RATE = 2        # Her 2 karede bir takip işlemi (Performans için)
CONFIDENCE = 0.35    # Algılama hassasiyeti

# --- YOĞUNLUK EŞİKLERİ ---
LIMIT_LOW = 4
LIMIT_MID = 10

# --- VİDEO KAYNAĞI ---
# SOURCE_URL = "https://canliyayin.bursa.bel.tr/..." # Canlı yayın linkiniz buraya
SOURCE_URL = "vehicle-counting.mp4" # Video dosyanız

# --- RENK PALETİ (BGR) ---
COLOR_LEFT = (255, 191, 0)   # Sol şerit rengi
COLOR_RIGHT = (0, 165, 255)  # Sağ şerit rengi
COLOR_GREEN = (0, 255, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_RED = (0, 0, 255)
COLOR_WHITE = (255, 255, 255)

# 1. MODEL VE VİDEO BAŞLATMA
print("Model yükleniyor...")
model = YOLO('yolov8n.pt')

print(f"Video açılıyor: {SOURCE_URL}")
cap = cv2.VideoCapture(SOURCE_URL, cv2.CAP_FFMPEG)

# Pencere ayarı (Boyutlandırılabilir olması için WINDOW_NORMAL şart)
window_name = "Canlı Trafik Analizi"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
# Başlangıçta makul bir boyutta açılması için:
cv2.resizeWindow(window_name, 1280, 720)

# Hedef sınıflar (Araba, motosiklet, otobüs, kamyon)
target_classes = [2, 3, 5, 7]

# Değişkenler
prev_frame_time = 0
frame_counter = 0
memory_boxes = []
memory_ids = []

# --- YARDIMCI FONKSİYONLAR ---
def draw_transparent_box(img, x, y, w, h, color, alpha=0.5):
    """Yarı saydam siyah arka plan kutusu çizer"""
    try:
        sub_img = img[y:y+h, x:x+w]
        white_rect = np.full(sub_img.shape, color, dtype=np.uint8)
        res = cv2.addWeighted(sub_img, 1-alpha, white_rect, alpha, 1.0)
        img[y:y+h, x:x+w] = res
    except:
        pass

def get_status_and_color(count):
    """Araç sayısına göre trafik durumunu belirler"""
    if count <= LIMIT_LOW:
        return "AKICI", COLOR_GREEN
    elif count <= LIMIT_MID:
        return "NORMAL", COLOR_YELLOW
    else:
        return "YOGUN", COLOR_RED

# --- ANA DÖNGÜ ---
while True:
    ret, frame = cap.read()

    if not ret:
        print("Video bitti veya okunamadı. Çıkılıyor...")
        # Döngü başa dönsün isterseniz alttaki 2 satırı açın:
        # cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        # continue
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

    # 3. Bilgi Paneli (Sol Üst Köşe)
    box_x, box_y = 0, 0
    draw_transparent_box(frame, box_x, box_y, 330, 175, (0, 0, 0), alpha=0.85)

    # Başlık
    cv2.putText(frame, "BOLGESEL TRAFIK ANALIZI", (box_x + 15, box_y + 25), cv2.FONT_HERSHEY_DUPLEX, 0.6, COLOR_WHITE, 1, cv2.LINE_AA)
    cv2.line(frame, (box_x + 15, box_y + 35), (box_x + 315, box_y + 35), (150, 150, 150), 1, cv2.LINE_AA)

    # Sol Şerit Bilgisi
    line_y_1 = box_y + 65
    cv2.putText(frame, "SOL SERIT", (box_x + 15, line_y_1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_LEFT, 1, cv2.LINE_AA)
    cv2.putText(frame, f"Arac: {instant_left}", (box_x + 130, line_y_1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE, 1, cv2.LINE_AA)
    cv2.putText(frame, status_text_L, (box_x + 230, line_y_1), cv2.FONT_HERSHEY_DUPLEX, 0.7, status_color_L, 2, cv2.LINE_AA)

    # Sağ Şerit Bilgisi
    line_y_2 = box_y + 105
    cv2.putText(frame, "SAG SERIT", (box_x + 15, line_y_2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_RIGHT, 1, cv2.LINE_AA)
    cv2.putText(frame, f"Arac: {instant_right}", (box_x + 130, line_y_2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE, 1, cv2.LINE_AA)
    cv2.putText(frame, status_text_R, (box_x + 230, line_y_2), cv2.FONT_HERSHEY_DUPLEX, 0.7, status_color_R, 2, cv2.LINE_AA)

    # FPS Alt Bilgi
    line_y_3 = box_y + 135
    cv2.line(frame, (box_x + 15, line_y_3), (box_x + 315, line_y_3), (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(frame, f"Sistem FPS: {int(fps)}", (box_x + 15, line_y_3 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)

    # --- EKRANA BASMA (Dinamik Boyutlandırma) ---
    
    # Pencerenin o anki boyutlarını al
    try:
        # Bu fonksiyon pencerenin (x, y, genişlik, yükseklik) değerlerini döner
        _, _, win_w, win_h = cv2.getWindowImageRect(window_name)
        
        # Eğer pencere boyutu mantıklıysa görüntüyü ona "gerdir" (stretch)
        # Bu sayede gri boşluk kalmaz, görüntü pencereye tam oturur.
        if win_w > 0 and win_h > 0:
            show_frame = cv2.resize(frame, (win_w, win_h), interpolation=cv2.INTER_LINEAR)
        else:
            show_frame = frame
    except:
        show_frame = frame

    cv2.imshow(window_name, show_frame)

    # KLAVYE KONTROLLERİ
    key = cv2.waitKey(1) & 0xFF

    # 'q' -> Çıkış
    if key == ord('q'):
        break
    
    # 'f' -> Tam Ekran Aç/Kapat
    elif key == ord('f'):
        # Pencerenin şu anki modunu al
        current_prop = cv2.getWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN)
        
        # Eğer zaten tam ekransa -> Normal moda geç
        if current_prop == cv2.WINDOW_FULLSCREEN:
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        # Değilse -> Tam ekran yap
        else:
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# --- KAPANIŞ ---
cap.release()
cv2.destroyAllWindows()
print("Program sonlandırıldı.")