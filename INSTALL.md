# Hướng dẫn cài đặt nhanh

## Bước 1: Cài đặt Python

Đảm bảo bạn đã cài đặt Python 3.8 trở lên:
```bash
python --version
```

## Bước 2: Cài đặt các thư viện

```bash
pip install -r requirements.txt
```

Nếu gặp lỗi với PyTorch, cài đặt theo phiên bản phù hợp với hệ thống của bạn:
- Windows: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`
- Linux/Mac: `pip install torch torchvision`

## Bước 3: Kiểm tra file cần thiết

Đảm bảo các file sau có trong thư mục:
- ✅ `canhbao.mp3` - File âm thanh cảnh báo
- ✅ `yolov8n.pt` - Mô hình YOLO (sẽ tự động tải nếu chưa có)

## Bước 4: Chạy ứng dụng

```bash
python main.py
```

## Khắc phục lỗi thường gặp

### Lỗi: "No module named 'ultralytics'"
```bash
pip install ultralytics
```

### Lỗi: "No module named 'PIL'"
```bash
pip install Pillow
```

### Lỗi: Camera không hoạt động
- Kiểm tra camera có được kết nối
- Thử thay đổi `CAMERA_INDEX` trong `config/config.py` (0, 1, 2...)

### Lỗi: Không tải được mô hình YOLO
- Kiểm tra kết nối internet
- Hoặc tải thủ công từ: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

## Kiểm tra cài đặt

Chạy script kiểm tra:
```bash
python -c "import cv2; import ultralytics; import pygame; import PIL; print('Tất cả thư viện đã được cài đặt thành công!')"
```

