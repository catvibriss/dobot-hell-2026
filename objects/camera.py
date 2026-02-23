import cv2
import numpy as np
import time
from pprint import pprint

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

DEFAULT_THRESHOLD = 60
DEFAULT_KERNEL = 5
DEFAULT_DILATE = 2
DEFAULT_ERODE = 1

ROI_WINDOW_WIDTH = 400
ROI_WINDOW_HEIGHT = 300

def on_cube_detected(cube_data):
    pprint(cube_data)

class Cube:
    def __init__(self, color, center_mm, timestamp):
        self.color = color
        self.center_mm = center_mm
        self.timestamp = timestamp
        self.reported = False
        self.global_pos = (0, 0)
        self.area = 0

class ConveyorTracker:
    def __init__(self, cube_callback=None):
        self.threshold = DEFAULT_THRESHOLD
        self.kernel_size = DEFAULT_KERNEL
        self.dilate_iter = DEFAULT_DILATE
        self.erode_iter = DEFAULT_ERODE
        self.window_created = False
        self.ppm = 1.0
        self.active_cubes = {}
        self.cube_id_counter = 0
        self.cube_timeout = 2.0
        self.min_cube_area = 500
        self.cube_callback = cube_callback

    def create_windows(self):
        cv2.namedWindow("Settings")
        cv2.createTrackbar("Threshold", "Settings", self.threshold, 255, self.nothing)
        cv2.createTrackbar("Kernel", "Settings", self.kernel_size, 21, self.nothing)
        cv2.createTrackbar("Dilate", "Settings", self.dilate_iter, 10, self.nothing)
        cv2.createTrackbar("Erode", "Settings", self.erode_iter, 10, self.nothing)
        cv2.createTrackbar("Min Cube Area", "Settings", self.min_cube_area, 5000, self.nothing)
        self.window_created = True

    def nothing(self, x):
        pass

    def get_settings(self):
        self.threshold = cv2.getTrackbarPos("Threshold", "Settings")
        self.kernel_size = cv2.getTrackbarPos("Kernel", "Settings")
        self.dilate_iter = cv2.getTrackbarPos("Dilate", "Settings")
        self.erode_iter = cv2.getTrackbarPos("Erode", "Settings")
        self.min_cube_area = cv2.getTrackbarPos("Min Cube Area", "Settings")
        
        if self.kernel_size % 2 == 0:
            self.kernel_size += 1
            cv2.setTrackbarPos("Kernel", "Settings", self.kernel_size)

    def create_blank_roi(self):
        blank = np.zeros((ROI_WINDOW_HEIGHT, ROI_WINDOW_WIDTH, 3), dtype=np.uint8)
        cv2.putText(blank, "NO SIGNAL", (120, 140), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(blank, "Adjust threshold", (100, 170), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
        return blank

    def draw_coordinates(self, image):
        if image is None or image.size == 0:
            return self.create_blank_roi()
        h, w = image.shape[:2]
        if h == 0 or w == 0:
            return self.create_blank_roi()

        cx, cy = w // 2, h // 2
        color = (0, 255, 0)
        
        cv2.line(image, (cx, 0), (cx, h), color, 1)
        cv2.line(image, (0, cy), (w, cy), color, 1)
        
        cv2.putText(image, "Y:-50", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        cv2.putText(image, "Y:+50", (5, h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        cv2.putText(image, "X:-35", (5, cy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        cv2.putText(image, "X:+35", (w - 50, cy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        cv2.putText(image, "(0,0)", (cx + 5, cy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        return image

    def scale_to_roi_window(self, image):
        if image is None or image.size == 0:
            return self.create_blank_roi()
        h, w = image.shape[:2]
        if h == 0 or w == 0:
            return self.create_blank_roi()
        
        scale = min(ROI_WINDOW_WIDTH / w, ROI_WINDOW_HEIGHT / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        scaled = np.zeros((ROI_WINDOW_HEIGHT, ROI_WINDOW_WIDTH, 3), dtype=np.uint8)
        offset_x = (ROI_WINDOW_WIDTH - new_w) // 2
        offset_y = (ROI_WINDOW_HEIGHT - new_h) // 2
        
        scaled[offset_y:offset_y+new_h, offset_x:offset_x+new_w] = resized
        return scaled

    def process_frame(self, frame):
        self.get_settings()
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
                            'area': area,
                            'contour': cnt
                        })
                        
                        cv2.rectangle(roi_raw, (x, y), (x + w, y + h), (0, 255, 255), 2)
                        cv2.putText(roi_raw, f"{color}", (x, y - 5), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                        cv2.putText(roi_raw, f"({x_mm:+.1f}, {y_mm:+.1f})", (x, y + h + 15), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
            
            roi_raw = self.draw_coordinates(roi_raw)
       
        roi_view = self.scale_to_roi_window(roi_raw)
        
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
            
            if self.cube_callback is not None:
                self.cube_callback(cube_data)
            
            print(f"[CUBE DETECTED] Color: {cube.color:6s}")
        
        cv2.putText(display, f"Cubes in ROI: {len(detected_cubes)}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display, f"Tracked: {len(self.active_cubes)}", (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return display, roi_view, thresh_color

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Ошибка камеры")
            return

        self.create_windows()

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            main_view, roi_view, binary_view = self.process_frame(frame)
            
            if main_view is not None and main_view.size > 0:
                cv2.imshow("1. Main Camera", main_view)
            if roi_view is not None and roi_view.size > 0:
                cv2.imshow("2. ROI with Cubes", roi_view)
            if binary_view is not None and binary_view.size > 0:
                cv2.imshow("3. Binary Debug", binary_view)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tracker = ConveyorTracker(cube_callback=on_cube_detected)
    tracker.run()