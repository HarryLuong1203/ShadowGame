# build_spec.py
# Chạy file này để tạo file .spec cho PyInstaller

import PyInstaller.__main__
import os

# Lấy đường dẫn thư mục hiện tại
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'main.py',
    '--name=BanTayMaThuat',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    
    # Thêm các file dữ liệu
    f'--add-data=font.ttf{os.pathsep}.',
    f'--add-data=slide.jpg{os.pathsep}.',
    f'--add-data=core{os.pathsep}core',
    
    # Thêm các hidden imports cho mediapipe
    '--hidden-import=mediapipe',
    '--hidden-import=cv2',
    '--hidden-import=pygame',
    '--hidden-import=pymunk',
    '--hidden-import=numpy',
    '--hidden-import=mediapipe.python',
    '--hidden-import=mediapipe.python.solutions',
    '--hidden-import=mediapipe.python.solutions.hands',
    '--hidden-import=google.protobuf',
    
    # Collect tất cả data của mediapipe
    '--collect-data=mediapipe',
    '--collect-all=mediapipe',
    
    # Optimization
    '--clean',
    '--noconfirm',
])

print("\n✅ Build hoàn thành! File .exe nằm trong thư mục 'dist/'")