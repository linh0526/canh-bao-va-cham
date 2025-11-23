"""
Module lọc vật thể chỉ ở làn đường trước mặt
"""

import cv2
import numpy as np
from config.config import (ENABLE_LANE_FILTER, LANE_CENTER_WIDTH, 
                          LANE_LEFT_MARGIN, LANE_RIGHT_MARGIN, SHOW_LANE_ROI)


class LaneFilterModule:
    """Module lọc vật thể chỉ ở làn đường trước mặt"""
    
    def __init__(self):
        """Khởi tạo lane filter module"""
        self.enabled = ENABLE_LANE_FILTER
        self.center_width = LANE_CENTER_WIDTH
        self.left_margin = LANE_LEFT_MARGIN
        self.right_margin = LANE_RIGHT_MARGIN
        self.show_roi = SHOW_LANE_ROI
    
    def is_in_lane(self, bbox, frame_width, frame_height):
        """
        Kiểm tra vật thể có nằm trong làn đường trước mặt không
        
        Args:
            bbox: (x1, y1, x2, y2) bounding box của vật thể
            frame_width: Chiều rộng khung hình
            frame_height: Chiều cao khung hình
            
        Returns:
            bool: True nếu vật thể nằm trong làn đường
        """
        if not self.enabled:
            return True  # Nếu không bật filter, cho phép tất cả
        
        x1, y1, x2, y2 = bbox
        
        # Tính tâm của bounding box
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Tính vùng làn đường (giữa khung hình)
        left_bound = frame_width * self.left_margin
        right_bound = frame_width * (1 - self.right_margin)
        
        # Kiểm tra tâm có nằm trong vùng làn đường không
        in_lane = left_bound <= center_x <= right_bound
        
        # Ngoài ra, nếu vật thể quá lớn và một phần đáng kể nằm trong vùng, cũng coi là trong làn
        if not in_lane:
            # Kiểm tra xem có bao nhiêu phần trăm vật thể nằm trong vùng
            bbox_width = x2 - x1
            overlap_left = max(0, left_bound - x1)
            overlap_right = max(0, x2 - right_bound)
            overlap_width = bbox_width - overlap_left - overlap_right
            
            if overlap_width > bbox_width * 0.5:  # Nếu > 50% vật thể trong vùng
                in_lane = True
        
        return in_lane
    
    def filter_detections(self, detections, frame_width, frame_height):
        """
        Lọc danh sách vật thể, chỉ giữ lại những vật thể ở làn đường trước mặt
        
        Args:
            detections: Danh sách vật thể được phát hiện
            frame_width: Chiều rộng khung hình
            frame_height: Chiều cao khung hình
            
        Returns:
            list: Danh sách vật thể đã được lọc
        """
        if not self.enabled:
            return detections
        
        filtered = []
        for detection in detections:
            bbox = detection.get('bbox', (0, 0, 0, 0))
            if self.is_in_lane(bbox, frame_width, frame_height):
                filtered.append(detection)
        
        return filtered
    
    def draw_lane_roi(self, frame):
        """
        Vẽ vùng ROI (làn đường) lên khung hình
        
        Args:
            frame: Khung hình đầu vào
            
        Returns:
            numpy.ndarray: Khung hình đã được vẽ vùng ROI
        """
        if not self.show_roi or not self.enabled:
            return frame
        
        display_frame = frame.copy()
        h, w = display_frame.shape[:2]
        
        # Tính vùng làn đường
        left_bound = int(w * self.left_margin)
        right_bound = int(w * (1 - self.right_margin))
        
        # Vẽ đường viền vùng ROI
        cv2.line(display_frame, (left_bound, 0), (left_bound, h), (0, 255, 255), 2)  # Vàng
        cv2.line(display_frame, (right_bound, 0), (right_bound, h), (0, 255, 255), 2)  # Vàng
        
        # Vẽ nhãn
        cv2.putText(display_frame, "Lane ROI", (left_bound + 10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return display_frame

