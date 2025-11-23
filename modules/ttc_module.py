"""
Module tính toán Time-to-Collision (TTC) và khoảng cách dừng an toàn
"""

import numpy as np
from collections import deque


class TTCModule:
    """Module tính toán TTC và khoảng cách dừng an toàn"""
    
    def __init__(self, reaction_time=1.2, deceleration=6.0):
        """
        Khởi tạo TTC module
        
        Args:
            reaction_time: Thời gian phản ứng của tài xế (giây), mặc định 1.2s
            deceleration: Gia tốc hãm (m/s²), mặc định 6.0 m/s² (~0.6g)
        """
        self.reaction_time = reaction_time
        self.deceleration = deceleration
        self.distance_history = {}  # Lưu lịch sử khoảng cách để tính vận tốc
        self.history_size = 5
    
    def calculate_stopping_distance(self, velocity_ms):
        """
        Tính khoảng cách dừng an toàn
        
        Args:
            velocity_ms: Vận tốc hiện tại (m/s)
            
        Returns:
            float: Khoảng cách dừng cần thiết (mét)
        """
        # d = v*t + v²/(2*a)
        reaction_distance = velocity_ms * self.reaction_time
        braking_distance = (velocity_ms ** 2) / (2 * self.deceleration)
        stopping_distance = reaction_distance + braking_distance
        
        return stopping_distance
    
    def estimate_relative_velocity(self, object_id, current_distance, current_time):
        """
        Ước lượng vận tốc tương đối dựa trên thay đổi khoảng cách
        
        Args:
            object_id: ID của vật thể
            current_distance: Khoảng cách hiện tại (mét)
            current_time: Thời gian hiện tại (giây)
            
        Returns:
            float: Vận tốc tương đối (m/s), dương nếu đang tiến gần
        """
        if object_id not in self.distance_history:
            self.distance_history[object_id] = deque(maxlen=self.history_size)
        
        self.distance_history[object_id].append({
            'distance': current_distance,
            'time': current_time
        })
        
        history = list(self.distance_history[object_id])
        
        if len(history) < 2:
            return 0.0  # Chưa đủ dữ liệu
        
        # Tính vận tốc trung bình từ 2 điểm gần nhất
        if len(history) >= 2:
            dt = history[-1]['time'] - history[-2]['time']
            if dt > 0:
                dd = history[-1]['distance'] - history[-2]['distance']
                velocity = -dd / dt  # Dương nếu đang tiến gần (khoảng cách giảm)
                return velocity
        
        return 0.0
    
    def calculate_ttc(self, distance, relative_velocity):
        """
        Tính Time-to-Collision (TTC)
        
        Args:
            distance: Khoảng cách hiện tại (mét)
            relative_velocity: Vận tốc tương đối (m/s), dương nếu đang tiến gần
            
        Returns:
            float: TTC (giây), hoặc None nếu không thể tính (vận tốc <= 0)
        """
        if relative_velocity <= 0:
            return None  # Không có nguy cơ va chạm (đang xa ra hoặc đứng yên)
        
        if distance <= 0:
            return 0.0  # Đã va chạm
        
        ttc = distance / relative_velocity
        return ttc
    
    def assess_risk_with_ttc(self, distance, relative_velocity, current_velocity_ms=None):
        """
        Đánh giá mức độ nguy hiểm kết hợp khoảng cách và TTC
        
        Args:
            distance: Khoảng cách hiện tại (mét)
            relative_velocity: Vận tốc tương đối (m/s), dương nếu đang tiến gần
            current_velocity_ms: Vận tốc hiện tại của xe (m/s), nếu có
            
        Returns:
            dict: Thông tin đánh giá rủi ro với keys:
                 - 'level': 'safe', 'caution', 'warning', 'danger'
                 - 'color': Màu sắc cảnh báo (BGR)
                 - 'needs_alert': Có cần cảnh báo không
                 - 'ttc': Time-to-Collision (giây)
                 - 'stopping_distance': Khoảng cách dừng cần thiết (mét)
        """
        """
        Đánh giá mức độ nguy hiểm kết hợp khoảng cách và TTC
        
        Args:
            distance: Khoảng cách hiện tại (mét)
            relative_velocity: Vận tốc tương đối (m/s)
            current_velocity_ms: Vận tốc hiện tại của xe (m/s), nếu có
            
        Returns:
            dict: Thông tin đánh giá rủi ro với keys:
                 - 'level': 'safe', 'caution', 'warning', 'danger'
                 - 'color': Màu sắc cảnh báo (BGR)
                 - 'needs_alert': Có cần cảnh báo không
                 - 'ttc': Time-to-Collision (giây)
                 - 'stopping_distance': Khoảng cách dừng cần thiết (mét)
        """
        # Tính TTC
        ttc = self.calculate_ttc(distance, relative_velocity)
        
        # Tính khoảng cách dừng nếu có vận tốc
        stopping_distance = None
        if current_velocity_ms is not None and current_velocity_ms > 0:
            stopping_distance = self.calculate_stopping_distance(current_velocity_ms)
        
        # Đánh giá dựa trên TTC và khoảng cách, kết hợp với vận tốc
        # Nếu vận tốc tương đối thấp và khoảng cách xa, không nên báo nguy hiểm
        is_slow_approach = relative_velocity < 1.0  # Vận tốc tương đối < 1 m/s
        
        if ttc is not None:
            # Ưu tiên TTC nếu có
            # Nếu TTC thấp VÀ vận tốc đáng kể → nguy hiểm
            if ttc <= 2.0 and not is_slow_approach:  # ≤ 2 giây và không phải tiếp cận chậm
                return {
                    'level': 'danger',
                    'color': (0, 0, 255),  # Đỏ
                    'needs_alert': True,
                    'priority': 3,
                    'ttc': ttc,
                    'stopping_distance': stopping_distance
                }
            elif ttc <= 2.0 and is_slow_approach and distance <= 5.0:
                # TTC thấp nhưng tiếp cận chậm, chỉ báo đỏ nếu rất gần
                return {
                    'level': 'danger',
                    'color': (0, 0, 255),  # Đỏ
                    'needs_alert': True,
                    'priority': 3,
                    'ttc': ttc,
                    'stopping_distance': stopping_distance
                }
            elif ttc <= 4.0 and not is_slow_approach:  # 2-4 giây và không phải tiếp cận chậm
                return {
                    'level': 'warning',
                    'color': (0, 255, 255),  # Vàng
                    'needs_alert': True,
                    'priority': 2,
                    'ttc': ttc,
                    'stopping_distance': stopping_distance
                }
            elif ttc <= 6.0:  # 4-6 giây
                return {
                    'level': 'caution',
                    'color': (0, 165, 255),  # Cam
                    'needs_alert': False,
                    'priority': 1,
                    'ttc': ttc,
                    'stopping_distance': stopping_distance
                }
        
        # Nếu không có TTC, đánh giá dựa trên khoảng cách và vận tốc
        # Khi xe chạy chậm, chỉ báo đỏ khi rất gần
        if distance <= 5.0:  # Rất gần, luôn báo đỏ
            return {
                'level': 'danger',
                'color': (0, 0, 255),  # Đỏ
                'needs_alert': True,
                'priority': 3,
                'ttc': ttc,
                'stopping_distance': stopping_distance
            }
        elif distance <= 8.0 and not is_slow_approach:  # Gần và không chạy chậm
            return {
                'level': 'danger',
                'color': (0, 0, 255),  # Đỏ
                'needs_alert': True,
                'priority': 3,
                'ttc': ttc,
                'stopping_distance': stopping_distance
            }
        elif distance <= 8.0 and is_slow_approach:  # Gần nhưng chạy chậm → chỉ cảnh báo
            return {
                'level': 'warning',
                'color': (0, 255, 255),  # Vàng
                'needs_alert': True,
                'priority': 2,
                'ttc': ttc,
                'stopping_distance': stopping_distance
            }
        elif distance <= 15.0 and not is_slow_approach:  # Trung bình và không chạy chậm
            return {
                'level': 'warning',
                'color': (0, 255, 255),  # Vàng
                'needs_alert': True,
                'priority': 2,
                'ttc': ttc,
                'stopping_distance': stopping_distance
            }
        elif distance <= 20.0:
            return {
                'level': 'caution',
                'color': (0, 165, 255),  # Cam
                'needs_alert': False,
                'priority': 1,
                'ttc': ttc,
                'stopping_distance': stopping_distance
            }
        else:
            return {
                'level': 'safe',
                'color': (0, 255, 0),  # Xanh lá
                'needs_alert': False,
                'priority': 0,
                'ttc': ttc,
                'stopping_distance': stopping_distance
            }
    
    def process_detections_with_ttc(self, detections, current_time, current_velocity_ms=None):
        """
        Xử lý danh sách phát hiện và tính TTC cho mỗi vật thể
        
        Args:
            detections: Danh sách vật thể đã được tính khoảng cách
            current_time: Thời gian hiện tại (giây)
            current_velocity_ms: Vận tốc hiện tại của xe (m/s), nếu có
            
        Returns:
            list: Danh sách vật thể đã được đánh giá với TTC
        """
        processed = []
        
        for detection in detections:
            distance = detection.get('distance')
            if distance is None:
                continue
            
            # Tạo ID cho vật thể
            bbox = detection.get('bbox', (0, 0, 0, 0))
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            object_id = f"{detection.get('class', 'unknown')}_{int(center_x//50)}_{int(center_y//50)}"
            
            # Ước lượng vận tốc tương đối
            relative_velocity = self.estimate_relative_velocity(object_id, distance, current_time)
            
            # Đánh giá rủi ro với TTC
            risk_assessment = self.assess_risk_with_ttc(
                distance, 
                relative_velocity, 
                current_velocity_ms
            )
            
            processed_detection = {
                **detection,
                'relative_velocity': relative_velocity,
                'risk': risk_assessment
            }
            
            processed.append(processed_detection)
        
        # Xóa lịch sử của các vật thể không còn xuất hiện
        active_ids = {f"{d.get('class', 'unknown')}_{int((d.get('bbox', (0,0,0,0))[0] + d.get('bbox', (0,0,0,0))[2])//50)}_{int((d.get('bbox', (0,0,0,0))[1] + d.get('bbox', (0,0,0,0))[3])//50)}" 
                     for d in detections}
        self.distance_history = {k: v for k, v in self.distance_history.items() 
                               if any(k.startswith(aid.split('_')[0]) for aid in active_ids)}
        
        return processed
    
    def clear_history(self):
        """Xóa lịch sử khoảng cách"""
        self.distance_history.clear()

