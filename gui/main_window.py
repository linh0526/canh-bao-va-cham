"""
Giao diện người dùng chính của ứng dụng ITS
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import threading
import time
from datetime import datetime

import sys
import os

# Thêm đường dẫn gốc vào sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from modules.camera_module import CameraModule
from modules.detection_module import DetectionModule
from modules.distance_module import DistanceModule
from modules.alert_module import AlertModule
from modules.logger_module import LoggerModule
from modules.motion_detection_module import MotionDetectionModule
from modules.ttc_module import TTCModule
from modules.lane_filter_module import LaneFilterModule
from config.config import (GUI_TITLE, GUI_WIDTH, GUI_HEIGHT, ENABLE_MOTION_DETECTION, 
                          ENABLE_TTC, MIN_VELOCITY_FOR_ALERT, MAX_TTC_FOR_ALERT,
                          CONSECUTIVE_RISK_THRESHOLD, CONSECUTIVE_SAFE_THRESHOLD)


class MainWindow:
    """Cửa sổ chính của ứng dụng"""
    
    def __init__(self):
        """Khởi tạo giao diện chính"""
        self.root = tk.Tk()
        self.root.title(GUI_TITLE)
        self.root.geometry(f"{GUI_WIDTH}x{GUI_HEIGHT}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Các module
        self.camera = None
        self.detection = DetectionModule()
        self.distance = DistanceModule()
        self.alert = AlertModule()
        self.logger = LoggerModule()
        self.motion_detection = MotionDetectionModule() if ENABLE_MOTION_DETECTION else None
        self.ttc_module = TTCModule() if ENABLE_TTC else None
        self.lane_filter = LaneFilterModule()
        
        # Trạng thái
        self.is_running = False
        self.current_frame = None
        self.processed_detections = []
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        self.video_path = None
        self.use_camera = True
        self.alert_disabled = False  # Tắt cảnh báo tạm thời
        self.alert_disabled_until = 0  # Thời gian tắt cảnh báo đến khi nào
        self._label_size = None  # Kích thước label để tránh resize liên tục
        self.consecutive_risk_count = 0  # Đếm số lần liên tục phát hiện nguy hiểm
        self.consecutive_safe_count = 0  # Đếm số lần liên tục an toàn
        
        # Giao diện
        self.setup_ui()
        
        # Khởi tạo các module
        self.initialize_modules()
    
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        # Menu bar
        self.create_menu_bar()
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Video display
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Video label
        self.video_label = ttk.Label(left_panel, text="Khởi tạo camera...", background='black')
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(left_panel)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Source selection
        source_frame = ttk.Frame(control_frame)
        source_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(source_frame, text="Nguồn:").pack(side=tk.LEFT, padx=2)
        self.source_var = tk.StringVar(value="camera")
        ttk.Radiobutton(source_frame, text="Camera", variable=self.source_var, 
                       value="camera", command=self.on_source_change).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(source_frame, text="Video", variable=self.source_var, 
                       value="video", command=self.on_source_change).pack(side=tk.LEFT, padx=2)
        
        self.select_video_btn = ttk.Button(source_frame, text="Chọn video...", 
                                          command=self.select_video_file, state=tk.DISABLED)
        self.select_video_btn.pack(side=tk.LEFT, padx=5)
        
        self.video_path_label = ttk.Label(source_frame, text="", foreground="gray")
        self.video_path_label.pack(side=tk.LEFT, padx=5)
        
        # Tùy chọn phát lại video
        self.loop_video_var = tk.BooleanVar(value=False)
        self.loop_video_check = ttk.Checkbutton(source_frame, text="Phát lại video", 
                                               variable=self.loop_video_var, state=tk.DISABLED)
        self.loop_video_check.pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.LEFT, padx=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Bắt đầu", command=self.start_system)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Dừng", command=self.stop_system, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.mute_alert_btn = ttk.Button(btn_frame, text="Tắt cảnh báo (30s)", 
                                         command=self.toggle_alert_mute)
        self.mute_alert_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Trạng thái: Chưa khởi động")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Right panel - Information
        right_panel = ttk.Frame(main_frame, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        right_panel.pack_propagate(False)
        
        # Statistics
        stats_frame = ttk.LabelFrame(right_panel, text="Thống kê")
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.fps_label = ttk.Label(stats_frame, text="FPS: 0")
        self.fps_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.detection_label = ttk.Label(stats_frame, text="Vật thể phát hiện: 0")
        self.detection_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.alert_label = ttk.Label(stats_frame, text="Cảnh báo: 0")
        self.alert_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Detection list
        detection_frame = ttk.LabelFrame(right_panel, text="Vật thể phát hiện")
        detection_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview for detections
        columns = ('Class', 'Distance', 'Risk')
        self.detection_tree = ttk.Treeview(detection_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.detection_tree.heading(col, text=col)
            self.detection_tree.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(detection_frame, orient=tk.VERTICAL, command=self.detection_tree.yview)
        self.detection_tree.configure(yscrollcommand=scrollbar.set)
        
        self.detection_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Logs section
        self.logs_frame = ttk.LabelFrame(right_panel, text="Nhật ký cảnh báo")
        self.logs_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.logs_text = tk.Text(self.logs_frame, height=6, wrap=tk.WORD)
        logs_scrollbar = ttk.Scrollbar(self.logs_frame, orient=tk.VERTICAL, command=self.logs_text.yview)
        self.logs_text.configure(yscrollcommand=logs_scrollbar.set)
        
        self.logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.export_btn = ttk.Button(self.logs_frame, text="Xuất nhật ký", command=self.export_logs)
        self.export_btn.pack(pady=5)
    
    def create_menu_bar(self):
        """Tạo thanh menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Xuất nhật ký...", command=self.export_logs)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Xem", menu=view_menu)
        view_menu.add_command(label="Thống kê", command=self.show_statistics)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cài đặt", menu=settings_menu)
        settings_menu.add_command(label="Cấu hình hệ thống", command=self.show_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Trợ giúp", menu=help_menu)
        help_menu.add_command(label="Về ứng dụng", command=self.show_about)
    
    def initialize_modules(self):
        """Khởi tạo các module"""
        try:
            # Khởi tạo logger
            self.logger.initialize()
            self.logger.log_info("Khởi tạo hệ thống...")
            
            # Khởi tạo detection
            if not self.detection.initialize():
                messagebox.showerror("Lỗi", "Không thể khởi tạo mô hình YOLO")
                return False
            
            # Khởi tạo alert
            if not self.alert.initialize():
                messagebox.showwarning("Cảnh báo", "Không thể khởi tạo hệ thống âm thanh")
            
            self.logger.log_info("Khởi tạo thành công")
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khởi tạo: {e}")
            return False
    
    def on_source_change(self):
        """Xử lý khi thay đổi nguồn (camera/video)"""
        if self.source_var.get() == "video":
            self.select_video_btn.config(state=tk.NORMAL)
            self.loop_video_check.config(state=tk.NORMAL)
            self.use_camera = False
        else:
            self.select_video_btn.config(state=tk.DISABLED)
            self.loop_video_check.config(state=tk.DISABLED)
            self.video_path = None
            self.video_path_label.config(text="")
            self.use_camera = True
    
    def select_video_file(self):
        """Chọn file video"""
        file_path = filedialog.askopenfilename(
            title="Chọn file video",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("MP4 files", "*.mp4"),
                ("AVI files", "*.avi"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.video_path = file_path
            # Hiển thị tên file (rút gọn nếu quá dài)
            file_name = os.path.basename(file_path)
            if len(file_name) > 30:
                file_name = "..." + file_name[-27:]
            self.video_path_label.config(text=file_name, foreground="black")
            self.logger.log_info(f"Đã chọn video: {file_path}")
    
    def start_system(self):
        """Bắt đầu hệ thống"""
        if self.is_running:
            return
        
        try:
            # Kiểm tra nguồn video
            if not self.use_camera:
                if not self.video_path:
                    messagebox.showwarning("Cảnh báo", "Vui lòng chọn file video trước")
                    return
                # Khởi tạo camera với video file
                loop_video = self.loop_video_var.get()
                self.camera = CameraModule(video_path=self.video_path, loop_video=loop_video)
            else:
                # Khởi tạo camera
                self.camera = CameraModule()
            
            # Khởi động camera/video
            if not self.camera.start():
                error_msg = "Không thể khởi động camera" if self.use_camera else "Không thể mở file video"
                messagebox.showerror("Lỗi", error_msg)
                return
            
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Trạng thái: Đang chạy")
            
            # Bắt đầu vòng lặp xử lý
            self.start_time = time.time()
            self.frame_count = 0
            self.process_loop()
            
            self.logger.log_info("Hệ thống đã được khởi động")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khởi động: {e}")
            self.is_running = False
    
    def toggle_alert_mute(self):
        """Tắt/bật cảnh báo tạm thời (30 giây)"""
        if self.alert_disabled:
            # Bật lại cảnh báo
            self.alert_disabled = False
            self.alert_disabled_until = 0
            self.mute_alert_btn.config(text="Tắt cảnh báo (30s)")
            self.logger.log_info("Đã bật lại cảnh báo")
        else:
            # Tắt cảnh báo 30 giây
            self.alert_disabled = True
            self.alert_disabled_until = time.time() + 30
            self.alert.stop_alert()
            self.mute_alert_btn.config(text="Bật cảnh báo")
            self.logger.log_info("Đã tắt cảnh báo tạm thời (30 giây)")
    
    def stop_system(self):
        """Dừng hệ thống"""
        self.is_running = False
        if self.camera:
            self.camera.stop()
        self.alert.stop_alert()
        
        # Reset trạng thái
        self.alert_disabled = False
        self.alert_disabled_until = 0
        self.consecutive_risk_count = 0
        self.consecutive_safe_count = 0
        if self.motion_detection:
            self.motion_detection.clear_history()
        if self.ttc_module:
            self.ttc_module.clear_history()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.mute_alert_btn.config(text="Tắt cảnh báo (30s)")
        self.status_label.config(text="Trạng thái: Đã dừng")
        
        self.logger.log_info("Hệ thống đã được dừng")
    
    def process_loop(self):
        """Vòng lặp xử lý chính"""
        if not self.is_running:
            return
        
        try:
            # Lấy khung hình
            if self.camera is None:
                self.root.after(10, self.process_loop)
                return
                
            frame = self.camera.get_frame()
            if frame is None:
                # Kiểm tra nếu video đã hết
                if not self.use_camera and self.camera and not self.camera.is_running:
                    self.status_label.config(text="Trạng thái: Video đã hết")
                    self.stop_system()
                    return
                self.root.after(10, self.process_loop)
                return
            
            # Tính FPS
            self.frame_count += 1
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                self.fps = self.frame_count / elapsed
            
            # Phát hiện vật thể
            detections = self.detection.detect(frame)
            
            # Lọc chỉ lấy vật thể ở làn đường trước mặt
            h, w = frame.shape[:2]
            detections = self.lane_filter.filter_detections(detections, w, h)
            
            # Tính khoảng cách
            processed_detections = self.distance.process_detections(detections)
            
            # Tính TTC và đánh giá rủi ro nâng cao (nếu bật)
            if self.ttc_module and len(processed_detections) > 0:
                current_time = time.time()
                # Ước lượng vận tốc hiện tại (có thể lấy từ GPS/sensor, tạm thời để None)
                current_velocity_ms = None  # Có thể thêm input từ cảm biến tốc độ
                processed_detections = self.ttc_module.process_detections_with_ttc(
                    processed_detections, 
                    current_time,
                    current_velocity_ms
                )
            
            self.processed_detections = processed_detections
            
            # Phát hiện chuyển động (nếu bật)
            is_vehicle_stopped = False
            if self.motion_detection and len(processed_detections) > 0:
                h, w = frame.shape[:2]
                self.motion_detection.update_frame_size(w, h)
                movement_info = self.motion_detection.calculate_movement(processed_detections)
                is_vehicle_stopped = self.motion_detection.is_vehicle_stopped(
                    processed_detections, movement_info
                )
            
            # Kiểm tra thời gian tắt cảnh báo tạm thời
            if self.alert_disabled_until > 0 and time.time() >= self.alert_disabled_until:
                self.alert_disabled = False
                self.alert_disabled_until = 0
                self.mute_alert_btn.config(text="Tắt cảnh báo (30s)")
            
            # Kiểm tra nguy cơ va chạm
            has_risk = self.distance.has_collision_risk(processed_detections)
            
            # Kiểm tra thêm điều kiện: nếu vận tốc tương đối gần 0 thì không cảnh báo
            has_real_risk = False
            if has_risk:
                for det in processed_detections:
                    if det['risk']['needs_alert']:
                        # Kiểm tra vận tốc tương đối (nếu có)
                        rel_velocity = det.get('relative_velocity', 0)
                        ttc = det['risk'].get('ttc')
                        distance = det.get('distance')
                        
                        # Nếu vận tốc tương đối rất thấp hoặc TTC rất lớn
                        # thì không cảnh báo (có thể là vật thể đứng yên)
                        if abs(rel_velocity) < MIN_VELOCITY_FOR_ALERT or (ttc is not None and ttc > MAX_TTC_FOR_ALERT):
                            continue
                        
                        # Nếu khoảng cách xa (>15m) và vận tốc thấp, không cảnh báo
                        if distance is not None and distance > 15.0 and abs(rel_velocity) < 1.5:
                            continue
                        
                        has_real_risk = True
                        break
            
            # Hệ thống đếm liên tục: chỉ cảnh báo sau N lần liên tục phát hiện nguy hiểm
            if has_real_risk:
                self.consecutive_risk_count += 1
                self.consecutive_safe_count = 0
            else:
                self.consecutive_risk_count = 0
                self.consecutive_safe_count += 1
            
            # Chỉ cảnh báo khi:
            # 1. Phát hiện nguy hiểm liên tục đủ số lần
            # 2. Người dùng chưa tắt tạm thời
            # 3. Xe không đang dừng
            # 4. Chưa có đủ số lần an toàn liên tục để tắt cảnh báo
            should_alert = (self.consecutive_risk_count >= CONSECUTIVE_RISK_THRESHOLD and 
                          not self.alert_disabled and 
                          not is_vehicle_stopped and
                          self.consecutive_safe_count < CONSECUTIVE_SAFE_THRESHOLD)
            
            if should_alert:
                self.alert.play_alert()
                # Ghi nhật ký cho các vật thể nguy hiểm
                for det in processed_detections:
                    if det['risk']['needs_alert']:
                        self.logger.log_warning(det)
            else:
                self.alert.stop_alert()
                if is_vehicle_stopped and has_risk:
                    # Ghi log khi tắt cảnh báo do xe dừng
                    self.logger.log_info("Cảnh báo đã tắt do phát hiện xe đang dừng")
            
            # Vẽ vùng ROI làn đường (nếu bật)
            display_frame = self.lane_filter.draw_lane_roi(frame)
            
            # Vẽ lên khung hình
            display_frame = self.alert.draw_detections(display_frame, processed_detections)
            
            # Vẽ thông tin trạng thái
            closest_obj = self.distance.get_closest_object(processed_detections)
            closest_dist = closest_obj['distance'] if closest_obj else None
            closest_ttc = closest_obj['risk'].get('ttc') if closest_obj else None
            
            alert_count = sum(1 for d in processed_detections if d['risk']['needs_alert'])
            
            # Thêm thông tin trạng thái
            status_text = []
            if self.alert_disabled:
                status_text.append("Cảnh báo: TẮT")
            if is_vehicle_stopped:
                status_text.append("Xe: DỪNG")
            
            display_frame = self.alert.draw_status_overlay(
                display_frame,
                fps=int(self.fps),
                alert_count=alert_count,
                closest_distance=closest_dist,
                closest_ttc=closest_ttc,
                status_text=" | ".join(status_text) if status_text else None
            )
            
            # Hiển thị khung hình
            self.display_frame(display_frame)
            
            # Cập nhật thống kê
            self.update_statistics(processed_detections)
            
            # Cập nhật nhật ký
            self.update_logs_display()
            
        except Exception as e:
            self.logger.log_error(f"Lỗi xử lý: {e}")
        
        # Lặp lại
        self.root.after(1, self.process_loop)
    
    def display_frame(self, frame):
        """Hiển thị khung hình lên giao diện"""
        try:
            # Lấy kích thước gốc của frame
            h, w = frame.shape[:2]
            
            # Lấy kích thước label (chỉ lấy một lần, không lặp lại)
            if not hasattr(self, '_label_size') or self._label_size is None:
                self.root.update_idletasks()  # Cập nhật layout trước
                label_w = self.video_label.winfo_width()
                label_h = self.video_label.winfo_height()
                
                # Chỉ lưu nếu kích thước hợp lệ
                if label_w > 1 and label_h > 1:
                    self._label_size = (label_w, label_h)
                else:
                    # Sử dụng kích thước mặc định nếu chưa có
                    self._label_size = (960, 540)  # 16:9 aspect ratio
            
            label_w, label_h = self._label_size
            
            # Tính scale để giữ tỷ lệ khung hình
            scale = min(label_w / w, label_h / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # Chỉ resize nếu cần thiết
            if new_w != w or new_h != h:
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            
            # Chuyển đổi sang RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            
            self.video_label.config(image=img_tk)
            self.video_label.image = img_tk  # Giữ reference
            
        except Exception as e:
            print(f"Lỗi hiển thị: {e}")
    
    def update_statistics(self, detections):
        """Cập nhật thống kê"""
        self.fps_label.config(text=f"FPS: {int(self.fps)}")
        self.detection_label.config(text=f"Vật thể phát hiện: {len(detections)}")
        
        alert_count = sum(1 for d in detections if d['risk']['needs_alert'])
        self.alert_label.config(text=f"Cảnh báo: {alert_count}")
        
        # Cập nhật danh sách vật thể
        self.detection_tree.delete(*self.detection_tree.get_children())
        for det in detections:
            distance_str = f"{det['distance']:.2f}m" if det['distance'] else "N/A"
            risk_level = det['risk']['level']
            self.detection_tree.insert('', tk.END, values=(det['class'], distance_str, risk_level))
    
    def update_logs_display(self):
        """Cập nhật hiển thị nhật ký"""
        logs = self.logger.get_warning_logs(limit=20)
        self.logs_text.delete(1.0, tk.END)
        
        for log in reversed(logs[-20:]):  # Hiển thị 20 bản ghi gần nhất
            timestamp = log.get('timestamp', '')
            class_name = log.get('class', '')
            distance = log.get('distance', 0)
            risk = log.get('risk_level', '')
            
            log_line = f"[{timestamp}] {class_name} - {distance:.2f}m - {risk}\n"
            self.logs_text.insert(tk.END, log_line)
    
    def export_logs(self):
        """Xuất nhật ký ra file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            exported = self.logger.export_logs_to_json(file_path)
            if exported:
                messagebox.showinfo("Thành công", f"Đã xuất nhật ký ra: {exported}")
            else:
                messagebox.showerror("Lỗi", "Không thể xuất nhật ký")
    
    def show_statistics(self):
        """Hiển thị cửa sổ thống kê"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Thống kê hệ thống")
        stats_window.geometry("400x300")
        
        # Thêm nội dung thống kê ở đây
        ttk.Label(stats_window, text="Thống kê chi tiết sẽ được hiển thị ở đây").pack(pady=20)
    
    def show_settings(self):
        """Hiển thị cửa sổ cài đặt"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Cài đặt hệ thống")
        settings_window.geometry("500x400")
        
        # Thêm nội dung cài đặt ở đây
        ttk.Label(settings_window, text="Cài đặt hệ thống sẽ được hiển thị ở đây").pack(pady=20)
    
    def show_about(self):
        """Hiển thị thông tin về ứng dụng"""
        about_text = f"""
{GUI_TITLE}

Phiên bản: 1.0.0

Hệ thống cảnh báo và ngăn ngừa va chạm phía trước
sử dụng công nghệ YOLO và xử lý hình ảnh thời gian thực.

Phát triển bởi: Nhóm ITS
"""
        messagebox.showinfo("Về ứng dụng", about_text)
    
    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        if self.is_running:
            self.stop_system()
        
        self.alert.cleanup()
        self.logger.log_info("Ứng dụng đã được đóng")
        self.root.destroy()
    
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()

