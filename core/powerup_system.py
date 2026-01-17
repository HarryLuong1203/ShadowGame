# core/powerup_system.py
import time
from settings import POWERUP_DURATION

class PowerUp:
    """Một power-up đơn lẻ"""
    def __init__(self, powerup_type):
        self.type = powerup_type
        self.start_time = time.time()
        self.duration = POWERUP_DURATION
        self.active = True
        
    def get_remaining_time(self):
        elapsed = time.time() - self.start_time
        remaining = self.duration - elapsed
        return max(0, remaining)
    
    def is_expired(self):
        return self.get_remaining_time() <= 0
    
    def update(self):
        if self.is_expired():
            self.active = False


class PowerUpSystem:
    """Quản lý các power-ups đang active"""
    def __init__(self):
        self.active_powerups = []
        
    def activate(self, powerup_type):
        """Kích hoạt power-up mới"""
        # Kiểm tra xem đã có power-up cùng loại chưa
        for pu in self.active_powerups:
            if pu.type == powerup_type:
                # Reset thời gian
                pu.start_time = time.time()
                return
        
        # Thêm power-up mới
        powerup = PowerUp(powerup_type)
        self.active_powerups.append(powerup)
    
    def update(self):
        """Cập nhật và loại bỏ power-ups hết hạn"""
        for pu in self.active_powerups:
            pu.update()
        
        self.active_powerups = [pu for pu in self.active_powerups if pu.active]
    
    def has_powerup(self, powerup_type):
        """Kiểm tra có power-up này đang active không"""
        for pu in self.active_powerups:
            if pu.type == powerup_type and pu.active:
                return True
        return False
    
    def get_powerup(self, powerup_type):
        """Lấy power-up object"""
        for pu in self.active_powerups:
            if pu.type == powerup_type and pu.active:
                return pu
        return None
    
    def clear(self):
        """Xóa tất cả power-ups"""
        self.active_powerups.clear()
    
    def get_active_list(self):
        """Lấy danh sách power-ups đang active (để hiển thị UI)"""
        return [(pu.type, pu.get_remaining_time()) for pu in self.active_powerups]