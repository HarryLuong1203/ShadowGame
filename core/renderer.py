# core/renderer.py
import pygame
import math
import time
import os
from settings import *

class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.hand_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # --- QUẢN LÝ FONT (Cải tiến) ---
        # Ưu tiên load font đẹp từ file, nếu không có thì dùng font hệ thống
        font_path = "font.ttf" # Bạn nhớ để file font.ttf cùng thư mục main.py
        
        try:
            # Cố gắng load font xịn
            self.font_large = pygame.font.Font(font_path, 70)
            self.font_medium = pygame.font.Font(font_path, 45)
            self.font_small = pygame.font.Font(font_path, 30)
            self.font_tiny = pygame.font.Font(font_path, 20)
            print("Đã load font tùy chỉnh thành công!")
        except:
            # Fallback nếu không tìm thấy file
            print("Không tìm thấy 'font.ttf'. Đang dùng font mặc định.")
            self.font_large = pygame.font.SysFont("Verdana", 60, bold=True)
            self.font_medium = pygame.font.SysFont("Verdana", 40, bold=True)
            self.font_small = pygame.font.SysFont("Verdana", 25)
            self.font_tiny = pygame.font.SysFont("Verdana", 18)
        
        self.current_theme = THEMES['default']
        self.current_skin = BALL_SKINS['default']

    def set_theme(self, theme_name):
        if theme_name in THEMES:
            self.current_theme = THEMES[theme_name]
    
    def set_ball_skin(self, skin_name):
        if skin_name in BALL_SKINS:
            self.current_skin = BALL_SKINS[skin_name]

    def clear_screen(self):
        self.screen.fill(self.current_theme['bg'])
        self.hand_surface.fill((0, 0, 0, 0))

    def draw_organic_hand(self, landmarks, hand_model, style):
        # Giữ nguyên logic vẽ tay bóng đổ (vì nó đã ổn)
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

    def draw_ball(self, ball_shape, ball_type='normal', powerup_type=None):
        """Vẽ bóng có họa tiết và xoay theo vật lý"""
        if not ball_shape:
            return
            
        pos = (int(ball_shape.body.position.x), int(ball_shape.body.position.y))
        angle = ball_shape.body.angle # Góc xoay (radian)
        radius = BALL_RADIUS
        
        # 1. Xác định màu nền bóng
        if ball_type == 'powerup' and powerup_type:
            base_color = POWERUP_TYPES[powerup_type]['color']
            # Hiệu ứng nhấp nháy cho powerup
            pulse = (math.sin(time.time() * 10) + 1) / 2 # 0 -> 1
            # Pha màu trắng vào để nhấp nháy
            base_color = tuple(min(255, int(c + pulse * 50)) for c in base_color)
        elif self.current_skin['type'] == 'rainbow':
            hue = (time.time() * 100) % 360
            base_color = self._hsv_to_rgb(hue, 1.0, 1.0)
        else:
            base_color = self.current_skin.get('color', (200, 50, 50))

        # 2. Vẽ nền bóng
        if self.current_skin['type'] == 'beach':
            # Vẽ bóng bãi biển (3 múi màu)
            colors = self.current_skin['colors']
            # Vẽ 3 phần rẻ quạt xoay theo góc
            for i in range(3):
                start_angle = angle + i * (2 * math.pi / 3)
                end_angle = start_angle + (2 * math.pi / 3)
                pygame.draw.arc(self.screen, colors[i], 
                              (pos[0]-radius, pos[1]-radius, radius*2, radius*2), 
                              start_angle, end_angle, width=radius) # width=radius để tô đặc
        else:
            # Vẽ hình tròn đặc bình thường
            pygame.draw.circle(self.screen, base_color, pos, radius)

        # 3. Vẽ họa tiết xoay (Overlay patterns)
        skin_type = self.current_skin.get('type', 'solid')
        
        if skin_type == 'basketball':
            line_color = self.current_skin['line_color']
            width = 2
            # Vẽ chữ thập (+) xoay theo góc
            dx = math.cos(angle) * radius
            dy = math.sin(angle) * radius
            pygame.draw.line(self.screen, line_color, (pos[0]-dx, pos[1]-dy), (pos[0]+dx, pos[1]+dy), width)
            
            dx2 = math.cos(angle + math.pi/2) * radius
            dy2 = math.sin(angle + math.pi/2) * radius
            pygame.draw.line(self.screen, line_color, (pos[0]-dx2, pos[1]-dy2), (pos[0]+dx2, pos[1]+dy2), width)
            
        elif skin_type == 'soccer':
            patch_color = self.current_skin['patch_color']
            # Vẽ 1 hình ngũ giác (hoặc tròn nhỏ) ở tâm và 1 cái vệ tinh xoay quanh
            # Tâm (xoay nhẹ)
            center_off_x = math.cos(angle) * 5
            center_off_y = math.sin(angle) * 5
            pygame.draw.circle(self.screen, patch_color, (pos[0]+center_off_x, pos[1]+center_off_y), 6)
            
            # Vệ tinh
            sat_x = pos[0] + math.cos(angle) * 12
            sat_y = pos[1] + math.sin(angle) * 12
            pygame.draw.circle(self.screen, patch_color, (sat_x, sat_y), 5)

        # 4. Hiệu ứng bóng đổ nhẹ (Shading)
        pygame.draw.circle(self.screen, (0, 0, 0, 40), (pos[0] + 3, pos[1] + 3), radius)
        
        # 5. Icon Powerup (nếu có)
        if ball_type == 'powerup' and powerup_type:
            symbol = POWERUP_TYPES[powerup_type]['symbol']
            sym_surf = self.font_small.render(symbol, True, (255, 255, 255))
            sym_rect = sym_surf.get_rect(center=pos)
            self.screen.blit(sym_surf, sym_rect)

    def draw_basket(self):
        """Vẽ cái rổ nhìn 'xịn' hơn"""
        color = self.current_theme['basket']
        # Màu tối hơn cho phần sau rổ
        darker_color = (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30))
        
        bx, by = BASKET_X, BASKET_Y
        bw, bh = BASKET_WIDTH, BASKET_HEIGHT
        
        # 1. Vẽ lưới (Net) - Hình thang
        # Đáy nhỏ hơn miệng
        bottom_w = bw * 0.8
        bottom_x = bx + (bw - bottom_w) / 2
        
        # Các điểm của lưới
        points = [
            (bx, by),                   # Top Left
            (bx + bw, by),              # Top Right
            (bottom_x + bottom_w, by + bh), # Bot Right
            (bottom_x, by + bh)         # Bot Left
        ]
        
        # Vẽ nền lưới (bán trong suốt)
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.polygon(s, (*color, 100), points)
        self.screen.blit(s, (0,0))
        
        # Vẽ dây lưới đan chéo
        lines_count = 6
        # Dây dọc
        for i in range(lines_count + 1):
            t = i / lines_count
            top_p = (bx + bw * t, by)
            bot_p = (bottom_x + bottom_w * t, by + bh)
            pygame.draw.line(self.screen, (200, 200, 200), top_p, bot_p, 2)
            
        # Dây ngang (cong nhẹ thì tốt, nhưng thẳng cũng ok)
        for i in range(1, 4):
            y = by + (bh / 4) * i
            # Nội suy x trái và phải
            t = i / 4
            xl = bx + (bottom_x - bx) * t
            xr = (bx + bw) + ((bottom_x + bottom_w) - (bx + bw)) * t
            pygame.draw.line(self.screen, (200, 200, 200), (xl, y), (xr, y), 2)

        # 2. Vẽ vành rổ (Rim)
        pygame.draw.rect(self.screen, darker_color, (bx - 5, by, bw + 10, 10), border_radius=5)

    def draw_button(self, text, rect, base_color, hover=False):
        """Vẽ nút bấm phong cách hoạt hình"""
        # Hiệu ứng hover: Sáng hơn và nảy lên chút
        if hover:
            color = (min(255, base_color[0]+40), min(255, base_color[1]+40), min(255, base_color[2]+40))
            draw_rect = rect.move(0, -2) # Nảy lên
        else:
            color = base_color
            draw_rect = rect

        # Bóng đổ nút
        shadow_rect = pygame.Rect(draw_rect.x, draw_rect.y + 5, draw_rect.width, draw_rect.height)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=15)

        # Thân nút
        pygame.draw.rect(self.screen, color, draw_rect, border_radius=15)
        # Viền nút
        pygame.draw.rect(self.screen, (255, 255, 255), draw_rect, 3, border_radius=15)
        
        # Text
        text_surf = self.font_medium.render(text, True, (255, 255, 255))
        # Shadow text
        text_shadow = self.font_medium.render(text, True, (0, 0, 0, 50))
        
        center_x = draw_rect.centerx - text_surf.get_width() // 2
        center_y = draw_rect.centery - text_surf.get_height() // 2
        
        self.screen.blit(text_shadow, (center_x + 2, center_y + 2))
        self.screen.blit(text_surf, (center_x, center_y))

    def draw_hud(self, score, time_left, combo_system, powerup_system):
        """Vẽ bảng điểm tự động co giãn (Tránh lọt chữ)"""
        
        # 1. Chuẩn bị text
        lbl_score = "ĐIỂM"
        lbl_time = "THỜI GIAN"
        
        val_score = str(score)
        val_time = f"{int(time_left)}s"
        
        # Render text để đo kích thước
        surf_lbl_score = self.font_tiny.render(lbl_score, True, (100, 100, 100))
        surf_val_score = self.font_medium.render(val_score, True, self.current_theme['text'])
        
        surf_lbl_time = self.font_tiny.render(lbl_time, True, (100, 100, 100))
        color_time = (220, 50, 50) if time_left < 10 else self.current_theme['text']
        surf_val_time = self.font_medium.render(val_time, True, color_time)
        
        # 2. Tính toán layout
        # Box Điểm
        box_w = 150
        box_h = 80
        padding = 20
        
        # Tính vị trí trung tâm để căn giữa màn hình
        total_w = box_w * 2 + padding
        start_x = (self.width - total_w) // 2
        
        rect_score = pygame.Rect(start_x, 20, box_w, box_h)
        rect_time = pygame.Rect(start_x + box_w + padding, 20, box_w, box_h)
        
        # 3. Vẽ nền (Panel)
        pygame.draw.rect(self.screen, self.current_theme['ui_bg'], rect_score, border_radius=15)
        pygame.draw.rect(self.screen, self.current_theme['ui_bg'], rect_time, border_radius=15)
        
        # 4. Vẽ nội dung
        # Điểm
        self.screen.blit(surf_lbl_score, (rect_score.centerx - surf_lbl_score.get_width()//2, rect_score.y + 10))
        self.screen.blit(surf_val_score, (rect_score.centerx - surf_val_score.get_width()//2, rect_score.y + 35))
        
        # Thời gian
        self.screen.blit(surf_lbl_time, (rect_time.centerx - surf_lbl_time.get_width()//2, rect_time.y + 10))
        self.screen.blit(surf_val_time, (rect_time.centerx - surf_val_time.get_width()//2, rect_time.y + 35))

        # 5. Combo (Ở giữa màn hình)
        if combo_system.should_show_combo():
            scale = combo_system.combo_scale
            # Hiệu ứng nảy: scale font size
            display_size = int(60 * scale)
            font_combo = pygame.font.Font(None, display_size) # Dùng font mặc định cho nhanh hoặc load lại nếu muốn
            # (Tốt nhất là dùng font_large đã scale nếu pygame hỗ trợ, nhưng ở đây ta vẽ đơn giản)
            
            txt = f"COMBO x{combo_system.combo_count}!"
            col_combo = (255, 150, 0)
            
            surf_combo = self.font_large.render(txt, True, col_combo)
            # Resize theo scale
            w = int(surf_combo.get_width() * scale)
            h = int(surf_combo.get_height() * scale)
            if w > 0 and h > 0:
                surf_combo = pygame.transform.scale(surf_combo, (w, h))
            
            self.screen.blit(surf_combo, (self.width//2 - surf_combo.get_width()//2, 150))

        # 6. Power-up Icons (Góc phải)
        active_pus = powerup_system.get_active_list()
        for i, (ptype, remain) in enumerate(active_pus):
            pinfo = POWERUP_TYPES[ptype]
            # Vẽ vòng tròn nền
            px = self.width - 60
            py = 150 + i * 70
            
            # Progress arc (Vòng tròn thu nhỏ dần)
            pct = remain / POWERUP_DURATION
            pygame.draw.circle(self.screen, pinfo['color'], (px, py), 25)
            pygame.draw.arc(self.screen, (255, 255, 255), (px-25, py-25, 50, 50), 0, pct * 2 * math.pi, 3)
            
            # Symbol
            sym = self.font_small.render(pinfo['symbol'], True, (255, 255, 255))
            self.screen.blit(sym, (px - sym.get_width()//2, py - sym.get_height()//2))

    def draw_menu(self, high_score):
        # Tiêu đề game
        title = "BÀN TAY MA THUẬT"
        surf = self.font_large.render(title, True, self.current_theme['text'])
        # Shadow
        shad = self.font_large.render(title, True, (0,0,0,50))
        self.screen.blit(shad, (self.width//2 - surf.get_width()//2 + 4, self.height//3 + 4))
        self.screen.blit(surf, (self.width//2 - surf.get_width()//2, self.height//3))
        
        # Điểm cao
        txt = f"Kỷ lục: {high_score}"
        surf_hs = self.font_medium.render(txt, True, (150, 150, 150))
        self.screen.blit(surf_hs, (self.width//2 - surf_hs.get_width()//2, self.height//3 + 90))

    def draw_game_over(self, current_score, high_scores, combo_system):
        # Màn hình mờ
        ov = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))
        
        # Text
        lbl = "HẾT GIỜ!"
        surf = self.font_large.render(lbl, True, (255, 100, 100))
        self.screen.blit(surf, (self.width//2 - surf.get_width()//2, 100))
        
        sc = f"Điểm của bạn: {current_score}"
        surf_sc = self.font_medium.render(sc, True, (255, 255, 255))
        self.screen.blit(surf_sc, (self.width//2 - surf_sc.get_width()//2, 180))
        
        # Bảng xếp hạng
        pygame.draw.rect(self.screen, (255, 255, 255, 20), (self.width//2 - 200, 250, 400, 250), border_radius=20)
        
        head = "--- BẢNG XẾP HẠNG ---"
        surf_head = self.font_small.render(head, True, (200, 200, 200))
        self.screen.blit(surf_head, (self.width//2 - surf_head.get_width()//2, 270))
        
        for i, s in enumerate(high_scores[:5]):
            color = (255, 215, 0) if i == 0 else (255, 255, 255) # Top 1 màu vàng
            row = f"#{i+1} ..... {s}"
            surf_row = self.font_small.render(row, True, color)
            self.screen.blit(surf_row, (self.width//2 - surf_row.get_width()//2, 320 + i*35))

    def _hsv_to_rgb(self, h, s, v):
        """Hàm phụ trợ đổi màu cầu vồng"""
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        if h < 60: r, g, b = c, x, 0
        elif h < 120: r, g, b = x, c, 0
        elif h < 180: r, g, b = 0, c, x
        elif h < 240: r, g, b = 0, x, c
        elif h < 300: r, g, b = x, 0, c
        else: r, g, b = c, 0, x
        return (int((r+m)*255), int((g+m)*255), int((b+m)*255))

    # --- CÁC HÀM MỚI BỔ SUNG CHO TUTORIAL ---
    
    def draw_tutorial(self, step_data, step_num, total_steps):
        """Vẽ hộp thoại hướng dẫn"""
        # Nền mờ toàn màn hình
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Khung chứa nội dung
        panel_width = 800
        panel_height = 400
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (250, 245, 230), rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 4, border_radius=20)
        
        # Tiêu đề
        title_surf = self.font_large.render(step_data['title'], True, (200, 50, 50))
        self.screen.blit(title_surf, (self.width//2 - title_surf.get_width()//2, panel_y + 30))
        
        # Nội dung text (Xử lý xuống dòng)
        text_lines = step_data['text'].split('\n')
        y_offset = panel_y + 120
        for line in text_lines:
            line_surf = self.font_small.render(line, True, (50, 50, 50))
            line_x = self.width // 2 - line_surf.get_width() // 2
            self.screen.blit(line_surf, (line_x, y_offset))
            y_offset += 35
        
        # Progress (Bước hiện tại / Tổng số bước)
        progress_text = f"Bước {step_num + 1} / {total_steps}"
        progress_surf = self.font_tiny.render(progress_text, True, (150, 150, 150))
        self.screen.blit(progress_surf, (self.width // 2 - progress_surf.get_width() // 2, panel_y + panel_height - 40))

    def draw_hint(self, hint_text):
        """Vẽ hint (mẹo) ở dưới cùng màn hình"""
        # Tạo text
        hint_surf = self.font_small.render(hint_text, True, (255, 255, 255))
        
        # Tạo khung nền
        hint_width = hint_surf.get_width() + 30
        hint_height = hint_surf.get_height() + 15
        hint_x = self.width // 2 - hint_width // 2
        hint_y = self.height - 80
        
        hint_rect = pygame.Rect(hint_x, hint_y, hint_width, hint_height)
        
        # Vẽ khung bán trong suốt
        s = pygame.Surface((hint_width, hint_height), pygame.SRCALPHA)
        pygame.draw.rect(s, (50, 50, 50, 200), s.get_rect(), border_radius=10)
        self.screen.blit(s, (hint_x, hint_y))
        
        # Vẽ text lên trên
        self.screen.blit(hint_surf, (hint_x + 15, hint_y + 7))