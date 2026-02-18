import cv2
import numpy as np
import time
from collections import deque

# ==============================================================================
# НАСТРОЙКИ
# ==============================================================================

CAMERA_INDEX = 1              # Индекс веб-камеры
CONVEYOR_WIDTH_MM = 100.0     # Ширина ленты конвейера в мм

MIN_CUBE_AREA = 800           # Минимальная площадь кубика в пикселях
MAX_TRACK_DISTANCE = 40       # Максимальное расстояние для трека (пиксели)
TRACK_TIMEOUT = 3.0           # Время жизни трека без обновлений (сек)
QUEUE_MAX_SIZE = 50           # Максимум записей в очереди

# Базовые диапазоны HSV (будут переопределены трекбарами)
COLOR_BASE_RANGES = {
    'Red':    ([0, 70, 50], [15, 255, 255]),
    'Green':  ([40, 70, 50], [80, 255, 255]),
    'Blue':   ([100, 70, 50], [130, 255, 255]),
    'Yellow': ([20, 70, 50], [35, 255, 255])
}

COLOR_BOXES = {
    'Red': (0, 0, 255),
    'Green': (0, 255, 0),
    'Blue': (255, 0, 0),
    'Yellow': (0, 255, 255)
}

# ==============================================================================
# КЛАССЫ
# ==============================================================================

class TrackedCube:
    def __init__(self, track_id, color, center_x, center_y, deviation_mm):
        self.id = track_id
        self.color = color
        self.center_x = center_x
        self.center_y = center_y
        self.deviation_mm = deviation_mm
        self.frames_seen = 1
        self.last_seen = time.time()
        self.counted = False
        self.start_x = center_x  # Для отслеживания движения

class CubeQueue:
    def __init__(self, max_size=50):
        self.queue = deque(maxlen=max_size)
        self.next_track_id = 1
        self.tracked_cubes = {}
        self.counting_enabled = True
        self.total_counted = 0
    
    def toggle_counting(self):
        self.counting_enabled = not self.counting_enabled
        return self.counting_enabled
    
    def update_tracks(self, detections, conveyor_rect, scale_px_per_mm, center_y):
        current_time = time.time()
        matched_ids = set()
        
        for det in detections:
            best_match_id = None
            best_distance = float('inf')
            
            for track_id, track in self.tracked_cubes.items():
                if track.color != det['color']:
                    continue
                
                distance = np.sqrt(
                    (track.center_x - det['center_x'])**2 + 
                    (track.center_y - det['center_y'])**2
                )
                
                if distance < best_distance and distance < MAX_TRACK_DISTANCE:
                    best_distance = distance
                    best_match_id = track_id
            
            if best_match_id is not None:
                track = self.tracked_cubes[best_match_id]
                track.center_x = det['center_x']
                track.center_y = det['center_y']
                track.frames_seen += 1
                track.last_seen = current_time
                
                # Считаем только если: включен счётчик + трек новый + достаточно кадров
                if not track.counted and self.counting_enabled and track.frames_seen >= 3:
                    self.queue.append({
                        'id': track.id,
                        'color': track.color,
                        'deviation_mm': track.deviation_mm,
                        'timestamp': time.strftime("%H:%M:%S", time.localtime())
                    })
                    track.counted = True
                    self.total_counted += 1
                    print(f"[{track.last_seen:.0f}] ✅ Кубик #{track.id}: {track.color}, Отклонение: {track.deviation_mm:+.1f} мм")
                
                matched_ids.add(best_match_id)
            else:
                track_id = self.next_track_id
                self.next_track_id += 1
                
                deviation_mm = 0.0
                if scale_px_per_mm > 0 and conveyor_rect:
                    offset_px = center_y - det['center_y']
                    deviation_mm = offset_px / scale_px_per_mm
                
                new_track = TrackedCube(track_id, det['color'], det['center_x'], det['center_y'], deviation_mm)
                self.tracked_cubes[track_id] = new_track
        
        # Удаляем старые треки
        stale_ids = [tid for tid, tr in self.tracked_cubes.items() 
                     if current_time - tr.last_seen > TRACK_TIMEOUT]
        for track_id in stale_ids:
            del self.tracked_cubes[track_id]
    
    def get_active_count(self):
        return len(self.tracked_cubes)
    
    def get_queue_count(self):
        return len(self.queue)

def nothing(x):
    pass

def create_color_masks_grid(masks_dict, cell_size=(160, 120)):
    colors = list(COLOR_BASE_RANGES.keys())
    grid_h, grid_w = cell_size[0] * 2, cell_size[1] * 2
    grid = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)
    
    for i, color_name in enumerate(colors):
        row = i // 2
        col = i % 2
        x_off = col * cell_size[1]
        y_off = row * cell_size[0]
        
        mask = masks_dict.get(color_name, np.zeros(cell_size, dtype=np.uint8))
        mask_resized = cv2.resize(mask, (cell_size[1], cell_size[0]))
        mask_color = cv2.cvtColor(mask_resized, cv2.COLOR_GRAY2BGR)
        
        cv2.putText(mask_color, color_name, (5, 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        grid[y_off:y_off+cell_size[0], x_off:x_off+cell_size[1]] = mask_color
    
    return grid

# ==============================================================================
# ОСНОВНАЯ ПРОГРАММА
# ==============================================================================

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        print(f"Ошибка: Не удалось открыть камеру {CAMERA_INDEX}")
        return

    # Окна (все можно ресайзить мышкой)
    cv2.namedWindow("Live Feed", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Debug Masks", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
    
    cv2.resizeWindow("Live Feed", 640, 480)
    cv2.resizeWindow("Debug Masks", 320, 240)
    cv2.resizeWindow("Calibration", 350, 400)

    # Трекбары для конвейера
    cv2.createTrackbar("Conv Threshold", "Calibration", 60, 255, nothing)
    
    # Трекбары для КАЖДОГО цвета отдельно (особенно важно для красного!)
    for color_name in COLOR_BASE_RANGES.keys():
        cv2.createTrackbar(f"{color_name} H-Min", "Calibration", COLOR_BASE_RANGES[color_name][0][0], 180, nothing)
        cv2.createTrackbar(f"{color_name} H-Max", "Calibration", COLOR_BASE_RANGES[color_name][1][0], 180, nothing)
        cv2.createTrackbar(f"{color_name} S-Min", "Calibration", COLOR_BASE_RANGES[color_name][0][1], 255, nothing)
        cv2.createTrackbar(f"{color_name} V-Min", "Calibration", COLOR_BASE_RANGES[color_name][0][2], 255, nothing)
    
    cv2.createTrackbar("Min Area", "Calibration", 800, 5000, nothing)

    cube_queue = CubeQueue(max_size=QUEUE_MAX_SIZE)
    kernel = np.ones((5, 5), np.uint8)

    print("=" * 60)
    print("СИСТЕМА ЗАПУЩЕНА")
    print("=" * 60)
    print(f"Камера: {CAMERA_INDEX} | Ширина ленты: {CONVEYOR_WIDTH_MM} мм")
    print("Управление:")
    print("  [SPACE] - Старт/Стоп счётчика")
    print("  [Q]     - Выход")
    print("  [R]     - Сброс счётчика")
    print("=" * 60)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # --- 1. КОНВЕЙЕР ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh_val = cv2.getTrackbarPos("Conv Threshold", "Calibration")
        _, mask_conv = cv2.threshold(blurred, thresh_val, 255, cv2.THRESH_BINARY_INV)
        mask_conv = cv2.morphologyEx(mask_conv, cv2.MORPH_CLOSE, kernel)
        mask_conv = cv2.morphologyEx(mask_conv, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(mask_conv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        output_frame = frame.copy()
        
        conveyor_rect = None
        scale_px_per_mm = 0.0
        center_x, center_y = 0, 0
        conveyor_width_px = 0

        if contours:
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            
            if w > h and h > 20: 
                conveyor_rect = (x, y, w, h)
                conveyor_width_px = h  # Высота прямоугольника = ширина ленты
                scale_px_per_mm = h / CONVEYOR_WIDTH_MM
                center_x = int(x + w / 2)
                center_y = int(y + h / 2)
                
                cv2.rectangle(output_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.line(output_frame, (center_x, y), (center_x, y + h), (255, 0, 0), 2)
                
                # Шкала мм
                step_mm = 10.0 
                half_width = CONVEYOR_WIDTH_MM / 2.0
                current_mm = -half_width
                while current_mm <= half_width:
                    offset_px = int(current_mm * scale_px_per_mm)
                    pos_y = center_y - offset_px
                    tick_len = 10 if abs(current_mm) < 0.1 else 5
                    cv2.line(output_frame, (center_x - tick_len, pos_y), 
                             (center_x + tick_len, pos_y), (0, 255, 255), 1)
                    label = "0" if abs(current_mm) < 0.1 else f"{int(current_mm)}"
                    cv2.putText(output_frame, label, (center_x + 15, pos_y + 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                    current_mm += step_mm

        # --- 2. КУБИКИ ---
        MIN_CUBE_AREA = cv2.getTrackbarPos("Min Area", "Calibration")
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        detections = []
        color_masks = {}

        for color_name in COLOR_BASE_RANGES.keys():
            # Читаем трекбары для каждого цвета
            h_min = cv2.getTrackbarPos(f"{color_name} H-Min", "Calibration")
            h_max = cv2.getTrackbarPos(f"{color_name} H-Max", "Calibration")
            s_min = cv2.getTrackbarPos(f"{color_name} S-Min", "Calibration")
            v_min = cv2.getTrackbarPos(f"{color_name} V-Min", "Calibration")
            
            # Для красного цвета: если H-Max < H-Min, значит диапазон переходит через 0
            if color_name == 'Red' and h_max < h_min:
                # Два диапазона для красного (0-10 и 170-180)
                lower1 = np.array([0, s_min, v_min], dtype=np.uint8)
                upper1 = np.array([h_max, 255, 255], dtype=np.uint8)
                lower2 = np.array([h_min, s_min, v_min], dtype=np.uint8)
                upper2 = np.array([180, 255, 255], dtype=np.uint8)
                
                mask1 = cv2.inRange(hsv, lower1, upper1)
                mask2 = cv2.inRange(hsv, lower2, upper2)
                mask_color = cv2.bitwise_or(mask1, mask2)
            else:
                dynamic_lower = np.array([h_min, s_min, v_min], dtype=np.uint8)
                dynamic_upper = np.array([h_max, 255, 255], dtype=np.uint8)
                mask_color = cv2.inRange(hsv, dynamic_lower, dynamic_upper)
            
            mask_color = cv2.morphologyEx(mask_color, cv2.MORPH_OPEN, kernel)
            mask_color = cv2.morphologyEx(mask_color, cv2.MORPH_CLOSE, kernel)
            color_masks[color_name] = mask_color
            
            cnts, _ = cv2.findContours(mask_color, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in cnts:
                area = cv2.contourArea(cnt)
                if area > MIN_CUBE_AREA: 
                    x, y, w, h = cv2.boundingRect(cnt)
                    cube_center_x = x + w // 2
                    cube_center_y = y + h // 2
                    
                    on_conveyor = False
                    if conveyor_rect:
                        cx, cy, cw, ch = conveyor_rect
                        if cy - 10 <= cube_center_y <= cy + ch + 10:
                            on_conveyor = True
                    
                    if not on_conveyor:
                        continue
                    
                    # Расчет отклонения
                    deviation_mm = 0.0
                    if scale_px_per_mm > 0:
                        offset_px = center_y - cube_center_y
                        deviation_mm = offset_px / scale_px_per_mm
                    
                    detections.append({
                        'color': color_name,
                        'center_x': cube_center_x,
                        'center_y': cube_center_y,
                        'area': area,
                        'rect': (x, y, w, h),
                        'deviation_mm': deviation_mm
                    })

        # Обновляем треки
        cube_queue.update_tracks(detections, conveyor_rect, scale_px_per_mm, center_y)
        
        # Отрисовка треков
        for track_id, track in cube_queue.tracked_cubes.items():
            box_color = COLOR_BOXES.get(track.color, (255, 255, 255))
            for det in detections:
                if det['color'] == track.color:
                    dist = np.sqrt((track.center_x - det['center_x'])**2 + 
                                   (track.center_y - det['center_y'])**2)
                    if dist < MAX_TRACK_DISTANCE:
                        x, y, w, h = det['rect']
                        cv2.rectangle(output_frame, (x, y), (x + w, y + h), box_color, 2)
                        status = "✓" if track.counted else "..."
                        count_status = "ON" if cube_queue.counting_enabled else "OFF"
                        label = f"#{track.id}{status} [{count_status}]"
                        cv2.putText(output_frame, label, (x, y - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)
                        break

        # --- 3. ИНТЕРФЕЙС ---
        status_color = (0, 255, 0) if cube_queue.counting_enabled else (0, 0, 255)
        status_text = "COUNTING: ON" if cube_queue.counting_enabled else "COUNTING: OFF"
        cv2.putText(output_frame, status_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(output_frame, f"Total: {cube_queue.total_counted}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(output_frame, f"Active: {cube_queue.get_active_count()}", (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Отладка конвейера
        debug_info = [
            f"Conv Width: {conveyor_width_px} px",
            f"Scale: {scale_px_per_mm:.2f} px/mm",
            f"Center Y: {center_y}",
            f"Threshold: {thresh_val}"
        ]
        for i, info in enumerate(debug_info):
            cv2.putText(output_frame, info, (10, 120 + i*25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        masks_grid = create_color_masks_grid(color_masks)
        
        # Окно калибровки с информацией
        calib_frame = np.zeros((400, 350, 3), dtype=np.uint8)
        calib_text = [
            f"CONVEYOR CALIBRATION",
            f"Width (px): {conveyor_width_px}",
            f"Scale: {scale_px_per_mm:.2f} px/mm",
            f"Center Y: {center_y}",
            f"",
            f"COUNTING: {'ON' if cube_queue.counting_enabled else 'OFF'}",
            f"Total Counted: {cube_queue.total_counted}",
            f"",
            f"CONTROLS:",
            f"[SPACE] Toggle",
            f"[R] Reset",
            f"[Q] Quit"
        ]
        for i, text in enumerate(calib_text):
            color = (0, 255, 0) if "ON" in text else (255, 255, 255)
            cv2.putText(calib_frame, text, (10, 30 + i*25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        cv2.imshow("Calibration", calib_frame)
        cv2.imshow("Debug Masks", masks_grid)
        cv2.imshow("Live Feed", output_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            state = cube_queue.toggle_counting()
            print(f"\n{'✅ СЧЁТЧИК ВКЛЮЧЕН' if state else '❌ СЧЁТЧИК ОТКЛЮЧЕН'}\n")
        elif key == ord('r'):
            cube_queue.queue.clear()
            cube_queue.tracked_cubes.clear()
            cube_queue.total_counted = 0
            cube_queue.next_track_id = 1
            print("\n🔄 СЧЁТЧИК СБРОШЕН\n")

    print(f"\nВсего кубиков: {cube_queue.total_counted}")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()