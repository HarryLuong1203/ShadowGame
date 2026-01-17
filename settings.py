# settings.py

# --- CẤU HÌNH MÀN HÌNH ---
WIDTH = 1280
HEIGHT = 720
FPS = 60 

# --- VẬT LÝ ---
GRAVITY = 900
BALL_RADIUS = 20
BALL_ELASTICITY = 0.4 # Do Nhay cua Bong
BALL_FRICTION = 0.5

# --- THÔNG SỐ VẼ TAY ---
FINGER_THICKNESS = 40

# --- CẤU HÌNH GAMEPLAY ---
GAME_DURATION = 60
BASKET_WIDTH = 160 # Rộng hơn xíu cho dễ hứng
BASKET_HEIGHT = 100

BASKET_X = (WIDTH - BASKET_WIDTH) // 2
BASKET_Y = HEIGHT - 150 

# --- COMBO & STREAK ---
COMBO_TIMEOUT = 4.0
COMBO_MULTIPLIERS = {
    2: 2,    # x2 điểm
    5: 3,    # x3 điểm
    10: 5,   # x5 điểm
    15: 10   # x10 điểm
}

# --- POWER-UPS ---
POWERUP_SPAWN_CHANCE = 0.2 # 20% cơ hội
POWERUP_DURATION = 8.0     # Tăng thời gian hiệu lực lên 8s

# Các loại power-up (Việt hóa)
POWERUP_TYPES = {
    'slow_motion': {'color': (100, 200, 255), 'symbol': '⏱', 'name': 'Làm Chậm'},
    'magnet': {'color': (255, 100, 255), 'symbol': '🧲', 'name': 'Nam Châm'},
    'double_points': {'color': (255, 215, 0), 'symbol': 'x2', 'name': 'Nhân Đôi'}
}

# --- HIỆU ỨNG HẠT (PARTICLES) - ĐÃ BỔ SUNG ĐẦY ĐỦ ---
PARTICLE_COUNT = 30        # Số lượng hạt nổ ra
PARTICLE_LIFETIME = 1.0    # Thời gian tồn tại của hạt (giây) <-- QUAN TRỌNG
PARTICLE_SPEED_MIN = 100   # Tốc độ tối thiểu
PARTICLE_SPEED_MAX = 300   # Tốc độ tối đa
PARTICLE_SIZE_MIN = 3      # Kích thước hạt nhỏ nhất
PARTICLE_SIZE_MAX = 8      # Kích thước hạt lớn nhất
STAR_TRAIL_LENGTH = 15     # Độ dài đuôi sao chổi

# --- BALL SKINS (Thêm loại họa tiết) ---
BALL_SKINS = {
    'default': {
        'type': 'solid',
        'color': (220, 60, 60),
        'name': 'Bóng Đỏ (Cơ Bản)'
    },
    'basketball': {
        'type': 'basketball',
        'color': (255, 140, 0), # Cam
        'line_color': (30, 30, 30),
        'name': 'Bóng Rổ'
    },
    'soccer': {
        'type': 'soccer',
        'color': (240, 240, 240), # Trắng
        'patch_color': (20, 20, 20), # Đen
        'name': 'Bóng Đá'
    },
    'beach': {
        'type': 'beach',
        'colors': [(255, 0, 0), (255, 255, 0), (0, 0, 255)], # Đỏ, Vàng, Xanh
        'name': 'Bóng Bãi Biển'
    },
    'rainbow': {
        'type': 'rainbow',
        'color': None,
        'name': 'Cầu Vồng'
    }
}

# --- THEMES (Giao diện) ---
THEMES = {
    'default': {
        'bg': (245, 240, 220),      # Giấy cũ sáng hơn chút
        'basket': (100, 60, 30),    # Màu gỗ nâu
        'text': (50, 40, 40),       # Nâu đen
        'ui_bg': (255, 255, 255, 200),
        'name': 'Cổ Điển'
    },
    'night': {
        'bg': (30, 35, 50),
        'basket': (100, 100, 120),
        'text': (220, 220, 255),
        'ui_bg': (60, 60, 90, 200),
        'name': 'Ban Đêm'
    },
    'forest': {
        'bg': (200, 230, 200),
        'basket': (90, 50, 20),
        'text': (10, 60, 20),
        'ui_bg': (255, 255, 255, 180),
        'name': 'Rừng Xanh'
    }
}

# Màu mặc định fallback
COLOR_BG = THEMES['default']['bg']
COLOR_BALL = (200, 50, 50)
COLOR_BASKET = THEMES['default']['basket']
COLOR_TEXT = THEMES['default']['text']
COLOR_UI_BG = THEMES['default']['ui_bg']