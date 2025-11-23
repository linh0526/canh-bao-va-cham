"""
Module phát hiện chuyển động để xác định khi xe đang dừng
"""

import numpy as np
from collections import deque


class MotionDetectionModule:
    """Module phát hiện chuyển động của vật thể"""
    
    def __init__(self, history_size=10, movement_threshold=0.02):
        """
        Khởi tạo motion detection module
        
        Args:
            history_size: Số lượng khung hình lưu lại để phân tích
            movement_threshold: Ngưỡng chuyển động (tỷ lệ di chuyển so với kích thước frame)
        """
        self.history_size = history_size
        self.movement_threshold = movement_threshold
        self.object_history = {}  # Lưu lịch sử vị trí của các vật thể
        self.frame_width = None
        self.frame_height = None
    
    def update_frame_size(self, width, height):
        """Cập nhật kích thước khung hình"""
        self.frame_width = width
        self.frame_height = height
    
    def calculate_center(self, bbox):
        """
        Tính tâm của bounding box
        
        Args:
            bbox: (x1, y1, x2, y2)
            
        Returns:
            tuple: (center_x, center_y)
        """
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def calculate_movement(self, detections):
        """
        Tính toán chuyển động của các vật thể
        
        Args:
            detections: Danh sách vật thể được phát hiện
            
        Returns:
            dict: Thông tin chuyển động cho mỗi vật thể
        """
        if self.frame_width is None or self.frame_height is None:
            return {}
        
        movement_info = {}
        frame_size = max(self.frame_width, self.frame_height)
        
        for detection in detections:
            # Tạo ID duy nhất cho vật thể dựa trên vị trí và loại
            bbox = detection['bbox']
            center = self.calculate_center(bbox)
            obj_id = f"{detection['class']}_{int(center[0]//50)}_{int(center[1]//50)}"
            
            # Lưu lịch sử
            if obj_id not in self.object_history:
                self.object_history[obj_id] = deque(maxlen=self.history_size)
            
            self.object_history[obj_id].append({
                'center': center,
                'bbox': bbox,
                'distance': detection.get('distance')
            })
            
            # Tính chuyển động nếu có đủ lịch sử
            if len(self.object_history[obj_id]) >= 3:
                centers = [h['center'] for h in list(self.object_history[obj_id])[-5:]]
                
                # Tính tổng khoảng cách di chuyển
                total_movement = 0
                for i in range(1, len(centers)):
                    dx = centers[i][0] - centers[i-1][0]
                    dy = centers[i][1] - centers[i-1][1]
                    movement = np.sqrt(dx*dx + dy*dy)
                    total_movement += movement
                
                # Chuẩn hóa theo kích thước frame
                normalized_movement = total_movement / frame_size
                
                # Xác định vật thể có đang di chuyển không
                is_moving = normalized_movement > self.movement_threshold
                
                movement_info[obj_id] = {
                    'is_moving': is_moving,
                    'movement': normalized_movement,
                    'center': center
                }
            else:
                movement_info[obj_id] = {
                    'is_moving': True,  # Mặc định coi là đang di chuyển nếu chưa đủ dữ liệu
                    'movement': 0,
                    'center': center
                }
        
        # Xóa lịch sử của các vật thể không còn xuất hiện
        active_ids = set(movement_info.keys())
        self.object_history = {k: v for k, v in self.object_history.items() if k in active_ids}
        
        return movement_info
    
    def is_vehicle_stopped(self, detections, movement_info):
        """
        Xác định xe có đang dừng không dựa trên chuyển động
        
        Args:
            detections: Danh sách vật thể
            movement_info: Thông tin chuyển động
            
        Returns:
            bool: True nếu xe có vẻ đang dừng
        """
        if not movement_info:
            return False
        
        # Đếm số vật thể không di chuyển
        stationary_objects = sum(1 for info in movement_info.values() if not info['is_moving'])
        total_objects = len(movement_info)
        
        # Kiểm tra chuyển động trung bình
        if total_objects > 0:
            avg_movement = sum(info['movement'] for info in movement_info.values()) / total_objects
            stationary_ratio = stationary_objects / total_objects
            
            # Điều kiện xe dừng: 
            # 1. Phần lớn vật thể không di chuyển (≥70%)
            # 2. VÀ chuyển động trung bình rất thấp (<0.01)
            if stationary_ratio >= 0.7 and avg_movement < 0.01:
                return True
            
            # Nếu có ít nhất 3 vật thể và tất cả đều không di chuyển
            if total_objects >= 3 and stationary_ratio >= 0.9:
                return True
        
        return False
    
    def clear_history(self):
        """Xóa lịch sử chuyển động"""
        self.object_history.clear()

