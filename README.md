# ITS - Hệ thống cảnh báo và ngăn ngừa va chạm phía trước

Ứng dụng phát hiện vật cản phía trước, ước lượng khoảng cách, dự đoán nguy cơ va chạm và cảnh báo kịp thời cho người lái bằng hình ảnh và âm thanh.

## Tính năng chính

- ✅ **Thu nhận dữ liệu thời gian thực** từ camera/cảm biến phía trước
- ✅ **Nhận diện vật cản** bằng mô hình AI YOLOv8 (person, car, truck, bus, motorcycle, bicycle)
- ✅ **Ước lượng khoảng cách** vật cản dựa trên chiều cao thực tế và tiêu cự camera
- ✅ **Tính toán Time-to-Collision (TTC)** dựa trên vận tốc tương đối
- ✅ **Tính khoảng cách dừng an toàn** dựa trên vận tốc và gia tốc hãm
- ✅ **Đánh giá nguy cơ va chạm** kết hợp khoảng cách và TTC với 4 mức độ: An toàn, Thận trọng, Cảnh báo, Nguy hiểm
- ✅ **Cảnh báo đa phương thức**: Âm thanh + Hiển thị trực quan với bounding box, khoảng cách và TTC
- ✅ **Hệ thống logging** lưu nhật ký cảnh báo để phân tích
- ✅ **Phát hiện xe dừng** tự động tắt cảnh báo khi xe đang dừng (đèn đỏ)
- ✅ **Giao diện trực quan** với màu sắc cảnh báo (xanh → cam → vàng → đỏ)
- ✅ **Xử lý thời gian thực** với độ trễ thấp

## Yêu cầu hệ thống

- Python 3.8 trở lên
- Camera hoặc webcam
- Windows/Linux/macOS

## Cài đặt

### 1. Clone hoặc tải xuống dự án

```bash
cd app
```

### 2. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

### 3. Tải mô hình YOLO (nếu chưa có)

Mô hình `yolov8n.pt` sẽ được tự động tải khi chạy lần đầu. Hoặc bạn có thể tải thủ công từ [Ultralytics](https://github.com/ultralytics/ultralytics).

### 4. Chuẩn bị file âm thanh cảnh báo

Đảm bảo file `canhbao.mp3` có trong thư mục gốc của ứng dụng.

## Sử dụng

### Chạy ứng dụng

```bash
python main.py
```

### Giao diện người dùng

1. **Chọn nguồn**: Chọn Camera hoặc Video để test
2. **Bắt đầu**: Nhấn nút "Bắt đầu" để khởi động hệ thống
3. **Xem cảnh báo**: Hệ thống sẽ tự động phát hiện và cảnh báo khi có nguy cơ va chạm
4. **Xem nhật ký**: Xem và xuất nhật ký cảnh báo

### Các mức độ cảnh báo

Hệ thống sử dụng kết hợp **khoảng cách** và **Time-to-Collision (TTC)** để đánh giá nguy cơ:

- 🟢 **An toàn** (> 20m hoặc TTC > 6s): Màu xanh lá, không cảnh báo
- 🟠 **Thận trọng** (15-20m hoặc TTC 4-6s): Màu cam, chỉ cảnh báo hình ảnh
- 🟡 **Cảnh báo** (8-15m hoặc TTC 2-4s): Màu vàng, có cảnh báo âm thanh
- 🔴 **Nguy hiểm** (≤ 8m hoặc TTC ≤ 2s): Màu đỏ, cảnh báo âm thanh khẩn cấp

**Lưu ý**: Ngưỡng này phù hợp cho xe ô tô trong phố, tốc độ ~50 km/h. Với tốc độ cao hơn (80-100 km/h), khoảng cách nên tăng gấp đôi.

## Cấu trúc dự án

```
app/
├── main.py                      # File chạy chính
├── config/
│   └── config.py               # Cấu hình hệ thống
├── modules/
│   ├── camera_module.py        # Module thu nhận camera
│   ├── detection_module.py     # Module phát hiện YOLO
│   ├── distance_module.py      # Module tính khoảng cách
│   ├── ttc_module.py           # Module tính TTC và khoảng cách dừng
│   ├── motion_detection_module.py  # Module phát hiện chuyển động
│   ├── alert_module.py         # Module cảnh báo
│   └── logger_module.py        # Module logging
├── gui/
│   └── main_window.py          # Giao diện người dùng
├── logs/                       # Thư mục lưu nhật ký
├── data/                       # Thư mục dữ liệu
├── canhbao.mp3                 # File âm thanh cảnh báo
├── yolov8n.pt                  # Mô hình YOLO
├── requirements.txt            # Danh sách thư viện
└── README.md                   # File hướng dẫn
```

## Cấu hình

Các thông số có thể điều chỉnh trong `config/config.py`:

- **Ngưỡng khoảng cách**: `SAFE_DISTANCE` (8m), `WARNING_DISTANCE` (15m), `CAUTION_DISTANCE` (20m)
- **Ngưỡng TTC**: `TTC_DANGER` (2s), `TTC_WARNING` (4s), `TTC_CAUTION` (6s)
- **Thời gian phản ứng**: `REACTION_TIME` (1.2s)
- **Gia tốc hãm**: `DECELERATION` (6.0 m/s²)
- **Tiêu cự camera**: `FOCAL_LENGTH`
- **Ngưỡng tin cậy YOLO**: `YOLO_CONFIDENCE_THRESHOLD`
- **Chiều cao thực tế vật thể**: `REAL_HEIGHTS`
- **Cấu hình camera**: `CAMERA_INDEX`, `CAMERA_WIDTH`, `CAMERA_HEIGHT`

## Phân quyền

### Người lái (Driver)
- Xem cảnh báo
- Xem camera

### Kỹ thuật viên (Technician)
- Tất cả quyền của Người lái
- Xem nhật ký cảnh báo
- Xem thống kê
- Điều chỉnh cài đặt

### Quản trị viên (Admin)
- Tất cả quyền của Kỹ thuật viên
- Quản lý người dùng

## Hiệu năng

- **Độ trễ xử lý**: ≤ 100ms (tùy thuộc vào phần cứng)
- **FPS**: 20-30 FPS trên máy tính trung bình
- **Độ chính xác**: Phụ thuộc vào điều kiện ánh sáng và chất lượng camera

## Khắc phục sự cố

### Camera không hoạt động
- Kiểm tra camera có được kết nối đúng không
- Thử thay đổi `CAMERA_INDEX` trong `config/config.py` (0, 1, 2...)

### Mô hình YOLO không tải được
- Kiểm tra kết nối internet (lần đầu tải mô hình)
- Hoặc tải thủ công file `yolov8n.pt` và đặt vào thư mục gốc

### Âm thanh không phát
- Kiểm tra file `canhbao.mp3` có tồn tại không
- Kiểm tra cài đặt âm thanh hệ thống

## Mở rộng

Hệ thống có thể được mở rộng với:
- Tích hợp radar/LiDAR
- Kết nối với hệ thống phanh tự động
- Phân tích dữ liệu nâng cao
- Giao diện web
- Ứng dụng mobile

## Tác giả

Nhóm phát triển ITS - Hệ thống Giao thông Thông minh

## Giấy phép

Dự án này được phát triển cho mục đích nghiên cứu và giáo dục.

