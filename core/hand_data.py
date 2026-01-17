# core/hand_data.py
from settings import FINGER_THICKNESS 

class HandModel:
    """
    HAND MODEL: Chứa kiến thức về giải phẫu học (Anatomy).
    """
    CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),       # Ngón cái
        (0, 5), (5, 6), (6, 7), (7, 8),       # Ngón trỏ
        (9, 10), (10, 11), (11, 12),          # Ngón giữa
        (13, 14), (14, 15), (15, 16),         # Ngón áp út
        (0, 17), (17, 18), (18, 19), (19, 20) # Ngón út
    ]

    PALM_INDICES = [0, 1, 5, 9, 13, 17]


class HandStyle:
    """
    HAND STYLE: Chỉnh màu sắc tại đây.
    """
    REALISTIC_SHADOW = {
        # Màu Xám Trong Suốt: (R, G, B, Alpha)
        # Alpha = 150 (Khoảng 60% độ đậm)
        "color": (100, 100, 100, 150), 
        
        "finger_thickness": FINGER_THICKNESS,
        "joint_radius_ratio": 0.5,
        "use_palm_fill": True
    } 