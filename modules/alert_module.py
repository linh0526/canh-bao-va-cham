"""
Module cảnh báo âm thanh và hình ảnh
"""

import pygame
import cv2
import numpy as np
from config.config import ALERT_SOUND_PATH, ALERT_VOLUME, COLOR_SAFE, COLOR_CAUTION, COLOR_WARNING, COLOR_DANGER


class AlertModule:
    """Module quản lý cảnh báo âm thanh và hiển thị trực quan"""
    
    def __init__(self, sound_path=ALERT_SOUND_PATH):
        """
        Khởi tạo alert module
        
        Args:
            sound_path: Đường dẫn đến file âm thanh cảnh báo
        """
        self.sound_path = sound_path
        self.is_playing = False
        self.volume = ALERT_VOLUME
        self.pygame_initialized = False
        
    def initialize(self):
        """Khởi tạo pygame mixer"""
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(self.sound_path)
            pygame.mixer.music.set_volume(self.volume)
            self.pygame_initialized = True
            return True
        except Exception as e:
            print(f"Lỗi khởi tạo âm thanh: {e}")
            return False
    
    def play_alert(self, loop=True):
        """
        Phát cảnh báo âm thanh
        
        Args:
            loop: Có phát lặp lại không
        """
        if not self.pygame_initialized:
            if not self.initialize():
                return
        
        if not self.is_playing:
            try:
                if loop:
                    pygame.mixer.music.play(-1)  # Phát lặp vô hạn
                else:
                    pygame.mixer.music.play()
                self.is_playing = True
            except Exception as e:
                print(f"Lỗi phát âm thanh: {e}")
    
    def stop_alert(self):
        """Dừng cảnh báo âm thanh"""
        if self.is_playing:
            try:
                pygame.mixer.music.stop()
                self.is_playing = False
            except Exception as e:
                print(f"Lỗi dừng âm thanh: {e}")
    
    def set_volume(self, volume):
        """
        Điều chỉnh âm lượng
        
        Args:
            volume: Mức âm lượng (0.0 - 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        if self.pygame_initialized:
            pygame.mixer.music.set_volume(self.volume)
    
    @staticmethod
    def draw_detections(frame, processed_detections):
        """
        Vẽ bounding box và thông tin lên khung hình
        
        Args:
            frame: Khung hình đầu vào
            processed_detections: Danh sách vật thể đã được xử lý
            
        Returns:
            numpy.ndarray: Khung hình đã được vẽ
        """
        display_frame = frame.copy()
        
        for detection in processed_detections:
            x1, y1, x2, y2 = detection['bbox']
            distance = detection['distance']
            class_name = detection['class']
            confidence = detection['confidence']
            risk = detection['risk']
            
            # Màu sắc dựa trên mức độ nguy hiểm
            color = risk['color']
            thickness = 3 if risk['needs_alert'] else 2
            
            # Vẽ bounding box
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, thickness)
            
            # Vẽ nhãn với thông tin
            label_parts = []
            if distance is not None:
                label_parts.append(f"{distance:.2f}m")
            
            # Thêm TTC nếu có
            ttc = risk.get('ttc')
            if ttc is not None:
                label_parts.append(f"TTC: {ttc:.1f}s")
            
            label_parts.append(class_name)
            label_parts.append(f"{confidence:.1%}")
            
            label = " | ".join(label_parts)
            
            # Tính kích thước text
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            (text_width, text_height), baseline = cv2.getTextSize(
                label, font, font_scale, 2
            )
            
            # Vẽ background cho text
            cv2.rectangle(
                display_frame,
                (x1, y1 - text_height - baseline - 5),
                (x1 + text_width, y1),
                color,
                -1
            )
            
            # Vẽ text
            cv2.putText(
                display_frame,
                label,
                (x1, y1 - 5),
                font,
                font_scale,
                (255, 255, 255),
                2
            )
        
        return display_frame
    
    @staticmethod
    def draw_status_overlay(frame, fps=None, alert_count=0, closest_distance=None, status_text=None, closest_ttc=None):
        """
        Vẽ thông tin trạng thái lên khung hình
        
        Args:
            frame: Khung hình đầu vào
            fps: FPS hiện tại
            alert_count: Số lượng cảnh báo
            closest_distance: Khoảng cách gần nhất
            status_text: Text trạng thái bổ sung (ví dụ: "Xe: DỪNG", "Cảnh báo: TẮT")
            
        Returns:
            numpy.ndarray: Khung hình đã được vẽ
        """
        display_frame = frame.copy()
        h, w = display_frame.shape[:2]
        
        # Vẽ background cho thông tin (mở rộng nếu có status_text)
        overlay = display_frame.copy()
        height = 130 if status_text else 100
        cv2.rectangle(overlay, (10, 10), (350, height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, display_frame, 0.3, 0, display_frame)
        
        y_offset = 30
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # FPS
        if fps is not None:
            cv2.putText(
                display_frame,
                f"FPS: {fps}",
                (20, y_offset),
                font,
                0.6,
                (0, 255, 0),
                2
            )
            y_offset += 25
        
        # Số lượng cảnh báo
        if alert_count > 0:
            cv2.putText(
                display_frame,
                f"Canh bao: {alert_count}",
                (20, y_offset),
                font,
                0.6,
                (0, 0, 255),
                2
            )
            y_offset += 25
        
        # Khoảng cách gần nhất
        if closest_distance is not None:
            distance_text = f"Gan nhat: {closest_distance:.2f}m"
            if closest_ttc is not None:
                distance_text += f" (TTC: {closest_ttc:.1f}s)"
            cv2.putText(
                display_frame,
                distance_text,
                (20, y_offset),
                font,
                0.6,
                (0, 255, 255),
                2
            )
            y_offset += 25
        
        # Trạng thái bổ sung
        if status_text:
            cv2.putText(
                display_frame,
                status_text,
                (20, y_offset),
                font,
                0.6,
                (0, 165, 255),  # Màu cam
                2
            )
        
        return display_frame
    
    def cleanup(self):
        """Giải phóng tài nguyên"""
        self.stop_alert()
        if self.pygame_initialized:
            pygame.mixer.quit()
            self.pygame_initialized = False

