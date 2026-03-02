import cv2
import numpy as np
import time
import threading
from functools import wraps

BELT_WIDTH_MM = 100.0
ROI_WIDTH_MM = 70.0
ROI_HEIGHT_MM = 100.0
CUBE_SIZE_MM = 27.0

COLOR_RANGES = {
    'RED':    [((0, 100, 100), (15, 255, 255)), ((160, 100, 100), (180, 255, 255))],
    'GREEN':  [((40, 100, 100), (70, 255, 255))],
    'BLUE':   [((100, 100, 100), (130, 255, 255))],
    'YELLOW': [((20, 100, 100), (35, 255, 255))]
}

ROI_WINDOW_WIDTH = 400
ROI_WINDOW_HEIGHT = 300

class Cube:
    def __init__(self, color, center_mm, timestamp):
        self.color = color
        self.center_mm = center_mm
        self.timestamp = timestamp
        self.reported = False
        self.global_pos = (0, 0)
        self.area = 0

class ConveyorTracker:
    def __init__(self):
        self.threshold = 60
        self.kernel_size = 5
        self.dilate_iter = 2
        self.erode_iter = 1
        self.ppm = 1.0
        self.active_cubes = {}
        self.cube_id_counter = 0
        self.cube_timeout = 2.0
        self.min_cube_area = 500
        
        self._callbacks = []
        self._tracking = False
        self._tracking_thread = None
        self._cap = None
        self._stop_event = threading.Event()

    def cube_callback(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        self._callbacks.append(func)
        return wrapper

    def _notify_callbacks(self, cube_data):
        for callback in self._callbacks:
            try:
                callback(cube_data)
            except Exception as e:
                print(f"Error in callback {callback.__name__}: {e}")

    def _tracking_loop(self, camera_source, show_windows):
        self._cap = cv2.VideoCapture(camera_source)
        if not self._cap.isOpened():
            print("Ошибка камеры")
            self._tracking = False
            return

        if show_windows:
            cv2.namedWindow("Settings")
            cv2.createTrackbar("Threshold", "Settings", self.threshold, 255, lambda x: None)
            cv2.createTrackbar("Kernel", "Settings", self.kernel_size, 21, lambda x: None)
            cv2.namedWindow("1. Main Camera")
            cv2.namedWindow("2. ROI with Cubes")
            cv2.namedWindow("3. Binary Debug")

        while not self._stop_event.is_set():
            ret, frame = self._cap.read()
            if not ret:
                break
            
            display, roi_view, binary_view = self._process_frame(frame, show_windows)
            
            if show_windows:
                self.threshold = cv2.getTrackbarPos("Threshold", "Settings")
                self.kernel_size = cv2.getTrackbarPos("Kernel", "Settings")
                if self.kernel_size % 2 == 0:
                    self.kernel_size += 1
                    cv2.setTrackbarPos("Kernel", "Settings", self.kernel_size)
                
                cv2.imshow("1. Main Camera", display)
                cv2.imshow("2. ROI with Cubes", roi_view)
                cv2.imshow("3. Binary Debug", binary_view)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

        self._cap.release()
        if show_windows:
            cv2.destroyAllWindows()
        self._tracking = False

    def _process_frame(self, frame, show_windows):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, self.threshold, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
        morph = cv2.dilate(thresh, kernel, iterations=self.dilate_iter)
        morph = cv2.erode(morph, kernel, iterations=self.erode_iter)
        thresh_color = cv2.cvtColor(morph, cv2.COLOR_GRAY2BGR)
        
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        belt_contour = None
        max_area = 0
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 5000 and area > max_area:
                max_area = area
                belt_contour = cnt
        
        display = frame.copy()
        roi_raw = None 
        roi_coords = None

        if belt_contour is not None:
            x, y, w, h = cv2.boundingRect(belt_contour)
            
            if show_windows:
                cv2.drawContours(display, [belt_contour], -1, (0, 255, 0), 2)
                cv2.rectangle(display, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            if h > 0:
                self.ppm = h / BELT_WIDTH_MM
                
                roi_w_px = int(ROI_WIDTH_MM * self.ppm)
                roi_h_px = int(ROI_HEIGHT_MM * self.ppm)
                
                center_x = x + w // 2
                center_y = y + h // 2
                
                roi_x = int(center_x - roi_w_px / 2)
                roi_y = int(center_y - roi_h_px / 2)
                
                h_frame, w_frame = frame.shape[:2]
                roi_x = max(0, roi_x)
                roi_y = max(0, roi_y)
                roi_x2 = min(w_frame, roi_x + roi_w_px)
                roi_y2 = min(h_frame, roi_y + roi_h_px)

                if roi_x2 > roi_x and roi_y2 > roi_y:
                    roi_raw = frame[roi_y:roi_y2, roi_x:roi_x2].copy()
                    roi_coords = (roi_x, roi_y, roi_x2 - roi_x, roi_y2 - roi_y)
                    if show_windows:
                        cv2.rectangle(display, (roi_x, roi_y), (roi_x2, roi_y2), (0, 255, 255), 2)
        
        detected_cubes = []
        if roi_raw is not None and roi_coords is not None:
            hsv_roi = cv2.cvtColor(roi_raw, cv2.COLOR_BGR2HSV)
            combined_mask = np.zeros(roi_raw.shape[:2], dtype=np.uint8)
            cube_masks = {}
            
            for color_name, ranges in COLOR_RANGES.items():
                color_mask = np.zeros(roi_raw.shape[:2], dtype=np.uint8)
                for lower, upper in ranges:
                    l_arr = np.array(lower, dtype=np.uint8)
                    u_arr = np.array(upper, dtype=np.uint8)
                    mask = cv2.inRange(hsv_roi, l_arr, u_arr)
                    color_mask = cv2.bitwise_or(color_mask, mask)
                color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
                cube_masks[color_name] = color_mask
                combined_mask = cv2.bitwise_or(combined_mask, color_mask)
            
            cube_contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            cube_size_px = CUBE_SIZE_MM * self.ppm
            min_cube_area = max(self.min_cube_area, int((cube_size_px * 0.7) ** 2))
            max_cube_area = int((cube_size_px * 1.5) ** 2)
            
            for cnt in cube_contours:
                area = cv2.contourArea(cnt)
                if min_cube_area <= area <= max_cube_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cx_roi = x + w // 2
                    cy_roi = y + h // 2
                    
                    color = None
                    max_pixels = 0
                    for color_name, mask in cube_masks.items():
                        roi_cnt_mask = mask[y:y+h, x:x+w]
                        pixels = cv2.countNonZero(roi_cnt_mask)
                        if pixels > max_pixels and pixels > 20:
                            max_pixels = pixels
                            color = color_name
                    
                    if color:
                        roi_center_x = roi_raw.shape[1] // 2
                        roi_center_y = roi_raw.shape[0] // 2
                        
                        x_mm = (cx_roi - roi_center_x) / self.ppm
                        y_mm = (cy_roi - roi_center_y) / self.ppm
                        
                        global_x = roi_coords[0] + cx_roi
                        global_y = roi_coords[1] + cy_roi
                        
                        detected_cubes.append({
                            'color': color,
                            'x_mm': x_mm,
                            'y_mm': y_mm,
                            'global_pos': (global_x, global_y),
                            'area': area
                        })
                        
                        if show_windows:
                            cv2.rectangle(roi_raw, (x, y), (x + w, y + h), (0, 255, 255), 2)
                            cv2.putText(roi_raw, f"{color}", (x, y - 5), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                            cv2.putText(roi_raw, f"({x_mm:+.1f}, {y_mm:+.1f})", (x, y + h + 15), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

            if show_windows and roi_raw is not None:
                h, w = roi_raw.shape[:2]
                cx, cy = w // 2, h // 2
                cv2.line(roi_raw, (cx, 0), (cx, h), (0, 255, 0), 1)
                cv2.line(roi_raw, (0, cy), (w, cy), (0, 255, 0), 1)
                cv2.putText(roi_raw, "(0,0)", (cx + 5, cy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        if roi_raw is not None:
            roi_view = cv2.resize(roi_raw, (ROI_WINDOW_WIDTH, ROI_WINDOW_HEIGHT), interpolation=cv2.INTER_LINEAR)
        else:
            roi_view = np.zeros((ROI_WINDOW_HEIGHT, ROI_WINDOW_WIDTH, 3), dtype=np.uint8)
            cv2.putText(roi_view, "NO ROI", (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        current_time = time.time()
        reported_cubes = []
        
        for cube in detected_cubes:
            matched = False
            for cube_id, tracked in self.active_cubes.items():
                dist = np.sqrt((cube['global_pos'][0] - tracked.global_pos[0])**2 + 
                              (cube['global_pos'][1] - tracked.global_pos[1])**2)
                if dist < 30:
                    tracked.timestamp = current_time
                    tracked.global_pos = cube['global_pos']
                    if not tracked.reported:
                        tracked.reported = True
                        reported_cubes.append(tracked)
                    matched = True
                    break
            
            if not matched:
                new_id = self.cube_id_counter
                self.cube_id_counter += 1
                new_cube = Cube(cube['color'], (cube['x_mm'], cube['y_mm']), current_time)
                new_cube.global_pos = cube['global_pos']
                new_cube.reported = False
                new_cube.area = cube['area']
                self.active_cubes[new_id] = new_cube
                new_cube.reported = True
                reported_cubes.append(new_cube)
        
        to_remove = [cid for cid, cube in self.active_cubes.items() 
                    if current_time - cube.timestamp > self.cube_timeout]
        for cid in to_remove:
            del self.active_cubes[cid]
        
        for cube in reported_cubes:
            cube_data = {
                'color': cube.color,
                'x_mm': cube.center_mm[0],
                'y_mm': cube.center_mm[1],
                'timestamp': cube.timestamp,
                'area': cube.area,
                'global_pos': cube.global_pos
            }
            self._notify_callbacks(cube_data)

        if show_windows:
            cv2.putText(display, f"Cubes in ROI: {len(detected_cubes)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display, f"Tracked: {len(self.active_cubes)}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display, f"PPM: {self.ppm:.2f}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

        return display, roi_view, thresh_color

    def start(self, camera_source=0, show_windows=True):
        if self._tracking:
            return
        self._tracking = True
        self._stop_event.clear()
        self._tracking_thread = threading.Thread(target=self._tracking_loop, args=(camera_source, show_windows))
        self._tracking_thread.daemon = True
        self._tracking_thread.start()

    def stop(self):
        if not self._tracking:
            return
        self._stop_event.set()
        if self._tracking_thread:
            self._tracking_thread.join(timeout=2.0)
        self._tracking = False

    def is_running(self):
        return self._tracking

# псевдо-singlethon
tracker = ConveyorTracker()
