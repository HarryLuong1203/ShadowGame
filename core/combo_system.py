# core/combo_system.py
import time
from settings import COMBO_TIMEOUT, COMBO_MULTIPLIERS

class ComboSystem:
    """Quản lý hệ thống combo và streak"""
    def __init__(self):
        self.combo_count = 0
        self.last_score_time = 0
        self.current_multiplier = 1
        self.best_combo = 0
        
        # Animation
        self.combo_display_time = 0
        self.combo_scale = 1.0
        
    def add_score(self):
        """Gọi khi ghi điểm"""
        current_time = time.time()
        
        # Kiểm tra timeout
        if self.last_score_time > 0 and (current_time - self.last_score_time) > COMBO_TIMEOUT:
            self.break_combo()
        
        # Tăng combo
        self.combo_count += 1
        self.last_score_time = current_time
        
        # Cập nhật multiplier
        self._update_multiplier()
        
        # Update best combo
        if self.combo_count > self.best_combo:
            self.best_combo = self.combo_count
        
        # Trigger animation
        self.combo_display_time = 2.0  # Hiển thị 2 giây
        self.combo_scale = 1.5  # Phóng to
        
        return self.current_multiplier
    
    def _update_multiplier(self):
        """Tính toán multiplier dựa trên combo"""
        self.current_multiplier = 1
        
        # Tìm multiplier cao nhất mà combo đạt được
        for threshold, multiplier in sorted(COMBO_MULTIPLIERS.items(), reverse=True):
            if self.combo_count >= threshold:
                self.current_multiplier = multiplier
                break
    
    def break_combo(self):
        """Reset combo"""
        self.combo_count = 0
        self.current_multiplier = 1
        self.combo_display_time = 0
    
    def check_timeout(self):
        """Kiểm tra xem combo có bị timeout không"""
        if self.last_score_time > 0:
            current_time = time.time()
            if (current_time - self.last_score_time) > COMBO_TIMEOUT:
                self.break_combo()
    
    def update(self, dt):
        """Update animation"""
        if self.combo_display_time > 0:
            self.combo_display_time -= dt
            
            # Scale animation
            if self.combo_scale > 1.0:
                self.combo_scale -= dt * 2
                if self.combo_scale < 1.0:
                    self.combo_scale = 1.0
    
    def reset(self):
        """Reset toàn bộ (khi bắt đầu game mới)"""
        self.combo_count = 0
        self.last_score_time = 0
        self.current_multiplier = 1
        self.combo_display_time = 0
        self.combo_scale = 1.0
        # Không reset best_combo vì nó là record
    
    def should_show_combo(self):
        """Có nên hiển thị combo text không"""
        return self.combo_count >= 2 and self.combo_display_time > 0
    
    def get_combo_text(self):
        """Lấy text hiển thị"""
        if self.combo_count < 2:
            return ""
        
        text = f"COMBO x{self.combo_count}!"
        if self.current_multiplier > 1:
            text += f" ({self.current_multiplier}x Points)"
        
        return text
    
    def get_time_until_timeout(self):
        """Thời gian còn lại trước khi timeout"""
        if self.last_score_time == 0:
            return 0
        
        current_time = time.time()
        elapsed = current_time - self.last_score_time
        remaining = max(0, COMBO_TIMEOUT - elapsed)
        return remaining