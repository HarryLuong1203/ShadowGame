# core/particle_system.py
import pygame
import random
import math
from settings import (
    GRAVITY, PARTICLE_COUNT, PARTICLE_LIFETIME, 
    PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX,
    PARTICLE_SIZE_MIN, PARTICLE_SIZE_MAX,
    STAR_TRAIL_LENGTH, POWERUP_TYPES
)

class Particle:
    """Một hạt hiệu ứng đơn lẻ"""
    def __init__(self, x, y, vx, vy, color, size, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alpha = 255

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += GRAVITY * dt * 0.3  # Trọng lực nhẹ
        self.lifetime -= dt
        
        # Fade out dần
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        
    def is_dead(self):
        return self.lifetime <= 0

    def draw(self, surface):
        if self.alpha > 0:
            color_with_alpha = (*self.color[:3], self.alpha)
            pos = (int(self.x), int(self.y))
            pygame.draw.circle(surface, color_with_alpha, pos, int(self.size))


class StarTrail:
    """Vệt sao cho combo"""
    def __init__(self, x, y):
        self.positions = [(x, y)]
        self.max_length = STAR_TRAIL_LENGTH
        self.active = True
        self.lifetime = 2.0
        
    def update(self, x, y, dt):
        self.positions.append((x, y))
        if len(self.positions) > self.max_length:
            self.positions.pop(0)
        
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
    
    def draw(self, surface):
        if len(self.positions) < 2:
            return
            
        for i in range(len(self.positions) - 1):
            alpha = int(255 * (i / len(self.positions)))
            color = (255, 215, 0, alpha)  # Màu vàng
            
            start = self.positions[i]
            end = self.positions[i + 1]
            
            # Vẽ line với độ dày giảm dần
            thickness = max(1, int(3 * (i / len(self.positions))))
            pygame.draw.line(surface, color, start, end, thickness)


class ParticleSystem:
    """Quản lý tất cả hiệu ứng particles"""
    def __init__(self):
        self.particles = []
        self.star_trails = []
        self.particle_surface = None
        
    def init_surface(self, width, height):
        self.particle_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
    def create_explosion(self, x, y, color, count=30):
        """Tạo hiệu ứng nổ khi ghi điểm"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(PARTICLE_SIZE_MIN, PARTICLE_SIZE_MAX)
            lifetime = random.uniform(0.5, PARTICLE_LIFETIME)
            
            particle = Particle(x, y, vx, vy, color, size, lifetime)
            self.particles.append(particle)
    
    def create_combo_stars(self, x, y, combo_count):
        """Tạo hiệu ứng sao cho combo"""
        # Sao lớn ở giữa
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 200  # Bay lên trên
            
            star = Particle(x, y, vx, vy, (255, 215, 0), 10, 1.5)
            self.particles.append(star)
        
        # Thêm vệt sao nếu combo cao
        if combo_count >= 5:
            trail = StarTrail(x, y)
            self.star_trails.append(trail)
    
    def create_powerup_collect(self, x, y, powerup_type):
        """Hiệu ứng khi nhặt power-up"""
        color = POWERUP_TYPES[powerup_type]['color']
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 100
            
            particle = Particle(x, y, vx, vy, color, 6, 1.0)
            self.particles.append(particle)
    
    def update(self, dt, ball_pos=None):
        # Update particles
        self.particles = [p for p in self.particles if not p.is_dead()]
        for particle in self.particles:
            particle.update(dt)
        
        # Update star trails
        if ball_pos:
            for trail in self.star_trails:
                trail.update(ball_pos[0], ball_pos[1], dt)
        
        self.star_trails = [t for t in self.star_trails if t.active]
    
    def draw(self, screen):
        if not self.particle_surface:
            return
            
        self.particle_surface.fill((0, 0, 0, 0))
        
        # Vẽ star trails trước
        for trail in self.star_trails:
            trail.draw(self.particle_surface)
        
        # Vẽ particles
        for particle in self.particles:
            particle.draw(self.particle_surface)
        
        screen.blit(self.particle_surface, (0, 0))
    
    def clear(self):
        """Xóa hết hiệu ứng"""
        self.particles.clear()
        self.star_trails.clear()