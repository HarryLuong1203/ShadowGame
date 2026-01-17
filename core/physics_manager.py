# core/physics_manager.py
import pymunk
import random
import numpy as np
import time
from settings import (
    WIDTH, HEIGHT, GRAVITY, BALL_RADIUS, BALL_ELASTICITY, BALL_FRICTION,
    BASKET_X, BASKET_Y, BASKET_WIDTH, BASKET_HEIGHT, COLOR_BASKET,
    FINGER_THICKNESS, FPS, POWERUP_TYPES, POWERUP_SPAWN_CHANCE,
    NEGATIVE_BALL_CHANCE, MULTI_BALL_CHANCE, MAX_BALLS_AT_ONCE, 
    BALL_SPAWN_DELAY, POWERUP_DURATION
)
from core.hand_data import HandModel
from typing import Tuple, Optional, List

class Ball:
    """Class đại diện cho một quả bóng"""
    def __init__(self, body, shape, ball_type='normal', powerup_type=None):
        self.body = body
        self.shape = shape
        self.ball_type = ball_type  # 'normal', 'powerup', 'negative'
        self.powerup_type = powerup_type

class PhysicsManager:
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)
        
        # --- QUẢN LÝ NHIỀU BÓNG ---
        self.balls = []  # Danh sách các Ball objects
        self.spawn_queue = []  # Hàng đợi spawn bóng
        self.last_spawn_time = 0
        
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

    def spawn_ball(self, force_powerup=False, force_negative=False):
        """Tạo bóng mới - có thể spawn nhiều bóng"""
        current_time = time.time()
        
        # Xác định số lượng bóng sẽ spawn
        num_balls = 1
        if random.random() < MULTI_BALL_CHANCE:
            num_balls = random.randint(2, MAX_BALLS_AT_ONCE)
        
        # Thêm vào hàng đợi spawn
        for i in range(num_balls):
            spawn_time = current_time + (i * BALL_SPAWN_DELAY)
            
            # Xác định loại bóng
            if force_negative:
                ball_type = 'negative'
                powerup_type = None
            elif force_powerup or random.random() < POWERUP_SPAWN_CHANCE:
                ball_type = 'powerup'
                powerup_type = random.choice(list(POWERUP_TYPES.keys()))
            elif random.random() < NEGATIVE_BALL_CHANCE:
                ball_type = 'negative'
                powerup_type = None
            else:
                ball_type = 'normal'
                powerup_type = None
            
            # Xác định vị trí spawn
            if ball_type == 'negative':
                # Bóng trừ điểm rơi thẳng vào rổ
                rand_x = BASKET_X + BASKET_WIDTH // 2
            else:
                # Bóng thường spawn ngẫu nhiên
                rand_x = random.randint(100, WIDTH - 100)
            
            self.spawn_queue.append({
                'time': spawn_time,
                'x': rand_x,
                'type': ball_type,
                'powerup': powerup_type
            })

    def _create_ball_now(self, x, ball_type, powerup_type):
        """Tạo bóng ngay lập tức"""
        body = pymunk.Body(1, 100, body_type=pymunk.Body.DYNAMIC)
        body.position = (x, -50)
        shape = pymunk.Circle(body, BALL_RADIUS)
        shape.elasticity = BALL_ELASTICITY
        shape.friction = BALL_FRICTION
        
        self.space.add(body, shape)
        ball = Ball(body, shape, ball_type, powerup_type)
        self.balls.append(ball)

    def process_spawn_queue(self):
        """Xử lý hàng đợi spawn bóng"""
        current_time = time.time()
        remaining_queue = []
        
        for item in self.spawn_queue:
            if current_time >= item['time']:
                self._create_ball_now(item['x'], item['type'], item['powerup'])
            else:
                remaining_queue.append(item)
        
        self.spawn_queue = remaining_queue

    def remove_ball(self, ball):
        """Xóa một bóng cụ thể"""
        if ball in self.balls:
            self.space.remove(ball.body, ball.shape)
            self.balls.remove(ball)

    def check_balls_status(self) -> List[Tuple[int, str, Optional[str]]]:
        """
        Kiểm tra trạng thái tất cả các bóng
        Returns: List[(status, ball_type, powerup_type)]
        - status: 1 (vào rổ), -1 (ra ngoài), 0 (đang rơi)
        """
        results = []
        balls_to_remove = []
        
        for ball in self.balls:
            x, y = ball.body.position
            r = BALL_RADIUS

            # Kiểm tra vào rổ
            if (BASKET_X < x < BASKET_X + BASKET_WIDTH) and \
               (BASKET_Y + r < y < BASKET_Y + BASKET_HEIGHT):
                results.append((1, ball.ball_type, ball.powerup_type))
                balls_to_remove.append(ball)
                continue

            # Kiểm tra ra ngoài biên
            if x < -r or x > WIDTH + r or y > HEIGHT + r:
                results.append((-1, ball.ball_type, ball.powerup_type))
                balls_to_remove.append(ball)
                continue
        
        # Xóa các bóng đã xử lý
        for ball in balls_to_remove:
            self.remove_ball(ball)
        
        return results

    def apply_magnet_force(self):
        """Áp dụng lực hút nam châm cho TẤT CẢ các bóng"""
        if not self.magnet_active:
            return
        
        basket_center_x = BASKET_X + BASKET_WIDTH // 2
        basket_center_y = BASKET_Y + BASKET_HEIGHT // 2
        
        for ball in self.balls:
            # Chỉ hút bóng thường và powerup, không hút bóng trừ điểm
            if ball.ball_type == 'negative':
                continue
                
            ball_pos = ball.body.position
            dx = basket_center_x - ball_pos.x
            dy = basket_center_y - ball_pos.y
            
            distance = max(1, (dx**2 + dy**2)**0.5)
            
            max_force = 2000
            force_magnitude = min(self.magnet_strength / (distance * 0.1), max_force)        
            force_x = (dx / distance) * force_magnitude
            force_y = (dy / distance) * force_magnitude
            
            ball.body.apply_force_at_local_point((force_x, force_y))

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
        # Xử lý hàng đợi spawn
        self.process_spawn_queue()
        
        # Áp dụng magnet nếu active
        if self.magnet_active:
            self.apply_magnet_force()
        
        self.space.step(dt)
    
    def set_magnet(self, active):
        """Bật/tắt nam châm"""
        self.magnet_active = active
    
    def get_all_balls(self):
        """Lấy danh sách tất cả các bóng"""
        return self.balls
    
    def reset(self):
        """Reset game"""
        for ball in self.balls[:]:
            self.remove_ball(ball)
        self.balls.clear()
        self.spawn_queue.clear()
        self.hand_body.velocity = (0, 0)
        self.prev_center = None
        self.magnet_active = False