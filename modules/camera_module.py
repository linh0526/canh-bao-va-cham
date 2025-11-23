"""
Module thu nhận dữ liệu từ camera
"""

import cv2
import threading
import time
from config.config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, FPS_TARGET


class CameraModule:
    """Module quản lý camera và thu nhận khung hình"""
    
    def __init__(self, camera_index=None, video_path=None, loop_video=False):
        """
        Khởi tạo camera module
        
        Args:
            camera_index: Chỉ số camera (mặc định 0) hoặc None nếu dùng video
            video_path: Đường dẫn đến file video hoặc None nếu dùng camera
            loop_video: Có phát lại video khi hết không (mặc định False)
        """
        self.camera_index = camera_index if camera_index is not None else CAMERA_INDEX
        self.video_path = video_path
        self.loop_video = loop_video
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.fps = 0
        self.last_frame_time = time.time()
        self.is_video_file = video_path is not None
        self.video_fps = 0
        
    def initialize(self):
        """Khởi tạo camera hoặc video file"""
        try:
            if self.is_video_file:
                # Mở file video
                self.cap = cv2.VideoCapture(self.video_path)
                if not self.cap.isOpened():
                    raise Exception(f"Không thể mở file video: {self.video_path}")
                # Lấy FPS của video
                self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
                if self.video_fps <= 0:
                    self.video_fps = 30  # Mặc định 30 FPS
            else:
                # Mở camera
                self.cap = cv2.VideoCapture(self.camera_index)
                if not self.cap.isOpened():
                    raise Exception(f"Không thể mở camera {self.camera_index}")
                
                # Thiết lập độ phân giải
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
                self.cap.set(cv2.CAP_PROP_FPS, FPS_TARGET)
            
            return True
        except Exception as e:
            print(f"Lỗi khởi tạo: {e}")
            return False
    
    def start(self):
        """Bắt đầu thu nhận khung hình"""
        if self.cap is None:
            if not self.initialize():
                return False
        
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        return True
    
    def _capture_loop(self):
        """Vòng lặp thu nhận khung hình"""
        frame_count = 0
        start_time = time.time()
        last_frame_time = time.time()
        
        # Tính thời gian delay giữa các frame cho video
        if self.is_video_file and self.video_fps > 0:
            frame_delay = 1.0 / self.video_fps
        else:
            frame_delay = 0  # Camera không cần delay
        
        while self.is_running:
            # Điều chỉnh tốc độ phát video
            if self.is_video_file and frame_delay > 0:
                current_time = time.time()
                elapsed = current_time - last_frame_time
                if elapsed < frame_delay:
                    time.sleep(frame_delay - elapsed)
                last_frame_time = time.time()
            
            ret, frame = self.cap.read()
            if ret:
                with self.frame_lock:
                    self.current_frame = frame.copy()
                    frame_count += 1
                    
                    # Tính FPS
                    current_time = time.time()
                    if current_time - start_time >= 1.0:
                        self.fps = frame_count
                        frame_count = 0
                        start_time = current_time
            else:
                # Nếu là video file và đã hết
                if self.is_video_file:
                    # Kiểm tra xem đã đến cuối video chưa
                    total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                    
                    if current_frame >= total_frames - 1:
                        # Video đã hết
                        if self.loop_video:
                            # Phát lại từ đầu nếu được bật
                            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            last_frame_time = time.time()  # Reset thời gian
                            continue
                        else:
                            # Dừng lại nếu không phát lại
                            self.is_running = False
                            break
                    else:
                        # Có thể là lỗi đọc, thử lại
                        time.sleep(0.01)
                else:
                    time.sleep(0.01)
    
    def get_frame(self):
        """
        Lấy khung hình hiện tại
        
        Returns:
            numpy.ndarray: Khung hình hoặc None nếu không có
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None
    
    def get_fps(self):
        """Lấy FPS hiện tại"""
        return self.fps
    
    def stop(self):
        """Dừng camera và giải phóng tài nguyên"""
        self.is_running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def __del__(self):
        """Destructor"""
        self.stop()

