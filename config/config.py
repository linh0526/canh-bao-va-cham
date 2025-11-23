"""
File cấu hình hệ thống ITS - Cảnh báo và ngăn ngừa va chạm
"""

# Cấu hình camera
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
FPS_TARGET = 30

# Cấu hình YOLO
YOLO_MODEL_PATH = 'yolov8n.pt'
YOLO_CONFIDENCE_THRESHOLD = 0.5
DETECTION_CLASSES = ['person', 'car', 'truck', 'bus', 'motorcycle', 'bicycle']

# Cấu hình khoảng cách
FOCAL_LENGTH = 900  # Tiêu cự camera

# Chiều cao thực tế của các vật thể (mét)
REAL_HEIGHTS = {
    'person': 1.7,
    'car': 1.5,
    'truck': 2.5,
    'bus': 2.8,
    'motorcycle': 1.2,
    'bicycle': 1.5
}

# Ngưỡng cảnh báo (mét) - Cho xe ô tô trong phố, tốc độ ~50 km/h
SAFE_DISTANCE = 8.0  # Khoảng cách nguy hiểm (≤ 8m)
WARNING_DISTANCE = 15.0  # Khoảng cách cảnh báo (8-15m)
CAUTION_DISTANCE = 20.0  # Khoảng cách thận trọng (15-20m)
SAFE_DISTANCE_THRESHOLD = 20.0  # Khoảng cách an toàn (> 20m)

# Cấu hình TTC (Time-to-Collision)
ENABLE_TTC = True  # Bật/tắt tính toán TTC
TTC_DANGER = 2.0  # TTC nguy hiểm (≤ 2 giây)
TTC_WARNING = 4.0  # TTC cảnh báo (2-4 giây)
TTC_CAUTION = 6.0  # TTC thận trọng (4-6 giây)

# Cấu hình khoảng cách dừng
REACTION_TIME = 1.2  # Thời gian phản ứng của tài xế (giây)
DECELERATION = 6.0  # Gia tốc hãm (m/s²), ~0.6g

# Phát hiện chuyển động
ENABLE_MOTION_DETECTION = True  # Bật/tắt phát hiện chuyển động
MOTION_HISTORY_SIZE = 10  # Số khung hình lưu lại
MOTION_THRESHOLD = 0.02  # Ngưỡng chuyển động (tỷ lệ)
STATIONARY_RATIO_THRESHOLD = 0.7  # Tỷ lệ vật thể đứng yên để coi là xe dừng (tăng từ 0.6)
MIN_VELOCITY_FOR_ALERT = 0.5  # Vận tốc tối thiểu (m/s) để cảnh báo
MAX_TTC_FOR_ALERT = 10.0  # TTC tối đa (giây) để cảnh báo
CONSECUTIVE_RISK_THRESHOLD = 4  # Số lần liên tục phát hiện nguy hiểm trước khi cảnh báo
CONSECUTIVE_SAFE_THRESHOLD = 1  # Số lần liên tục an toàn để tắt cảnh báo

# Vùng làn đường trước mặt (ROI - Region of Interest)
ENABLE_LANE_FILTER = True  # Bật/tắt lọc làn đường
LANE_CENTER_WIDTH = 0.5  # Chiều rộng vùng giữa (50% = 0.5, 40% = 0.4)
LANE_LEFT_MARGIN = 0.25  # Lề trái (25% mỗi bên)
LANE_RIGHT_MARGIN = 0.25  # Lề phải (25% mỗi bên)
SHOW_LANE_ROI = True  # Hiển thị vùng ROI trên màn hình

# Màu sắc cảnh báo (BGR format cho OpenCV)
COLOR_SAFE = (0, 255, 0)      # Xanh lá - An toàn
COLOR_CAUTION = (0, 165, 255)  # Cam - Thận trọng
COLOR_WARNING = (0, 255, 255)  # Vàng - Cảnh báo
COLOR_DANGER = (0, 0, 255)     # Đỏ - Nguy hiểm

# Cấu hình âm thanh
ALERT_SOUND_PATH = 'canhbao.mp3'
ALERT_VOLUME = 0.7

# Cấu hình logging
LOG_DIR = 'logs'
LOG_FILE = 'collision_warnings.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Cấu hình hiệu năng
MAX_PROCESSING_TIME_MS = 100  # Thời gian xử lý tối đa (ms)
ENABLE_MULTITHREADING = True

# Cấu hình giao diện
GUI_TITLE = "ITS - Hệ thống cảnh báo và ngăn ngừa va chạm"
GUI_WIDTH = 1280
GUI_HEIGHT = 720
DISPLAY_FPS = True
DISPLAY_DISTANCE = True
DISPLAY_WARNING_LEVEL = True

