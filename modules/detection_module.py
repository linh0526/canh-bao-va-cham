"""
Module phát hiện vật cản sử dụng YOLO
"""

from ultralytics import YOLO
import numpy as np
from config.config import YOLO_MODEL_PATH, YOLO_CONFIDENCE_THRESHOLD, DETECTION_CLASSES


class DetectionModule:
    """Module phát hiện vật cản bằng YOLO"""
    
    def __init__(self, model_path=YOLO_MODEL_PATH):
        """
        Khởi tạo detection module
        
        Args:
            model_path: Đường dẫn đến file mô hình YOLO
        """
        self.model = None
        self.model_path = model_path
        self.confidence_threshold = YOLO_CONFIDENCE_THRESHOLD
        self.detection_classes = DETECTION_CLASSES
        
    def initialize(self):
        """Khởi tạo mô hình YOLO"""
        try:
            self.model = YOLO(self.model_path)
            return True
        except Exception as e:
            print(f"Lỗi khởi tạo mô hình YOLO: {e}")
            return False
    
    def detect(self, frame):
        """
        Phát hiện vật cản trong khung hình
        
        Args:
            frame: Khung hình đầu vào (numpy array)
            
        Returns:
            list: Danh sách các vật thể được phát hiện
                 Mỗi vật thể là dict với keys: 'class', 'confidence', 'bbox', 'class_id'
        """
        if self.model is None:
            return []
        
        try:
            results = self.model(frame, verbose=False, conf=self.confidence_threshold)
            detections = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = self.model.names[cls_id]
                    
                    # Chỉ lấy các lớp trong danh sách
                    if class_name in self.detection_classes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        detection = {
                            'class': class_name,
                            'class_id': cls_id,
                            'confidence': conf,
                            'bbox': (x1, y1, x2, y2),
                            'pixel_height': y2 - y1,
                            'pixel_width': x2 - x1
                        }
                        detections.append(detection)
            
            return detections
        except Exception as e:
            print(f"Lỗi phát hiện vật cản: {e}")
            return []
    
    def get_model_info(self):
        """Lấy thông tin mô hình"""
        if self.model is None:
            return None
        return {
            'model_path': self.model_path,
            'classes': list(self.model.names.values()),
            'num_classes': len(self.model.names)
        }

