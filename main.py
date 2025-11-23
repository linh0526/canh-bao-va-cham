"""
Ứng dụng chính - ITS Hệ thống cảnh báo và ngăn ngừa va chạm
"""

import sys
import os

# Thêm đường dẫn vào sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

if __name__ == "__main__":
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\nỨng dụng đã được dừng bởi người dùng")
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {e}")
        import traceback
        traceback.print_exc()

