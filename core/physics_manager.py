# core/physics_manager.py
import pymunk
import random
import numpy as np
from settings import *
from core.hand_data import HandModel
from typing import Tuple, Optional

class PhysicsManager:
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)
        
        # --- QUẢN LÝ BÓNG ---
        self.current_ball = None 
        self.ball_shape = None
        self.ball_type = 'normal'  # 'normal' hoặc 'powerup'
        self.powerup_type = None   # Loại power-up nếu là bóng đặc biệt
        
        # --- RỔ HỨNG BÓNG ---
        self.create_basket()

        # --- TAY ---
        self.hand_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.space.add(self.hand_body)
        self.hand_shapes = [] 
        self.prev_center = None
        
        # --- MAGNET POWER-UP ---
        self.magnet_active = False
        self.magnet_strength = 500

    def create_basket(self):
        """Tạo 3 bức tường tĩnh làm thành cái rổ"""
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        thickness = 10
        
        floor = pymunk.Segment(body, (BASKET_X, BASKET_Y + BASKET_HEIGHT), 
                                     (BASKET_X + BASKET_WIDTH, BASKET_Y + BASKET_HEIGHT), thickness)
        left = pymunk.Segment(body, (BASKET_X, BASKET_Y), 
                                    (BASKET_X, BASKET_Y + BASKET_HEIGHT), thickness)
        right = pymunk.Segment(body, (BASKET_X + BASKET_WIDTH, BASKET_Y), 
                                     (BASKET_X + BASKET_WIDTH, BASKET_Y + BASKET_HEIGHT), thickness)
        
        self.space.add(body)
        
        for shape in [floor, left, right]:
            shape.elasticity = 0.5
            shape.friction = 1.0
            shape.color = (*COLOR_BASKET, 255)
            self.space.add(shape)
            
        self.basket_body = body

    def spawn_ball(self, force_powerup=False):
        """Tạo bóng mới (có thể là bóng thường hoặc power-up)"""
        if self.current_ball is not None:
            return

        rand_x = random.randint(100, WIDTH - 100)
        body = pymunk.Body(1, 100, body_type=pymunk.Body.DYNAMIC)
        body.position = (rand_x, -50)
        shape = pymunk.Circle(body, BALL_RADIUS)
        shape.elasticity = BALL_ELASTICITY
        shape.friction = BALL_FRICTION
        
        # Xác định loại bóng
        if force_powerup or random.random() < POWERUP_SPAWN_CHANCE:
            self.ball_type = 'powerup'
            self.powerup_type = random.choice(list(POWERUP_TYPES.keys()))
        else:
            self.ball_type = 'normal'
            self.powerup_type = None
        
        self.space.add(body, shape)
        self.current_ball = body
        self.ball_shape = shape

    def remove_ball(self):
        """Xóa bóng hiện tại"""
        if self.current_ball:
            self.space.remove(self.current_ball, self.ball_shape)
            self.current_ball = None
            self.ball_shape = None
            self.ball_type = 'normal'
            self.powerup_type = None

    def check_ball_status(self) -> Tuple[int, Optional[str]]:
        """
        Kiểm tra trạng thái bóng:
        - Return (1, powerup_type): Vào rổ
        - Return (-1, None): Ra ngoài
        - Return (0, None): Đang rơi
        """
        if not self.current_ball:
            return (0, None)

        x, y = self.current_ball.position
        r = BALL_RADIUS

        # Kiểm tra vào rổ
        if (BASKET_X < x < BASKET_X + BASKET_WIDTH) and \
           (BASKET_Y + r < y < BASKET_Y + BASKET_HEIGHT):
            powerup = self.powerup_type if self.ball_type == 'powerup' else None
            self.remove_ball()
            return (1, powerup)

        # Kiểm tra ra ngoài biên
        if x < -r or x > WIDTH + r or y > HEIGHT + r:
            self.remove_ball()
            return (-1, None)

        return (0, None)

    def apply_magnet_force(self):
        """Áp dụng lực hút nam châm"""
        if not self.magnet_active or not self.current_ball:
            return
        
        # Tính vector từ bóng đến giữa rổ
        basket_center_x = BASKET_X + BASKET_WIDTH // 2
        basket_center_y = BASKET_Y + BASKET_HEIGHT // 2
        
        ball_pos = self.current_ball.position
        dx = basket_center_x - ball_pos.x
        dy = basket_center_y - ball_pos.y
        
        distance = max(1, (dx**2 + dy**2)**0.5)
        
        # Lực hút giảm theo khoảng cách
        max_force = 2000
        force_magnitude = min(self.magnet_strength / (distance * 0.1), max_force)        
        force_x = (dx / distance) * force_magnitude
        force_y = (dy / distance) * force_magnitude
        
        self.current_ball.apply_force_at_local_point((force_x, force_y))

    def update_hand_physics(self, hands_landmarks):
        for shape in self.hand_shapes:
            self.space.remove(shape)
        self.hand_shapes.clear()
        
        self.hand_body.position = (0, 0)
        
        if not hands_landmarks:
            self.hand_body.velocity = (0, 0)
            self.prev_center = None
            return

        all_points = []
        for points in hands_landmarks:
            all_points.extend(points.values())
        
        if all_points:
            current_center = np.mean(all_points, axis=0)
            if self.prev_center is not None:
                dx = current_center[0] - self.prev_center[0]
                dy = current_center[1] - self.prev_center[1]
                self.hand_body.velocity = (dx * FPS, dy * FPS)
            else:
                self.hand_body.velocity = (0, 0)
            self.prev_center = current_center

        p_radius = FINGER_THICKNESS / 2.0

        for points in hands_landmarks:
            palm_points_list = [points[i] for i in HandModel.PALM_INDICES if i in points]
            if len(palm_points_list) >= 3:
                try:
                    poly = pymunk.Poly(self.hand_body, palm_points_list)
                    poly.elasticity = 0.2
                    poly.friction = 0.8
                    poly.filter = pymunk.ShapeFilter(group=1)
                    self.space.add(poly)
                    self.hand_shapes.append(poly)
                except: pass

            for p1_id, p2_id in HandModel.CONNECTIONS:
                if p1_id in points and p2_id in points:
                    segment = pymunk.Segment(self.hand_body, points[p1_id], points[p2_id], p_radius)
                    segment.elasticity = 0.2
                    segment.friction = 0.8
                    segment.filter = pymunk.ShapeFilter(group=1)
                    self.space.add(segment)
                    self.hand_shapes.append(segment)

    def step(self, dt):
        # Áp dụng magnet nếu active
        if self.magnet_active:
            self.apply_magnet_force()
        
        self.space.step(dt)
    
    def set_magnet(self, active):
        """Bật/tắt nam châm"""
        self.magnet_active = active
    
    def reset(self):
        """Reset game"""
        self.remove_ball()
        self.hand_body.velocity = (0, 0)
        self.prev_center = None
        self.magnet_active = False