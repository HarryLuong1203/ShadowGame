# 🎮 BÀN TAY MA THUẬT

Game tương tác bằng cử chỉ tay sử dụng Computer Vision và Physics Engine.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5.0-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📸 Demo

> **Lưu ý:** Cần webcam để chơi game!

[Thêm ảnh hoặc GIF demo tại đây]

## 🎯 Mô tả

**Bàn Tay Ma Thuật** là một trò chơi độc đáo sử dụng camera để nhận diện cử chỉ tay của người chơi. Bóng đỏ của bàn tay sẽ tương tác vật lý với các quả bóng rơi xuống!

### Tính năng chính:
- ✋ **Nhận diện bàn tay** bằng MediaPipe AI
- ⚽ **Vật lý thực tế** với Pymunk Physics Engine
- 🎯 **Gameplay đa dạng**: Bóng thường, bóng power-up, bóng trừ điểm
- 🎨 **Hiệu ứng particle** mượt mà
- 🏆 **Hệ thống combo** và điểm số
- 📚 **Tutorial tích hợp** cho người chơi mới

### Cách chơi:
1. 🔴 **Bóng đỏ**: Hứng và đưa vào rổ → +1 điểm
2. 💀 **Bóng đen**: Đánh văng ra ngoài (rơi vào rổ = -1 điểm)
3. 🎁 **Bóng màu**: Power-ups (làm chậm thời gian, nam châm, x2 điểm)
4. 🎯 **Mục tiêu**: Đạt 10 điểm trước khi hết giờ!

---

## 🚀 Cài đặt

### Yêu cầu hệ thống:
- **Python**: 3.8 trở lên
- **Webcam**: Bắt buộc
- **OS**: Windows / macOS / Linux

### Bước 1: Clone repository

```bash
git clone https://github.com/[YOUR_USERNAME]/ShadowGame.git
cd ShadowGame
```

### Bước 2: Tạo môi trường ảo (khuyên dùng)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 4: Chạy game!

```bash
python main.py
```

---

## 📦 Build file .exe (chỉ Windows)

Để tạo file `.exe` chạy độc lập:

1. **Cài PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Chạy build script:**
   ```bash
   build_windows.bat
   ```

3. **Lấy file game:**
   - File `.exe` nằm trong folder `dist/`
   - Kích thước: ~200-300 MB

---

## 🛠️ Cấu trúc dự án

```
ShadowGame/
├── core/                      # Core game modules
│   ├── __init__.py
│   ├── combo_system.py       # Hệ thống combo
│   ├── hand_data.py          # Định nghĩa cấu trúc tay
│   ├── hand_tracking.py      # MediaPipe hand tracking
│   ├── particle_system.py    # Hiệu ứng particles
│   ├── physics_manager.py    # Pymunk physics engine
│   ├── powerup_system.py     # Quản lý power-ups
│   ├── renderer.py           # Pygame rendering
│   └── tutorial_system.py    # Hệ thống hướng dẫn
│
├── font.ttf                  # Font tùy chỉnh
├── slide.jpg                 # Ảnh nền game
├── main.py                   # Entry point
├── settings.py               # Cấu hình game
├── requirements.txt          # Python dependencies
└── build_windows.bat         # Build script cho Windows
```

---

## ⚙️ Tùy chỉnh

Mở file `settings.py` để điều chỉnh:

```python
# Độ khó
WIN_SCORE = 10              # Điểm cần đạt để thắng
GAME_DURATION = 60          # Thời gian (giây)
NEGATIVE_BALL_CHANCE = 0.15 # Tỉ lệ bóng đen xuất hiện

# Hiệu suất
FPS = 60                    # Frames per second
PHYSICS_ITERATIONS = 10     # Độ chính xác vật lý

# Power-ups
POWERUP_SPAWN_CHANCE = 0.2  # Tỉ lệ power-up
POWERUP_DURATION = 8.0      # Thời gian hiệu lực (giây)
```

---

## 🐛 Xử lý lỗi

### **"Không tìm thấy camera"**
- Kiểm tra webcam đã cắm và bật
- Thử thay đổi camera index trong `main.py`:
  ```python
  self.cap = cv2.VideoCapture(1)  # Thử 0, 1, 2...
  ```

### **"Module not found"**
```bash
pip install -r requirements.txt
```

### **Game chạy chậm**
- Giảm FPS trong `settings.py`: `FPS = 30`
- Giảm `PHYSICS_ITERATIONS = 5`

### **Lỗi MediaPipe**
```bash
pip uninstall mediapipe
pip install mediapipe==0.10.0
```

---

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! 

1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/TinhNangMoi`)
3. Commit thay đổi (`git commit -m 'Thêm tính năng mới'`)
4. Push lên branch (`git push origin feature/TinhNangMoi`)
5. Tạo Pull Request

---

## 📜 License

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

---

## 👨‍💻 Tác giả

**[Tên của bạn]**
- GitHub: [@your_username](https://github.com/your_username)
- Email: your_email@example.com

---

## 🙏 Cảm ơn

- [MediaPipe](https://mediapipe.dev/) - Hand tracking
- [Pymunk](http://www.pymunk.org/) - Physics engine
- [Pygame](https://www.pygame.org/) - Game framework

---

## 📝 Changelog

### v1.0.0 (2026-01-18)
- ✨ Phiên bản đầu tiên
- ✋ Nhận diện tay với MediaPipe
- ⚽ Hệ thống vật lý hoàn chỉnh
- 💀 Bóng trừ điểm
- 🎁 Power-ups (slow-motion, magnet, x2 points)
- 🎯 Hệ thống combo
- 🎨 Hiệu ứng particles

---

**⭐ Nếu bạn thích dự án này, hãy cho một ngôi sao trên GitHub!**