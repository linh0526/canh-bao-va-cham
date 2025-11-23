"""
Module ước lượng khoảng cách vật cản
"""

from config.config import FOCAL_LENGTH, REAL_HEIGHTS, SAFE_DISTANCE, WARNING_DISTANCE, CAUTION_DISTANCE


class DistanceModule:
    """Module tính toán khoảng cách và đánh giá mức độ nguy hiểm"""
    
    def __init__(self):
        """Khởi tạo distance module"""
        self.focal_length = FOCAL_LENGTH
        self.real_heights = REAL_HEIGHTS
        self.safe_distance = SAFE_DISTANCE
        self.warning_distance = WARNING_DISTANCE
        self.caution_distance = CAUTION_DISTANCE
    
    def calculate_distance(self, pixel_height, object_class):
        """
        Tính khoảng cách đến vật cản
        
        Args:
            pixel_height: Chiều cao của bounding box trên ảnh (pixel)
            object_class: Loại vật thể (person, car, truck, ...)
            
        Returns:
            float: Khoảng cách tính bằng mét, hoặc None nếu không xác định được
        """
        if pixel_height <= 0:
            return None
        
        if object_class not in self.real_heights:
            return None
        
        real_height = self.real_heights[object_class]
        distance = (real_height * self.focal_length) / pixel_height
        
        return distance
    
    def assess_risk_level(self, distance):
        """
        Đánh giá mức độ nguy hiểm dựa trên khoảng cách
        
        Args:
            distance: Khoảng cách đến vật cản (mét)
            
        Returns:
            dict: Thông tin mức độ nguy hiểm với keys:
                 - 'level': 'safe', 'caution', 'warning', 'danger'
                 - 'color': Màu sắc cảnh báo (BGR)
                 - 'needs_alert': Có cần cảnh báo không
        """
        if distance is None:
            return {
                'level': 'unknown',
                'color': (128, 128, 128),
                'needs_alert': False
            }
        
        if distance <= self.safe_distance:
            return {
                'level': 'danger',
                'color': (0, 0, 255),  # Đỏ
                'needs_alert': True,
                'priority': 3
            }
        elif distance <= self.warning_distance:
            return {
                'level': 'warning',
                'color': (0, 255, 255),  # Vàng
                'needs_alert': True,
                'priority': 2
            }
        elif distance <= self.caution_distance:
            return {
                'level': 'caution',
                'color': (0, 165, 255),  # Cam
                'needs_alert': False,
                'priority': 1
            }
        else:
            return {
                'level': 'safe',
                'color': (0, 255, 0),  # Xanh lá
                'needs_alert': False,
                'priority': 0
            }
    
    def process_detections(self, detections):
        """
        Xử lý danh sách phát hiện và tính khoảng cách cho mỗi vật thể
        
        Args:
            detections: Danh sách các vật thể được phát hiện
            
        Returns:
            list: Danh sách vật thể đã được tính khoảng cách và đánh giá rủi ro
        """
        processed = []
        
        for detection in detections:
            distance = self.calculate_distance(
                detection['pixel_height'],
                detection['class']
            )
            
            risk_assessment = self.assess_risk_level(distance)
            
            processed_detection = {
                **detection,
                'distance': distance,
                'risk': risk_assessment
            }
            
            processed.append(processed_detection)
        
        return processed
    
    def has_collision_risk(self, processed_detections):
        """
        Kiểm tra xem có nguy cơ va chạm không
        
        Args:
            processed_detections: Danh sách vật thể đã được xử lý
            
        Returns:
            bool: True nếu có nguy cơ va chạm
        """
        for detection in processed_detections:
            if detection['risk']['needs_alert']:
                return True
        return False
    
    def get_closest_object(self, processed_detections):
        """
        Lấy vật thể gần nhất có nguy cơ va chạm
        
        Args:
            processed_detections: Danh sách vật thể đã được xử lý
            
        Returns:
            dict: Vật thể gần nhất hoặc None
        """
        dangerous_objects = [
            d for d in processed_detections 
            if d['risk']['needs_alert'] and d['distance'] is not None
        ]
        
        if not dangerous_objects:
            return None
        
        return min(dangerous_objects, key=lambda x: x['distance'])

