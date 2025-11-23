"""
Module ghi nhật ký cảnh báo và sự kiện hệ thống
"""

import logging
import os
from datetime import datetime
from config.config import LOG_DIR, LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT
import json


class LoggerModule:
    """Module quản lý logging và nhật ký cảnh báo"""
    
    def __init__(self):
        """Khởi tạo logger module"""
        self.log_dir = LOG_DIR
        self.log_file = os.path.join(LOG_DIR, LOG_FILE)
        self.logger = None
        self.warning_logs = []  # Lưu trữ cảnh báo trong bộ nhớ
        
    def initialize(self):
        """Khởi tạo logging system"""
        try:
            # Tạo thư mục logs nếu chưa có
            os.makedirs(self.log_dir, exist_ok=True)
            
            # Cấu hình logger
            self.logger = logging.getLogger('ITS_CollisionWarning')
            self.logger.setLevel(logging.INFO)
            
            # Handler cho file
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
            file_handler.setFormatter(formatter)
            
            # Handler cho console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            
            # Thêm handlers
            if not self.logger.handlers:
                self.logger.addHandler(file_handler)
                self.logger.addHandler(console_handler)
            
            self.logger.info("Hệ thống logging đã được khởi tạo")
            return True
        except Exception as e:
            print(f"Lỗi khởi tạo logging: {e}")
            return False
    
    def log_warning(self, detection_info):
        """
        Ghi nhật ký cảnh báo va chạm
        
        Args:
            detection_info: Thông tin vật thể được phát hiện (dict)
        """
        if self.logger is None:
            return
        
        try:
            timestamp = datetime.now().strftime(LOG_DATE_FORMAT)
            class_name = detection_info.get('class', 'unknown')
            distance = detection_info.get('distance')
            risk_level = detection_info.get('risk', {}).get('level', 'unknown')
            confidence = detection_info.get('confidence', 0)
            
            log_entry = {
                'timestamp': timestamp,
                'class': class_name,
                'distance': distance,
                'risk_level': risk_level,
                'confidence': confidence,
                'bbox': detection_info.get('bbox')
            }
            
            # Ghi vào file
            message = (
                f"CẢNH BÁO - Vật thể: {class_name}, "
                f"Khoảng cách: {distance:.2f}m, "
                f"Mức độ: {risk_level}, "
                f"Độ tin cậy: {confidence:.1%}"
            )
            self.logger.warning(message)
            
            # Lưu vào bộ nhớ (giữ tối đa 1000 bản ghi)
            self.warning_logs.append(log_entry)
            if len(self.warning_logs) > 1000:
                self.warning_logs.pop(0)
                
        except Exception as e:
            print(f"Lỗi ghi nhật ký: {e}")
    
    def log_info(self, message):
        """
        Ghi thông tin hệ thống
        
        Args:
            message: Thông điệp cần ghi
        """
        if self.logger:
            self.logger.info(message)
    
    def log_error(self, message):
        """
        Ghi lỗi hệ thống
        
        Args:
            message: Thông điệp lỗi
        """
        if self.logger:
            self.logger.error(message)
    
    def get_warning_logs(self, limit=100):
        """
        Lấy danh sách cảnh báo gần đây
        
        Args:
            limit: Số lượng bản ghi tối đa
            
        Returns:
            list: Danh sách cảnh báo
        """
        return self.warning_logs[-limit:]
    
    def export_logs_to_json(self, output_path=None):
        """
        Xuất nhật ký ra file JSON
        
        Args:
            output_path: Đường dẫn file output (mặc định: logs/warnings_export.json)
            
        Returns:
            str: Đường dẫn file đã xuất
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.log_dir, f'warnings_export_{timestamp}.json')
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.warning_logs, f, ensure_ascii=False, indent=2)
            return output_path
        except Exception as e:
            self.log_error(f"Lỗi xuất nhật ký: {e}")
            return None
    
    def clear_logs(self):
        """Xóa tất cả nhật ký trong bộ nhớ"""
        self.warning_logs.clear()
        self.log_info("Đã xóa tất cả nhật ký trong bộ nhớ")

