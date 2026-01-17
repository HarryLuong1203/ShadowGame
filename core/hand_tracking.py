# core/hand_tracking.py
import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    def __init__(self, max_hands=2):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.results = None

    def process(self, frame):
        """Xử lý khung hình để tìm bàn tay"""
        # Chuyển BGR sang RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

    def get_hand_landmarks(self, width, height):
        """
        Trả về danh sách các điểm khớp tay đã quy đổi ra pixel.
        Dùng cho việc tạo vật lý (Physics).
        """
        all_hands_points = []
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                points = {}
                for id, lm in enumerate(hand_lms.landmark):
                    cx, cy = int(lm.x * width), int(lm.y * height)
                    points[id] = (cx, cy)
                all_hands_points.append(points)
        return all_hands_points

    def get_shadow_polygons(self, width, height):
        """
        Trả về danh sách các đa giác (Polygon) bao quanh bàn tay.
        Dùng để VẼ BÓNG (Visual).
        """
        polygons = []
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                # 1. Lấy tất cả tọa độ điểm của 1 bàn tay
                point_list = []
                for lm in hand_lms.landmark:
                    cx, cy = int(lm.x * width), int(lm.y * height)
                    point_list.append([cx, cy])
                
                # 2. Dùng thuật toán Convex Hull để tìm đường bao ngoài cùng
                point_array = np.array(point_list, dtype=np.int32)
                hull = cv2.convexHull(point_array)
                
                # 3. Chuẩn hóa format để Pygame vẽ được
                # hull trả về mảng [[x, y], [x, y]...], ta cần list các điểm
                polygon_points = [pt[0].tolist() for pt in hull]
                polygons.append(polygon_points)
                
        return polygons
