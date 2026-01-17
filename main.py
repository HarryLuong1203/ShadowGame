# main.py
import pygame
import cv2
import os
from settings import * 
from core import (
    HandModel, HandStyle, HandTracker, PhysicsManager, GameRenderer,
    ComboSystem, PowerUpSystem, ParticleSystem, TutorialSystem
)

# Game States
STATE_MENU = 0
STATE_TUTORIAL = 1
STATE_PLAYING = 2
STATE_GAMEOVER = 3
STATE_CUSTOMIZE = 4

HIGHSCORE_FILE = "highscores.txt"

class ShadowGame:
    def __init__(self):
        pygame.init()
        
        # Fullscreen & Scaled
        flags = pygame.FULLSCREEN | pygame.SCALED
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags, vsync=1)
        pygame.display.set_caption("Bàn Tay Ma Thuật")
        pygame.mouse.set_visible(True)

        self.clock = pygame.time.Clock()
        self.running = True

        # Core Systems
        self.tracker = HandTracker()
        self.physics = PhysicsManager()
        self.renderer = GameRenderer(self.screen)
        self.combo_system = ComboSystem()
        self.powerup_system = PowerUpSystem()
        self.particle_system = ParticleSystem()
        self.tutorial_system = TutorialSystem()
        
        self.particle_system.init_surface(WIDTH, HEIGHT)
        
        # Webcam
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, WIDTH)
        self.cap.set(4, HEIGHT)

        self.state = STATE_MENU
        self.score = 0
        self.time_left = GAME_DURATION
        self.high_scores = self.load_high_scores()
        
        self.current_theme = 'default'
        self.current_skin = 'default'
        self.time_scale = 1.0
        
        # --- ĐỊNH NGHĨA NÚT BẤM ---
        cx = WIDTH // 2
        cy = HEIGHT // 2
        
        # Menu
        self.btn_start_rect = pygame.Rect(cx - 120, cy + 40, 240, 70)
        self.btn_customize_rect = pygame.Rect(cx - 120, cy + 130, 240, 70)
        
        # Game Over / Customize Back
        self.btn_reset_rect = pygame.Rect(cx - 120, HEIGHT - 120, 240, 70)
        
        # Tutorial buttons (Các nút trong màn hình hướng dẫn)
        self.btn_tutorial_prev = pygame.Rect(50, HEIGHT - 100, 150, 60)  # NÚT MỚI: Quay lại
        self.btn_tutorial_next = pygame.Rect(WIDTH - 200, HEIGHT - 100, 150, 60)
        self.btn_tutorial_skip = pygame.Rect(WIDTH - 160, 30, 130, 50)

        # Tạo nút customize
        self.theme_buttons = []
        self.skin_buttons = []
        self._create_customize_buttons()

    def _create_customize_buttons(self):
        # Themes
        themes = list(THEMES.keys())
        btn_w, btn_h = 180, 50
        start_x = WIDTH // 2 - (len(themes) * (btn_w + 20)) // 2
        for i, name in enumerate(themes):
            rect = pygame.Rect(start_x + i*(btn_w+20), HEIGHT//3, btn_w, btn_h)
            self.theme_buttons.append((name, rect))
            
        # Skins
        skins = list(BALL_SKINS.keys())
        start_x = WIDTH // 2 - (len(skins) * (btn_w + 20)) // 2
        for i, name in enumerate(skins):
            rect = pygame.Rect(start_x + i*(btn_w+20), HEIGHT//2 + 30, btn_w, btn_h)
            self.skin_buttons.append((name, rect))

    def load_high_scores(self):
        scores = []
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r", encoding='utf-8') as f:
                for line in f:
                    try: scores.append(int(line.strip()))
                    except: pass
        scores.sort(reverse=True)
        return scores

    def save_score(self):
        self.high_scores.append(self.score)
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:10]
        with open(HIGHSCORE_FILE, "w", encoding='utf-8') as f:
            for s in self.high_scores: f.write(f"{s}\n")

    def start_game(self):
        """Khởi động game"""
        self.score = 0
        self.time_left = GAME_DURATION
        self.physics.reset()
        self.combo_system.reset()
        self.powerup_system.clear()
        self.particle_system.clear()
        self.tutorial_system.reset_game_stats()
        self.time_scale = 1.0
        
        # --- LOGIC TUTORIAL: Nếu là lần đầu thì hiện hướng dẫn ---
        if self.tutorial_system.first_time:
            self.state = STATE_TUTORIAL
            self.tutorial_system.start_tutorial()
        else:
            self.state = STATE_PLAYING 

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_CUSTOMIZE: self.state = STATE_MENU
                    else: self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 1. MENU
                if self.state == STATE_MENU:
                    if self.btn_start_rect.collidepoint(mouse_pos):
                        self.start_game()
                    elif self.btn_customize_rect.collidepoint(mouse_pos):
                        self.state = STATE_CUSTOMIZE
                
                # 2. TUTORIAL
                elif self.state == STATE_TUTORIAL:
                    # NÚT QUAY LẠI (Mới thêm)
                    if self.btn_tutorial_prev.collidepoint(mouse_pos):
                        self.tutorial_system.prev_step()
                    
                    # NÚT TIẾP THEO
                    elif self.btn_tutorial_next.collidepoint(mouse_pos):
                        self.tutorial_system.next_step()
                        # Nếu hết tutorial thì tự vào game
                        if not self.tutorial_system.show_tutorial:
                            self.state = STATE_PLAYING
                    
                    # NÚT BỎ QUA
                    elif self.btn_tutorial_skip.collidepoint(mouse_pos):
                        self.tutorial_system.skip_tutorial()
                        self.state = STATE_PLAYING
                
                # 3. CUSTOMIZE
                elif self.state == STATE_CUSTOMIZE:
                    for name, rect in self.theme_buttons:
                        if rect.collidepoint(mouse_pos):
                            self.current_theme = name
                            self.renderer.set_theme(name)
                    for name, rect in self.skin_buttons:
                        if rect.collidepoint(mouse_pos):
                            self.current_skin = name
                            self.renderer.set_ball_skin(name)
                    if self.btn_reset_rect.collidepoint(mouse_pos):
                        self.state = STATE_MENU
                
                # 4. GAME OVER
                elif self.state == STATE_GAMEOVER:
                    if self.btn_reset_rect.collidepoint(mouse_pos):
                        self.start_game()

    def update(self):
        success, frame = self.cap.read()
        if success:
            frame = cv2.flip(frame, 1)
            self.tracker.process(frame)
        hands_data = self.tracker.get_hand_landmarks(WIDTH, HEIGHT)
        
        # Chỉ update logic game khi đang chơi
        if self.state == STATE_PLAYING:
            dt = (1/FPS) * self.time_scale
            
            self.tutorial_system.update(dt)
            self.powerup_system.update()
            
            # Xử lý Powerup
            self.time_scale = 0.5 if self.powerup_system.has_powerup('slow_motion') else 1.0
            self.physics.set_magnet(self.powerup_system.has_powerup('magnet'))
            
            self.physics.update_hand_physics(hands_data)
            if self.physics.current_ball is None: self.physics.spawn_ball()
            self.physics.step(dt)
            
            status, powerup_type = self.physics.check_ball_status()
            
            if status == 1: # Ghi điểm
                mult = self.combo_system.add_score()
                pts = 1 * (2 if self.powerup_system.has_powerup('double_points') else 1) * mult
                self.score += pts
                
                if powerup_type: 
                    self.powerup_system.activate(powerup_type)
                    # Effect nhặt powerup
                    bx, by = self.physics.current_ball.position if self.physics.current_ball else (0,0)
                    self.particle_system.create_powerup_collect(BASKET_X+BASKET_WIDTH//2, BASKET_Y, powerup_type)
                
                # Effect ghi điểm
                self.particle_system.create_explosion(BASKET_X+BASKET_WIDTH//2, BASKET_Y, (255, 200, 50))
                self.tutorial_system.on_score()
                
            elif status == -1: # Trượt
                self.combo_system.break_combo()
                self.tutorial_system.on_miss()
            
            self.combo_system.check_timeout()
            self.combo_system.update(dt)
            
            # Update particles
            b_pos = (self.physics.current_ball.position.x, self.physics.current_ball.position.y) if self.physics.current_ball else None
            self.particle_system.update(dt, b_pos if self.combo_system.combo_count >= 5 else None)
            
            self.time_left -= dt
            if self.time_left <= 0:
                self.state = STATE_GAMEOVER
                self.save_score()
        
        # Ở các màn hình khác (Menu, Tutorial), vẫn update tay để làm nền
        else:
            self.physics.update_hand_physics(hands_data)
                
        return hands_data

    def draw(self, hands_data):
        self.renderer.clear_screen()
        m_pos = pygame.mouse.get_pos()
        
        # Vẽ rổ ở mọi nơi trừ màn hình Customize (cho đỡ rối)
        if self.state not in [STATE_CUSTOMIZE]:
            self.renderer.draw_basket()
        
        # Vẽ tay (Luôn hiện để người chơi test tay)
        for hp in hands_data:
            self.renderer.draw_organic_hand(hp, HandModel, HandStyle.REALISTIC_SHADOW)
        self.renderer.apply_shadow_effect()

        # --- VẼ GIAO DIỆN THEO TRẠNG THÁI ---
        if self.state == STATE_MENU:
            bs = self.high_scores[0] if self.high_scores else 0
            self.renderer.draw_menu(bs)
            
            hov = self.btn_start_rect.collidepoint(m_pos)
            self.renderer.draw_button("BẮT ĐẦU", self.btn_start_rect, (0, 180, 0), hov)
            
            hov = self.btn_customize_rect.collidepoint(m_pos)
            self.renderer.draw_button("CỬA HÀNG", self.btn_customize_rect, (100, 100, 220), hov)

        # --- MÀN HÌNH TUTORIAL ---
        elif self.state == STATE_TUTORIAL:
            step = self.tutorial_system.get_current_step()
            if step:
                # Vẽ bảng hướng dẫn
                self.renderer.draw_tutorial(step, self.tutorial_system.current_step, len(self.tutorial_system.tutorial_steps))
            
            # Vẽ nút QUAY LẠI (chỉ hiện nếu không phải bước đầu tiên)
            if self.tutorial_system.current_step > 0:
                hov = self.btn_tutorial_prev.collidepoint(m_pos)
                self.renderer.draw_button("QUAY LẠI", self.btn_tutorial_prev, (100, 100, 100), hov)
            
            # Vẽ nút TIẾP THEO / BẮT ĐẦU
            hov = self.btn_tutorial_next.collidepoint(m_pos)
            btn_text = "BẮT ĐẦU" if self.tutorial_system.current_step == len(self.tutorial_system.tutorial_steps) - 1 else "TIẾP THEO"
            self.renderer.draw_button(btn_text, self.btn_tutorial_next, (0, 150, 0), hov)
            
            # Vẽ nút BỎ QUA
            hov = self.btn_tutorial_skip.collidepoint(m_pos)
            self.renderer.draw_button("BỎ QUA", self.btn_tutorial_skip, (150, 50, 50), hov)

        elif self.state == STATE_CUSTOMIZE:
            t = self.renderer.font_large.render("TÙY CHỈNH GIAO DIỆN", True, self.renderer.current_theme['text'])
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 80))
            
            lbl = self.renderer.font_medium.render("Chọn Chủ Đề:", True, self.renderer.current_theme['text'])
            self.screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, HEIGHT//3 - 60))
            for name, rect in self.theme_buttons:
                sel = name == self.current_theme
                hov = rect.collidepoint(m_pos)
                col = (0, 200, 0) if sel else (120, 120, 120)
                self.renderer.draw_button(THEMES[name]['name'], rect, col, hov)
                
            lbl = self.renderer.font_medium.render("Chọn Bóng:", True, self.renderer.current_theme['text'])
            self.screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, HEIGHT//2 - 10))
            for name, rect in self.skin_buttons:
                sel = name == self.current_skin
                hov = rect.collidepoint(m_pos)
                col = (0, 200, 0) if sel else (120, 120, 120)
                self.renderer.draw_button(BALL_SKINS[name]['name'], rect, col, hov)
                
            hov = self.btn_reset_rect.collidepoint(m_pos)
            self.renderer.draw_button("QUAY LẠI", self.btn_reset_rect, (220, 100, 50), hov)

        elif self.state == STATE_PLAYING:
            self.renderer.draw_ball(self.physics.ball_shape, self.physics.ball_type, self.physics.powerup_type)
            self.particle_system.draw(self.screen)
            self.renderer.draw_hud(self.score, self.time_left, self.combo_system, self.powerup_system)
            
            # Vẽ Hint (Mẹo) nếu có
            if self.tutorial_system.should_show_hint():
                self.renderer.draw_hint(self.tutorial_system.current_hint)

        elif self.state == STATE_GAMEOVER:
            self.renderer.draw_game_over(self.score, self.high_scores, self.combo_system)
            hov = self.btn_reset_rect.collidepoint(m_pos)
            self.renderer.draw_button("CHƠI LẠI", self.btn_reset_rect, (0, 150, 250), hov)
        
        pygame.display.update()

    def run(self):
        while self.running:
            self.handle_events()
            hands_data = self.update()
            self.draw(hands_data)
            self.clock.tick(FPS)
        self.cap.release()
        pygame.quit()

if __name__ == "__main__":
    game = ShadowGame()
    game.run()