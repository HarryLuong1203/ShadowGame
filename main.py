# main.py
import pygame
import cv2
import os
from settings import (
    WIDTH, HEIGHT, FPS, GAME_DURATION, WIN_SCORE,
    BASKET_X, BASKET_Y, BASKET_WIDTH, BASKET_HEIGHT,
    POWERUP_SPAWN_CHANCE, NEGATIVE_BALL_CHANCE, NEGATIVE_BALL_PENALTY,
    NEGATIVE_BALL_COLOR, NEGATIVE_BALL_SYMBOL
)
from core import (
    HandModel, HandStyle, HandTracker, PhysicsManager, GameRenderer,
    ComboSystem, PowerUpSystem, ParticleSystem, TutorialSystem
)

# Game States
STATE_MENU = 0
STATE_TUTORIAL = 1
STATE_PLAYING = 2
STATE_GAMEOVER = 3
STATE_WIN = 4  # Thêm trạng thái THẮNG

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
        
        self.time_scale = 1.0
        
        # --- ĐỊNH NGHĨA NÚT BẤM ---
        cx = WIDTH // 2
        cy = HEIGHT // 2
        
        # Menu
        self.btn_start_rect = pygame.Rect(cx - 120, cy + 40, 240, 70)
        
        # Game Over
        self.btn_reset_rect = pygame.Rect(cx - 120, HEIGHT - 120, 240, 70)
        
        # Tutorial buttons
        self.btn_tutorial_prev = pygame.Rect(50, HEIGHT - 100, 150, 60)
        self.btn_tutorial_next = pygame.Rect(WIDTH - 200, HEIGHT - 100, 150, 60)
        self.btn_tutorial_skip = pygame.Rect(WIDTH - 160, 30, 130, 50)

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
        
        # Logic tutorial
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
                    self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # MENU
                if self.state == STATE_MENU:
                    if self.btn_start_rect.collidepoint(mouse_pos):
                        self.start_game()
                
                # TUTORIAL
                elif self.state == STATE_TUTORIAL:
                    if self.btn_tutorial_prev.collidepoint(mouse_pos):
                        self.tutorial_system.prev_step()
                    
                    elif self.btn_tutorial_next.collidepoint(mouse_pos):
                        self.tutorial_system.next_step()
                        if not self.tutorial_system.show_tutorial:
                            self.state = STATE_PLAYING
                    
                    elif self.btn_tutorial_skip.collidepoint(mouse_pos):
                        self.tutorial_system.skip_tutorial()
                        self.state = STATE_PLAYING
                
                # GAME OVER / WIN
                elif self.state == STATE_GAMEOVER or self.state == STATE_WIN:
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
            
            # Spawn bóng nếu không có bóng nào
            if len(self.physics.get_all_balls()) == 0:
                self.physics.spawn_ball()
            
            self.physics.step(dt)
            
            # Kiểm tra trạng thái TẤT CẢ bóng
            results = self.physics.check_balls_status()
            
            for status, ball_type, powerup_type in results:
                if status == 1:  # Vào rổ
                    if ball_type == 'negative':
                        # BÓNG TRỪ ĐIỂM - Không cho điểm âm
                        self.score = max(0, self.score + NEGATIVE_BALL_PENALTY)
                        self.combo_system.break_combo()
                        # Hiệu ứng âm thanh/particle tiêu cực
                        self.particle_system.create_explosion(
                            BASKET_X + BASKET_WIDTH//2, 
                            BASKET_Y, 
                            NEGATIVE_BALL_COLOR
                        )
                        self.tutorial_system.show_hint("BỊ TRỪ ĐIỂM! Đánh văng bóng đen!", 2.0)
                    else:
                        # Bóng thường hoặc powerup - GHI ĐIỂM
                        # ===== SỬA LẠI LOGIC TÍNH ĐIỂM =====
                        combo_mult = self.combo_system.add_score()  # Lấy combo multiplier
                        base_points = 1 * combo_mult  # Tính điểm cơ bản với combo
                        
                        # Áp dụng x2 SAU KHI đã tính combo
                        if self.powerup_system.has_powerup('double_points'):
                            pts = base_points * 2  # Nhân đôi điểm
                        else:
                            pts = base_points
                        
                        self.score += pts
                        
                        if powerup_type: 
                            self.powerup_system.activate(powerup_type)
                            self.particle_system.create_powerup_collect(
                                BASKET_X + BASKET_WIDTH//2, 
                                BASKET_Y, 
                                powerup_type
                            )
                        
                        # Effect ghi điểm
                        self.particle_system.create_explosion(
                            BASKET_X + BASKET_WIDTH//2, 
                            BASKET_Y, 
                            (255, 200, 50)
                        )
                        self.tutorial_system.on_score()
                
                elif status == -1:  # Ra ngoài
                    if ball_type == 'negative':
                        # Đánh văng bóng đen thành công - KHÔNG MẤT ĐIỂM
                        pass
                    else:
                        # Mất bóng thường/powerup
                        self.combo_system.break_combo()
                        self.tutorial_system.on_miss()
            
            self.combo_system.check_timeout()
            self.combo_system.update(dt)
            
            # Update particles
            all_balls = self.physics.get_all_balls()
            b_pos = None
            if all_balls and self.combo_system.combo_count >= 5:
                # Lấy bóng đầu tiên làm vị trí vệt sao
                b_pos = (all_balls[0].body.position.x, all_balls[0].body.position.y)
            
            self.particle_system.update(dt, b_pos)
            
            # Kiểm tra điều kiện THẮNG
            if self.score >= WIN_SCORE:
                self.state = STATE_WIN
            
            # Kiểm tra hết thời gian (THUA)
            self.time_left -= dt
            if self.time_left <= 0:
                self.state = STATE_GAMEOVER
        
        # Ở các màn hình khác, vẫn update tay để làm nền
        else:
            self.physics.update_hand_physics(hands_data)
                
        return hands_data

    def draw(self, hands_data):
        self.renderer.clear_screen()
        m_pos = pygame.mouse.get_pos()
        
        # Vẽ rổ ở mọi nơi trừ menu
        if self.state not in [STATE_MENU]:
            self.renderer.draw_basket()
        
        # Vẽ tay (Luôn hiện để người chơi test tay)
        for hp in hands_data:
            self.renderer.draw_organic_hand(hp, HandModel, HandStyle.REALISTIC_SHADOW)
        self.renderer.apply_shadow_effect()

        # --- VẼ GIAO DIỆN THEO TRẠNG THÁI ---
        if self.state == STATE_MENU:
            self.renderer.draw_menu_simple()
            
            hov = self.btn_start_rect.collidepoint(m_pos)
            self.renderer.draw_button("BẮT ĐẦU", self.btn_start_rect, (0, 180, 0), hov)

        elif self.state == STATE_TUTORIAL:
            step = self.tutorial_system.get_current_step()
            if step:
                self.renderer.draw_tutorial(step, self.tutorial_system.current_step, len(self.tutorial_system.tutorial_steps))
            
            if self.tutorial_system.current_step > 0:
                hov = self.btn_tutorial_prev.collidepoint(m_pos)
                self.renderer.draw_button("QUAY LẠI", self.btn_tutorial_prev, (100, 100, 100), hov)
            
            hov = self.btn_tutorial_next.collidepoint(m_pos)
            btn_text = "BẮT ĐẦU" if self.tutorial_system.current_step == len(self.tutorial_system.tutorial_steps) - 1 else "TIẾP THEO"
            self.renderer.draw_button(btn_text, self.btn_tutorial_next, (0, 150, 0), hov)
            
            hov = self.btn_tutorial_skip.collidepoint(m_pos)
            self.renderer.draw_button("BỎ QUA", self.btn_tutorial_skip, (150, 50, 50), hov)

        elif self.state == STATE_PLAYING:
            # Vẽ TẤT CẢ bóng
            for ball in self.physics.get_all_balls():
                self.renderer.draw_ball(ball)
            
            self.particle_system.draw(self.screen)
            self.renderer.draw_hud(self.score, self.time_left, self.combo_system, self.powerup_system)
            
            if self.tutorial_system.should_show_hint():
                self.renderer.draw_hint(self.tutorial_system.current_hint)

        elif self.state == STATE_WIN:
            # Màn hình CHIẾN THẮNG
            self.renderer.draw_win_screen(self.score)
            hov = self.btn_reset_rect.collidepoint(m_pos)
            self.renderer.draw_button("CHƠI LẠI", self.btn_reset_rect, (0, 200, 0), hov)

        elif self.state == STATE_GAMEOVER:
            # Màn hình THUA (hết giờ)
            self.renderer.draw_game_over_simple(self.score)
            hov = self.btn_reset_rect.collidepoint(m_pos)
            self.renderer.draw_button("CHƠI LẠI", self.btn_reset_rect, (200, 100, 0), hov)
        
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