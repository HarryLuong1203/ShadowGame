# settings.py

# --- CẤU HÌNH MÀN HÌNH ---
WIDTH = 1280
HEIGHT = 720
FPS = 60  # Giữ 60 FPS cho mượt

# --- VẬT LÝ (TỐI ƯU) ---
GRAVITY = 900
BALL_RADIUS = 20
BALL_ELASTICITY = 0.4
BALL_FRICTION = 0.5
PHYSICS_ITERATIONS = 10  # Giảm từ 10 xuống 5 để tăng hiệu suất

# --- THÔNG SỐ VẼ TAY ---
FINGER_THICKNESS = 40

# --- CẤU HÌNH GAMEPLAY ---
GAME_DURATION = 60  # Giữ lại nhưng không dùng làm điều kiện thắng
WIN_SCORE = 10      # Đạt 10 điểm = THẮNG
BASKET_WIDTH = 160  # Rộng hơn xíu cho dễ hứng
BASKET_HEIGHT = 100

BASKET_X = (WIDTH - BASKET_WIDTH) // 2
BASKET_Y = HEIGHT - 150 

# --- COMBO & STREAK ---
COMBO_TIMEOUT = 5.0
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

# --- BÓNG TRỪ ĐIỂM (ĐÃ SỬA) ---
NEGATIVE_BALL_CHANCE = 0.15  # 10% cơ hội xuất hiện bóng trừ điểm (GIẢM TỪ 0.2 → 0.1)
NEGATIVE_BALL_PENALTY = -1  # Số điểm bị trừ
NEGATIVE_BALL_COLOR = (50, 50, 50)  # Màu đen
NEGATIVE_BALL_SYMBOL = '💀'  # Biểu tượng

# --- SPAWN NHIỀU BÓNG (ĐÃ SỬA) ---
MULTI_BALL_CHANCE = 0.6  # 60% cơ hội spawn nhiều bóng (TĂNG TỪ 0.4 → 0.6)
MAX_BALLS_AT_ONCE = 3    # Tối đa 3 bóng cùng lúc
BALL_SPAWN_DELAY = 0.3   # Khoảng cách giữa các bóng (giây)

# --- HIỆU ỨNG HẠT (PARTICLES) ---
PARTICLE_COUNT = 30        # Số lượng hạt nổ ra
PARTICLE_LIFETIME = 1.0    # Thời gian tồn tại của hạt (giây)
PARTICLE_SPEED_MIN = 100   # Tốc độ tối thiểu
PARTICLE_SPEED_MAX = 300   # Tốc độ tối đa
PARTICLE_SIZE_MIN = 3      # Kích thước hạt nhỏ nhất
PARTICLE_SIZE_MAX = 8      # Kích thước hạt lớn nhất
STAR_TRAIL_LENGTH = 15     # Độ dài đuôi sao chổi

# --- BALL SKINS (Giữ nguyên nhưng chỉ dùng default) ---
BALL_SKINS = {
    'default': {
        'type': 'solid',
        'color': (220, 60, 60),
        'name': 'Bóng Đỏ (Cơ Bản)'
    }
}

# --- THEMES (Chỉ giữ default) ---
THEMES = {
    'default': {
        'bg': (245, 240, 220),      # Sẽ bị ghi đè bởi ảnh nền
        'basket': (100, 60, 30),    # Màu gỗ nâu
        'text': (50, 40, 40),       # Nâu đen
        'ui_bg': (255, 255, 255, 200),
        'name': 'Cổ Điển'
    }
}

# Màu mặc định fallback
COLOR_BG = THEMES['default']['bg']
COLOR_BALL = (200, 50, 50)
COLOR_BASKET = THEMES['default']['basket']
COLOR_TEXT = THEMES['default']['text']
COLOR_UI_BG = THEMES['default']['ui_bg']

# --- NỀN ẢNH (MỚI) ---
BACKGROUND_IMAGE = "slide.jpg"  # Tên file ảnh nền

# Export __init__.py sẽ import
__all__ = [
    'WIDTH', 'HEIGHT', 'FPS', 'GRAVITY', 'BALL_RADIUS',
    'NEGATIVE_BALL_CHANCE', 'NEGATIVE_BALL_PENALTY', 'NEGATIVE_BALL_COLOR',
    'NEGATIVE_BALL_SYMBOL', 'MULTI_BALL_CHANCE', 'MAX_BALLS_AT_ONCE',
    'BALL_SPAWN_DELAY', 'BACKGROUND_IMAGE'
]