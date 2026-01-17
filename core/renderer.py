# core/renderer.py
import pygame
import math
import time
import os
import sys

from settings import (
    WIDTH, HEIGHT, BALL_RADIUS, BASKET_X, BASKET_Y, BASKET_WIDTH, BASKET_HEIGHT,
    FINGER_THICKNESS, THEMES, BALL_SKINS, POWERUP_TYPES, POWERUP_DURATION,
    COMBO_TIMEOUT, COMBO_MULTIPLIERS, BACKGROUND_IMAGE,
    NEGATIVE_BALL_COLOR, NEGATIVE_BALL_SYMBOL
)

# ===== HÀM XỬ LÝ ĐƯỜNG DẪN CHO PYINSTALLER =====
def resource_path(relative_path):
    """
    Lấy đường dẫn tuyệt đối đến resource, hoạt động cho cả dev và PyInstaller
    """
    try:
        # PyInstaller tạo temp folder và lưu path vào _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.hand_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # --- LOAD ẢNH NỀN (ĐÃ SỬA) ---
        self.background = None
        try:
            bg_path = resource_path(BACKGROUND_IMAGE)
            bg_img = pygame.image.load(bg_path)
            self.background = pygame.transform.scale(bg_img, (self.width, self.height))
            print(f"✅ Đã load ảnh nền: {BACKGROUND_IMAGE}")
        except Exception as e:
            print(f"⚠️ Không thể load ảnh nền '{BACKGROUND_IMAGE}': {e}")
            print("   → Sử dụng màu nền mặc định.")
        
        # --- QUẢN LÝ FONT (ĐÃ SỬA) ---
        font_path = resource_path("font.ttf")
        
        try:
            self.font_large = pygame.font.Font(font_path, 70)
            self.font_medium = pygame.font.Font(font_path, 45)
            self.font_small = pygame.font.Font(font_path, 30)
            self.font_tiny = pygame.font.Font(font_path, 20)
            print("✅ Đã load font tùy chỉnh thành công!")
        except Exception as e:
            print(f"⚠️ Không tìm thấy 'font.ttf': {e}")
            print("   → Đang dùng font mặc định.")
            self.font_large = pygame.font.SysFont("Verdana", 60, bold=True)
            self.font_medium = pygame.font.SysFont("Verdana", 40, bold=True)
            self.font_small = pygame.font.SysFont("Verdana", 25)
            self.font_tiny = pygame.font.SysFont("Verdana", 18)
        
        # Chỉ dùng theme mặc định
        self.current_theme = THEMES['default']
        self.current_skin = BALL_SKINS['default']

    def clear_screen(self):
        """Vẽ nền - ưu tiên ảnh, fallback về màu"""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.current_theme['bg'])
        
        self.hand_surface.fill((0, 0, 0, 0))

    def draw_organic_hand(self, landmarks, hand_model, style):
        color = style["color"]
        thickness = style["finger_thickness"]

        webbing_groups = [[0, 5, 9], [0, 9, 13], [0, 13, 17]]
        for group in webbing_groups:
            points = [landmarks[i] for i in group if i in landmarks]
            if len(points) == 3:
                pygame.draw.polygon(self.hand_surface, color, points)

        palm_points = [landmarks[i] for i in hand_model.PALM_INDICES if i in landmarks]
        if len(palm_points) >= 3:
            pygame.draw.polygon(self.hand_surface, color, palm_points)

        for point in landmarks.values():
            pygame.draw.circle(self.hand_surface, color, point, int(thickness * 0.5))

        for p1_id, p2_id in hand_model.CONNECTIONS:
            if p1_id in landmarks and p2_id in landmarks:
                pygame.draw.line(self.hand_surface, color, landmarks[p1_id], landmarks[p2_id], thickness)

    def apply_shadow_effect(self):
        self.screen.blit(self.hand_surface, (0, 0))

    def draw_ball(self, ball_obj):
        """Vẽ bóng - hỗ trợ cả bóng trừ điểm"""
        if not ball_obj or not ball_obj.body:
            return
            
        pos = (int(ball_obj.body.position.x), int(ball_obj.body.position.y))
        angle = ball_obj.body.angle
        radius = BALL_RADIUS
        
        ball_type = ball_obj.ball_type
        powerup_type = ball_obj.powerup_type
        
        # 1. Xác định màu nền bóng
        if ball_type == 'negative':
            # BÓNG TRỪ ĐIỂM - Màu đen
            base_color = NEGATIVE_BALL_COLOR
            # Hiệu ứng nhấp nháy đỏ
            pulse = (math.sin(time.time() * 8) + 1) / 2
            base_color = tuple(int(c + pulse * 100) for c in base_color)
            
        elif ball_type == 'powerup' and powerup_type:
            base_color = POWERUP_TYPES[powerup_type]['color']
            pulse = (math.sin(time.time() * 10) + 1) / 2
            base_color = tuple(min(255, int(c + pulse * 50)) for c in base_color)
        else:
            # Bóng thường
            base_color = self.current_skin.get('color', (200, 50, 50))

        # 2. Vẽ nền bóng
        pygame.draw.circle(self.screen, base_color, pos, radius)

        # 3. Bóng đổ nhẹ
        pygame.draw.circle(self.screen, (0, 0, 0, 40), (pos[0] + 3, pos[1] + 3), radius)
        
        # 4. Vẽ biểu tượng
        if ball_type == 'negative':
            # Biểu tượng bóng trừ điểm
            symbol = NEGATIVE_BALL_SYMBOL
            sym_surf = self.font_small.render(symbol, True, (255, 255, 255))
            sym_rect = sym_surf.get_rect(center=pos)
            self.screen.blit(sym_surf, sym_rect)
            
        elif ball_type == 'powerup' and powerup_type:
            # Icon Powerup
            symbol = POWERUP_TYPES[powerup_type]['symbol']
            sym_surf = self.font_small.render(symbol, True, (255, 255, 255))
            sym_rect = sym_surf.get_rect(center=pos)
            self.screen.blit(sym_surf, sym_rect)

    def draw_basket(self):
        """Vẽ cái rổ"""
        color = self.current_theme['basket']
        darker_color = (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30))
        
        bx, by = BASKET_X, BASKET_Y
        bw, bh = BASKET_WIDTH, BASKET_HEIGHT
        
        # 1. Vẽ lưới (Net) - Hình thang
        bottom_w = bw * 0.8
        bottom_x = bx + (bw - bottom_w) / 2
        
        points = [
            (bx, by),
            (bx + bw, by),
            (bottom_x + bottom_w, by + bh),
            (bottom_x, by + bh)
        ]
        
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.polygon(s, (*color, 100), points)
        self.screen.blit(s, (0,0))
        
        # Dây lưới dọc
        lines_count = 6
        for i in range(lines_count + 1):
            t = i / lines_count
            top_p = (bx + bw * t, by)
            bot_p = (bottom_x + bottom_w * t, by + bh)
            pygame.draw.line(self.screen, (200, 200, 200), top_p, bot_p, 2)
            
        # Dây ngang
        for i in range(1, 4):
            y = by + (bh / 4) * i
            t = i / 4
            xl = bx + (bottom_x - bx) * t
            xr = (bx + bw) + ((bottom_x + bottom_w) - (bx + bw)) * t
            pygame.draw.line(self.screen, (200, 200, 200), (xl, y), (xr, y), 2)

        # 2. Vẽ vành rổ (Rim)
        pygame.draw.rect(self.screen, darker_color, (bx - 5, by, bw + 10, 10), border_radius=5)

    def draw_button(self, text, rect, base_color, hover=False):
        """Vẽ nút bấm"""
        if hover:
            color = (min(255, base_color[0]+40), min(255, base_color[1]+40), min(255, base_color[2]+40))
            draw_rect = rect.move(0, -2)
        else:
            color = base_color
            draw_rect = rect

        shadow_rect = pygame.Rect(draw_rect.x, draw_rect.y + 5, draw_rect.width, draw_rect.height)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=15)

        pygame.draw.rect(self.screen, color, draw_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), draw_rect, 3, border_radius=15)
        
        text_surf = self.font_medium.render(text, True, (255, 255, 255))
        text_shadow = self.font_medium.render(text, True, (0, 0, 0, 50))
        
        center_x = draw_rect.centerx - text_surf.get_width() // 2
        center_y = draw_rect.centery - text_surf.get_height() // 2
        
        self.screen.blit(text_shadow, (center_x + 2, center_y + 2))
        self.screen.blit(text_surf, (center_x, center_y))

    def draw_hud(self, score, time_left, combo_system, powerup_system):
        """Vẽ bảng điểm"""
        lbl_score = "ĐIỂM"
        lbl_time = "THỜI GIAN"
        
        val_score = str(score)
        val_time = f"{int(time_left)}s"
        
        surf_lbl_score = self.font_tiny.render(lbl_score, True, (100, 100, 100))
        surf_val_score = self.font_medium.render(val_score, True, self.current_theme['text'])
        
        surf_lbl_time = self.font_tiny.render(lbl_time, True, (100, 100, 100))
        color_time = (220, 50, 50) if time_left < 10 else self.current_theme['text']
        surf_val_time = self.font_medium.render(val_time, True, color_time)
        
        box_w = 150
        box_h = 80
        padding = 20
        
        total_w = box_w * 2 + padding
        start_x = (self.width - total_w) // 2
        
        rect_score = pygame.Rect(start_x, 20, box_w, box_h)
        rect_time = pygame.Rect(start_x + box_w + padding, 20, box_w, box_h)
        
        pygame.draw.rect(self.screen, self.current_theme['ui_bg'], rect_score, border_radius=15)
        pygame.draw.rect(self.screen, self.current_theme['ui_bg'], rect_time, border_radius=15)
        
        self.screen.blit(surf_lbl_score, (rect_score.centerx - surf_lbl_score.get_width()//2, rect_score.y + 10))
        self.screen.blit(surf_val_score, (rect_score.centerx - surf_val_score.get_width()//2, rect_score.y + 35))
        
        self.screen.blit(surf_lbl_time, (rect_time.centerx - surf_lbl_time.get_width()//2, rect_time.y + 10))
        self.screen.blit(surf_val_time, (rect_time.centerx - surf_val_time.get_width()//2, rect_time.y + 35))

        # Combo
        if combo_system.should_show_combo():
            scale = combo_system.combo_scale
            txt = f"COMBO x{combo_system.combo_count}!"
            col_combo = (255, 150, 0)
            
            surf_combo = self.font_large.render(txt, True, col_combo)
            w = int(surf_combo.get_width() * scale)
            h = int(surf_combo.get_height() * scale)
            if w > 0 and h > 0:
                surf_combo = pygame.transform.scale(surf_combo, (w, h))
            
            self.screen.blit(surf_combo, (self.width//2 - surf_combo.get_width()//2, 150))

        # Power-up Icons
        active_pus = powerup_system.get_active_list()
        for i, (ptype, remain) in enumerate(active_pus):
            pinfo = POWERUP_TYPES[ptype]
            px = self.width - 60
            py = 150 + i * 70
            
            pct = remain / POWERUP_DURATION
            pygame.draw.circle(self.screen, pinfo['color'], (px, py), 25)
            pygame.draw.arc(self.screen, (255, 255, 255), (px-25, py-25, 50, 50), 0, pct * 2 * math.pi, 3)
            
            sym = self.font_small.render(pinfo['symbol'], True, (255, 255, 255))
            self.screen.blit(sym, (px - sym.get_width()//2, py - sym.get_height()//2))

    def draw_menu_simple(self):
        """Menu đơn giản - chỉ có ảnh nền và nút bấm"""
        pass  # Không vẽ gì cả, chỉ để nền hiển thị

    def draw_win_screen(self, final_score):
        """Màn hình CHIẾN THẮNG"""
        ov = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))
        
        # Tiêu đề THẮNG
        lbl = "CHIẾN THẮNG! 🎉"
        surf = self.font_large.render(lbl, True, (100, 255, 100))
        self.screen.blit(surf, (self.width//2 - surf.get_width()//2, 150))
        
        # Điểm số
        sc = f"Bạn đã đạt {final_score} điểm!"
        surf_sc = self.font_medium.render(sc, True, (255, 255, 255))
        self.screen.blit(surf_sc, (self.width//2 - surf_sc.get_width()//2, 250))
        
        # Thông điệp
        msg = "Xuất sắc! Bạn đã hoàn thành thử thách!"
        surf_msg = self.font_small.render(msg, True, (200, 200, 200))
        self.screen.blit(surf_msg, (self.width//2 - surf_msg.get_width()//2, 320))

    def draw_game_over_simple(self, final_score):
        """Màn hình THUA - đơn giản hóa"""
        ov = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))
        
        # Tiêu đề
        lbl = "HẾT GIỜ!"
        surf = self.font_large.render(lbl, True, (255, 100, 100))
        self.screen.blit(surf, (self.width//2 - surf.get_width()//2, 150))
        
        # Điểm số
        sc = f"Điểm của bạn: {final_score}"
        surf_sc = self.font_medium.render(sc, True, (255, 255, 255))
        self.screen.blit(surf_sc, (self.width//2 - surf_sc.get_width()//2, 250))
        
        # Thông điệp
        msg = "Cố gắng hơn lần sau nhé!"
        surf_msg = self.font_small.render(msg, True, (200, 200, 200))
        self.screen.blit(surf_msg, (self.width//2 - surf_msg.get_width()//2, 320))

    def draw_tutorial(self, step_data, step_num, total_steps):
        """Vẽ hộp thoại hướng dẫn"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        panel_width = 800
        panel_height = 400
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (250, 245, 230), rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 4, border_radius=20)
        
        title_surf = self.font_large.render(step_data['title'], True, (200, 50, 50))
        self.screen.blit(title_surf, (self.width//2 - title_surf.get_width()//2, panel_y + 30))
        
        text_lines = step_data['text'].split('\n')
        y_offset = panel_y + 120
        for line in text_lines:
            line_surf = self.font_small.render(line, True, (50, 50, 50))
            line_x = self.width // 2 - line_surf.get_width() // 2
            self.screen.blit(line_surf, (line_x, y_offset))
            y_offset += 35
        
        progress_text = f"Bước {step_num + 1} / {total_steps}"
        progress_surf = self.font_tiny.render(progress_text, True, (150, 150, 150))
        self.screen.blit(progress_surf, (self.width // 2 - progress_surf.get_width() // 2, panel_y + panel_height - 40))

    def draw_hint(self, hint_text):
        """Vẽ hint ở dưới cùng màn hình"""
        hint_surf = self.font_small.render(hint_text, True, (255, 255, 255))
        
        hint_width = hint_surf.get_width() + 30
        hint_height = hint_surf.get_height() + 15
        hint_x = self.width // 2 - hint_width // 2
        hint_y = self.height - 80
        
        hint_rect = pygame.Rect(hint_x, hint_y, hint_width, hint_height)
        
        s = pygame.Surface((hint_width, hint_height), pygame.SRCALPHA)
        pygame.draw.rect(s, (50, 50, 50, 200), s.get_rect(), border_radius=10)
        self.screen.blit(s, (hint_x, hint_y))
        
        self.screen.blit(hint_surf, (hint_x + 15, hint_y + 7))