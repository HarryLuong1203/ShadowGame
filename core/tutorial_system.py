# core/tutorial_system.py
import pygame

class TutorialSystem:
    """Hệ thống hướng dẫn và hints"""
    def __init__(self):
        self.first_time = True
        self.show_tutorial = False
        self.current_hint = ""
        self.hint_timer = 0
        self.miss_count = 0
        
        # Các tips ngẫu nhiên (CẬP NHẬT)
        self.tips = [
            "Mẹo: Di chuyển tay chậm để kiểm soát bóng tốt hơn!",
            "Mẹo: Ghi điểm liên tiếp để tăng Combo!",
            "Mẹo: Đánh văng bóng đen trước khi chúng rơi vào rổ!",
            "Mẹo: Đặt tay ở vị trí thấp để hứng bóng dễ hơn!",
            "Mẹo: Dùng cả hai tay để tăng phạm vi hứng bóng!",
        ]
        
        # Các bước hướng dẫn (CẬP NHẬT)
        self.tutorial_steps = [
            {
                'title': 'CHÀO MỪNG BẠN!',
                'text': 'Chào mừng đến với "Bàn Tay Ma Thuật".\nMục tiêu: Đạt 10 điểm để chiến thắng!',
                'image': None
            },
            {
                'title': 'CÁCH CHƠI',
                'text': 'Đưa tay lên trước Camera.\nBóng đen của tay bạn sẽ tương tác vật lý với quả bóng!\nHãy hứng bóng đỏ và đưa vào rổ.',
                'image': None
            },
            {
                'title': 'NGUY HIỂM - BÓNG ĐEN 💀',
                'text': 'CẨN THẬN! Bóng đen sẽ rơi thẳng vào rổ và TRỪ ĐIỂM!\nHãy dùng tay đánh văng chúng ra ngoài màn hình.\nĐể bóng đen rơi vào rổ = Mất 5 điểm!',
                'image': None
            },
            {
                'title': 'HỆ THỐNG COMBO',
                'text': 'Hứng bóng đỏ liên tiếp (không làm rơi) để tăng Combo.\nCombo càng cao = Điểm càng nhiều!',
                'image': None
            },
            {
                'title': 'BÓNG ĐẶC BIỆT',
                'text': 'Hãy săn các quả bóng có màu lạ:\n⏱ Màu Xanh: Làm chậm thời gian\n🧲 Màu Hồng: Nam châm hút bóng\nx2 Màu Vàng: Nhân đôi điểm số',
                'image': None
            },
            {
                'title': 'SẴN SÀNG CHƯA?',
                'text': 'Đạt 10 điểm để THẮNG!\nĐừng để bóng đen rơi vào rổ!\nChúc may mắn!',
                'image': None
            }
        ]
        
        self.current_step = 0
        
    def start_tutorial(self):
        """Bắt đầu tutorial"""
        self.show_tutorial = True
        self.current_step = 0
    
    def next_step(self):
        """Chuyển sang bước tiếp theo"""
        self.current_step += 1
        if self.current_step >= len(self.tutorial_steps):
            self.complete_tutorial()
    
    def prev_step(self):
        """Quay lại bước trước"""
        if self.current_step > 0:
            self.current_step -= 1
    
    def complete_tutorial(self):
        """Hoàn thành tutorial"""
        self.show_tutorial = False
        self.first_time = False
    
    def skip_tutorial(self):
        """Bỏ qua tutorial"""
        self.show_tutorial = False
        self.first_time = False
    
    def show_hint(self, hint_text, duration=3.0):
        """Hiển thị hint tạm thời"""
        self.current_hint = hint_text
        self.hint_timer = duration
    
    def on_miss(self):
        """Gọi khi người chơi bỏ lỡ bóng"""
        self.miss_count += 1
        
        if self.miss_count == 3:
            self.show_hint("Thử đặt tay thấp hơn để bắt bóng dễ hơn!")
        elif self.miss_count == 6:
            self.show_hint("Sử dụng cả hai tay để tăng diện tích bắt!")
    
    def on_score(self):
        """Reset miss count khi ghi điểm"""
        self.miss_count = 0
    
    def update(self, dt):
        """Update hint timer"""
        if self.hint_timer > 0:
            self.hint_timer -= dt
            if self.hint_timer <= 0:
                self.current_hint = ""
    
    def get_current_step(self):
        """Lấy bước tutorial hiện tại"""
        if 0 <= self.current_step < len(self.tutorial_steps):
            return self.tutorial_steps[self.current_step]
        return None
    
    def should_show_hint(self):
        """Có nên hiện hint không"""
        return self.hint_timer > 0 and self.current_hint != ""
    
    def reset_game_stats(self):
        """Reset stats khi bắt đầu game mới"""
        self.miss_count = 0
        self.current_hint = ""
        self.hint_timer = 0