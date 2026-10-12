# giao diện thi đấu 2 agent sokoban đối kháng bằng pygame
import os
import sys
import time
import pygame

# thêm thư mục hiện tại vào đường dẫn
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib
import importlib.util
from two_agent.game_env_2p import SokobanTwoPlayerEnv

def load_agent_module(identifier):
    # nếu đã là module
    if hasattr(identifier, 'get_action') or hasattr(identifier, '__file__'):
        return identifier

    # trường hợp truyền đường dẫn file .py
    if identifier.endswith('.py') or os.path.sep in identifier or '/' in identifier or os.path.exists(identifier):
        file_path = os.path.abspath(identifier)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Khong tim thay file agent tai: {identifier}")
        mod_name = os.path.splitext(os.path.basename(file_path))[0]
        # thêm thư mục chứa file vào sys.path để module import file phụ nếu có
        file_dir = os.path.dirname(file_path)
        if file_dir not in sys.path:
            sys.path.insert(0, file_dir)
        spec = importlib.util.spec_from_file_location(mod_name, file_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    # trường hợp truyền tên module theo chuẩn python
    return importlib.import_module(identifier)

class SokobanTwoPlayerGUI:
    def __init__(self, map_path='maps/map_competitive.txt', max_steps=60, player1_mod='two_agent.player1', player2_mod='two_agent.player2', ask_steps=False):
        pygame.init()
        pygame.display.set_caption("Sokoban Competitive 2-Agent - AI Midterm")

        self.map_path = map_path
        self.max_steps = max_steps
        self.env = SokobanTwoPlayerEnv(map_path, max_steps=max_steps)

        # khung nhập số bước n ngay trên cửa sổ game (yêu cầu 6)
        self.entering_n = ask_steps
        self.n_input = str(self.env.max_steps)

        # nạp thuật toán cho 2 agent từ file hoặc module riêng biệt
        self.p1_module_name = str(player1_mod)
        self.p2_module_name = str(player2_mod)
        self.p1 = load_agent_module(player1_mod)
        self.p2 = load_agent_module(player2_mod)
        self.name1 = getattr(self.p1, 'NAME', 'Agent 1')
        self.name2 = getattr(self.p2, 'NAME', 'Agent 2')

        # kích thước lưới và cửa sổ
        self.tile_size = 48
        self.sidebar_width = 300
        self.grid_width = self.env.width * self.tile_size
        self.grid_height = self.env.height * self.tile_size

        self.screen_width = max(720, self.grid_width + self.sidebar_width)
        self.screen_height = max(520, self.grid_height + 40)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        # cài đặt font tương thích hệ thống
        try:
            self.font_large = pygame.font.SysFont('arial', 20, bold=True)
            self.font_medium = pygame.font.SysFont('arial', 15)
            self.font_small = pygame.font.SysFont('arial', 12)
        except Exception:
            self.font_large = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 18)
            self.font_small = pygame.font.Font(None, 15)

        # bảng màu giao diện
        self.color_bg = (24, 26, 33)
        self.color_sidebar = (35, 38, 48)
        self.color_wall = (65, 70, 85)
        self.color_floor = (45, 48, 60)
        self.color_grid_line = (55, 58, 72)
        self.color_target = (142, 68, 173)

        # màu cho từng agent và hộp tương ứng
        self.color_agent1 = (41, 128, 185)    # xanh dương
        self.color_agent2 = (231, 76, 60)     # đỏ cam
        self.color_box_neutral = (211, 142, 58) # hộp chưa thuộc về ai
        self.color_box_p1 = (52, 152, 219)     # hộp do agent 1 chiếm
        self.color_box_p2 = (235, 87, 87)      # hộp do agent 2 chiếm

        self.color_text = (240, 240, 240)
        self.color_text_muted = (160, 165, 180)

        # trạng thái điều khiển
        self.is_paused = True
        self.step_delay = 400
        self.last_step_time = 0

        # thời gian suy nghĩ của từng agent (ms)
        self.time_agent1 = 0
        self.time_agent2 = 0
        self.last_act1 = 'None'
        self.last_act2 = 'None'

    def _call_agent(self, mod, agent_id, state):
        # hỗ trợ các giao thức gọi khác nhau từ các nhóm sinh viên
        if hasattr(mod, 'get_action'):
            try:
                return mod.get_action(agent_id, state)
            except TypeError:
                return mod.get_action(state)
        elif hasattr(mod, f'Player{agent_id}'):
            cls = getattr(mod, f'Player{agent_id}')
            return cls(agent_id).get_action(state)
        elif hasattr(mod, 'Player'):
            cls = getattr(mod, 'Player')
            try:
                return cls(agent_id).get_action(state)
            except TypeError:
                return cls().get_action(state)
        return 'Wait'

    def step_game(self):
        # gọi thuật toán của 2 agent để tính nước đi đồng thời
        if self.env.is_game_over():
            return

        state = self.env.get_state()

        # tính toán thời gian của agent 1
        t1_start = time.time()
        act1 = self._call_agent(self.p1, 1, state)
        self.time_agent1 = round((time.time() - t1_start) * 1000, 2)
        self.last_act1 = act1

        # tính toán thời gian của agent 2
        t2_start = time.time()
        act2 = self._call_agent(self.p2, 2, state)
        self.time_agent2 = round((time.time() - t2_start) * 1000, 2)
        self.last_act2 = act2

        # thực hiện bước đi đồng thời
        self.env.step(act1, act2)

    def undo_game(self):
        # lùi lại 1 bước
        self.env.undo()

    def reset_game(self):
        # bắt đầu lại trận đấu
        self.env.reset()
        self.is_paused = True
        self.time_agent1 = 0
        self.time_agent2 = 0
        self.last_act1 = 'None'
        self.last_act2 = 'None'

    def set_max_steps(self, n):
        # cập nhật số bước n do người dùng nhập và chơi lại từ đầu
        self.max_steps = max(1, n)
        self.env.max_steps = self.max_steps
        self.reset_game()

    def handle_n_input(self, event):
        # xử lý phím khi đang nhập số bước n
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.n_input.isdigit() and int(self.n_input) > 0:
                self.set_max_steps(int(self.n_input))
                self.entering_n = False
        elif event.key == pygame.K_ESCAPE:
            self.n_input = str(self.env.max_steps)
            self.entering_n = False
        elif event.key == pygame.K_BACKSPACE:
            self.n_input = self.n_input[:-1]
        elif event.unicode.isdigit() and len(self.n_input) < 4:
            self.n_input += event.unicode

    def draw_n_input_modal(self):
        # hộp thoại nhập số bước n
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((12, 15, 22, 220))
        self.screen.blit(overlay, (0, 0))

        modal_w, modal_h = 400, 200
        modal_x = (self.screen_width - modal_w) // 2
        modal_y = (self.screen_height - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        pygame.draw.rect(self.screen, (28, 32, 44), modal_rect, border_radius=12)
        pygame.draw.rect(self.screen, (241, 196, 15), modal_rect, width=2, border_radius=12)

        title = self.font_large.render("NHAP SO BUOC THI DAU n", True, (241, 196, 15))
        self.screen.blit(title, (modal_x + (modal_w - title.get_width()) // 2, modal_y + 20))

        box_rect = pygame.Rect(modal_x + 120, modal_y + 70, 160, 44)
        pygame.draw.rect(self.screen, (45, 48, 60), box_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 210), box_rect, width=2, border_radius=8)
        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        val = self.font_large.render(self.n_input + cursor, True, (255, 255, 255))
        self.screen.blit(val, (box_rect.x + (box_rect.w - val.get_width()) // 2, box_rect.y + 10))

        hint = self.font_small.render("Go so nguyen duong roi nhan Enter  |  Esc: huy", True, (180, 185, 200))
        self.screen.blit(hint, (modal_x + (modal_w - hint.get_width()) // 2, modal_y + 140))

    def draw_board(self):
        offset_x = 20
        offset_y = 20

        # vẽ lưới sàn và tường
        for r in range(self.env.height):
            for c in range(self.env.width):
                rect = pygame.Rect(offset_x + c * self.tile_size, offset_y + r * self.tile_size, self.tile_size, self.tile_size)
                pos = (r, c)

                if pos in self.env.walls:
                    pygame.draw.rect(self.screen, self.color_wall, rect, border_radius=4)
                    pygame.draw.rect(self.screen, (85, 90, 110), rect, width=2, border_radius=4)
                else:
                    pygame.draw.rect(self.screen, self.color_floor, rect)
                    pygame.draw.rect(self.screen, self.color_grid_line, rect, width=1)

                    if pos in self.env.targets:
                        # vẽ vị trí đích
                        pygame.draw.circle(self.screen, self.color_target, rect.center, 7)
                        pygame.draw.circle(self.screen, (200, 150, 220), rect.center, 3)

        # vẽ các hộp với màu sắc phân biệt theo chủ sở hữu
        for b in self.env.boxes:
            r, c = b
            rect = pygame.Rect(offset_x + c * self.tile_size + 5, offset_y + r * self.tile_size + 5, self.tile_size - 10, self.tile_size - 10)
            owner = self.env.box_owners.get(b, None)

            if b in self.env.targets and owner == 1:
                box_col = self.color_box_p1
                border_col = (130, 205, 255)
            elif b in self.env.targets and owner == 2:
                box_col = self.color_box_p2
                border_col = (255, 160, 160)
            else:
                box_col = self.color_box_neutral
                border_col = (255, 220, 150)

            pygame.draw.rect(self.screen, box_col, rect, border_radius=5)
            pygame.draw.rect(self.screen, border_col, rect, width=2, border_radius=5)

            # đánh dấu nhãn chủ sở hữu lên mặt hộp
            if owner == 1 and b in self.env.targets:
                label = self.font_small.render("P1", True, (255, 255, 255))
                self.screen.blit(label, (rect.centerx - 7, rect.centery - 6))
            elif owner == 2 and b in self.env.targets:
                label = self.font_small.render("P2", True, (255, 255, 255))
                self.screen.blit(label, (rect.centerx - 7, rect.centery - 6))

        # vẽ agent 1 (xanh dương)
        if self.env.agent1_pos is not None:
            r, c = self.env.agent1_pos
            center = (offset_x + c * self.tile_size + self.tile_size // 2, offset_y + r * self.tile_size + self.tile_size // 2)
            pygame.draw.circle(self.screen, self.color_agent1, center, self.tile_size // 2 - 6)
            pygame.draw.circle(self.screen, (255, 255, 255), center, self.tile_size // 2 - 6, width=2)
            txt1 = self.font_small.render("1", True, (255, 255, 255))
            self.screen.blit(txt1, (center[0] - 4, center[1] - 6))

        # vẽ agent 2 (đỏ cam)
        if self.env.agent2_pos is not None:
            r, c = self.env.agent2_pos
            center = (offset_x + c * self.tile_size + self.tile_size // 2, offset_y + r * self.tile_size + self.tile_size // 2)
            pygame.draw.circle(self.screen, self.color_agent2, center, self.tile_size // 2 - 6)
            pygame.draw.circle(self.screen, (255, 255, 255), center, self.tile_size // 2 - 6, width=2)
            txt2 = self.font_small.render("2", True, (255, 255, 255))
            self.screen.blit(txt2, (center[0] - 4, center[1] - 6))

    def draw_sidebar(self):
        sb_x = self.screen_width - self.sidebar_width + 10
        sb_y = 20
        sb_w = self.sidebar_width - 30
        sb_h = self.screen_height - 40

        panel_rect = pygame.Rect(sb_x, sb_y, sb_w, sb_h)
        pygame.draw.rect(self.screen, self.color_sidebar, panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (60, 65, 80), panel_rect, width=2, border_radius=8)

        cur_y = sb_y + 15
        line_spacing = 22

        # tiêu đề
        title = self.font_large.render("COMPETITIVE 2P", True, (241, 196, 15))
        self.screen.blit(title, (sb_x + 15, cur_y))
        cur_y += 32

        # số bước
        txt_step = self.font_medium.render(f"Buoc di: {self.env.current_step} / {self.env.max_steps}", True, self.color_text)
        self.screen.blit(txt_step, (sb_x + 15, cur_y))
        cur_y += line_spacing

        # tỷ số
        s1, s2 = self.env.get_scores()
        txt_s1 = self.font_medium.render(f"Agent 1 ({self.name1}): {s1} hop", True, self.color_agent1)
        self.screen.blit(txt_s1, (sb_x + 15, cur_y))
        cur_y += line_spacing

        txt_s2 = self.font_medium.render(f"Agent 2 ({self.name2}): {s2} hop", True, self.color_agent2)
        self.screen.blit(txt_s2, (sb_x + 15, cur_y))
        cur_y += 28

        # trạng thái kết quả trận đấu
        if self.env.is_game_over():
            winner = self.env.get_winner()
            if winner == 1:
                res_txt = f"Ket qua: Agent 1 ({self.name1}) Thang!"
                res_col = self.color_agent1
            elif winner == 2:
                res_txt = f"Ket qua: Agent 2 ({self.name2}) Thang!"
                res_col = self.color_agent2
            else:
                res_txt = "Ket qua: Hoa nhau!"
                res_col = (241, 196, 15)
            self.screen.blit(self.font_large.render(res_txt, True, res_col), (sb_x + 15, cur_y))
        else:
            status_txt = "Tam dung" if self.is_paused else "Dang thi dau"
            col = (255, 180, 100) if self.is_paused else (100, 220, 255)
            self.screen.blit(self.font_medium.render(f"Trang thai: {status_txt}", True, col), (sb_x + 15, cur_y))
        cur_y += 30

        # thời gian suy nghĩ (< 1000ms)
        self.screen.blit(self.font_medium.render("Thoi gian moi buoc (<1000ms):", True, self.color_text), (sb_x + 15, cur_y))
        cur_y += 20
        self.screen.blit(self.font_small.render(f"A1: {self.time_agent1} ms ({self.last_act1})", True, self.color_text_muted), (sb_x + 15, cur_y))
        cur_y += 18
        self.screen.blit(self.font_small.render(f"A2: {self.time_agent2} ms ({self.last_act2})", True, self.color_text_muted), (sb_x + 15, cur_y))
        cur_y += 26

        # chú thích màu hộp
        self.screen.blit(self.font_medium.render("Quy uoc mau hop:", True, (241, 196, 15)), (sb_x + 15, cur_y))
        cur_y += 20
        self.screen.blit(self.font_small.render("- Xanh: Diem cua Agent 1", True, self.color_box_p1), (sb_x + 15, cur_y))
        cur_y += 18
        self.screen.blit(self.font_small.render("- Do:   Diem cua Agent 2", True, self.color_box_p2), (sb_x + 15, cur_y))
        cur_y += 18
        self.screen.blit(self.font_small.render("- Vang: Hop chua vao dich", True, self.color_box_neutral), (sb_x + 15, cur_y))
        cur_y += 26

        # hướng dẫn phím
        self.screen.blit(self.font_medium.render("Dieu khien:", True, self.color_text), (sb_x + 15, cur_y))
        cur_y += 20
        guides = [
            ("Space", "Tam dung / Chay tiep"),
            ("Mui ten ->", "Tien 1 buoc"),
            ("Mui ten <-", "Lui 1 buoc (undo)"),
            ("Phim R", "Bat dau lai"),
            ("Phim N", "Nhap lai so buoc n")
        ]
        for k, v in guides:
            self.screen.blit(self.font_small.render(f"- {k}: {v}", True, self.color_text_muted), (sb_x + 15, cur_y))
            cur_y += 18

    def draw_game_over_modal(self):
        if not self.env.is_game_over():
            return

        offset_x = 20
        offset_y = 20
        board_w = self.env.width * self.tile_size
        board_h = self.env.height * self.tile_size

        # Lớp phủ làm mờ nền bàn cờ
        overlay = pygame.Surface((board_w, board_h), pygame.SRCALPHA)
        overlay.fill((12, 15, 22, 215))
        self.screen.blit(overlay, (offset_x, offset_y))

        # Kích thước modal thông báo
        modal_w = min(440, board_w - 30)
        modal_h = 240
        modal_x = offset_x + (board_w - modal_w) // 2
        modal_y = offset_y + (board_h - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        # Hộp modal với viền sáng
        pygame.draw.rect(self.screen, (28, 32, 44), modal_rect, border_radius=12)
        pygame.draw.rect(self.screen, (90, 105, 135), modal_rect, width=2, border_radius=12)

        winner = self.env.get_winner()
        s1, s2 = self.env.get_scores()

        # Tiêu đề kết thúc
        title_surf = self.font_large.render("TRAN DAU KET THUC", True, (241, 196, 15))
        self.screen.blit(title_surf, (modal_x + (modal_w - title_surf.get_width()) // 2, modal_y + 18))

        # Người chiến thắng
        if winner == 1:
            winner_text = f"AGENT 1 ({self.name1}) CHIEN THANG!"
            winner_color = (65, 175, 245)
        elif winner == 2:
            winner_text = f"AGENT 2 ({self.name2}) CHIEN THANG!"
            winner_color = (245, 95, 85)
        else:
            winner_text = "KET QUA: HOA NHAU!"
            winner_color = (241, 196, 15)

        win_surf = self.font_large.render(winner_text, True, winner_color)
        self.screen.blit(win_surf, (modal_x + (modal_w - win_surf.get_width()) // 2, modal_y + 58))

        # Tỷ số chung cuộc
        score_text = f"Ty so:  Agent 1 ({s1} hop)  -  ({s2} hop) Agent 2"
        score_surf = self.font_medium.render(score_text, True, (240, 240, 240))
        self.screen.blit(score_surf, (modal_x + (modal_w - score_surf.get_width()) // 2, modal_y + 100))

        # Lý do kết thúc trận đấu: luôn là đủ n bước theo đề
        reason_text = f"Da du n = {self.env.max_steps} buoc. Ben nhieu hop tren dich hon thang."
        reason_surf = self.font_small.render(reason_text, True, (160, 170, 190))
        self.screen.blit(reason_surf, (modal_x + (modal_w - reason_surf.get_width()) // 2, modal_y + 138))

        # Đường kẻ phân cách
        pygame.draw.line(self.screen, (55, 62, 80), (modal_x + 25, modal_y + 172), (modal_x + modal_w - 25, modal_y + 172), 1)

        # Hướng dẫn thao tác
        hint_text = "[R]: Bat dau lai  |  [N]: Doi so buoc n  |  [<-]: Undo"
        hint_surf = self.font_small.render(hint_text, True, (210, 215, 230))
        self.screen.blit(hint_surf, (modal_x + (modal_w - hint_surf.get_width()) // 2, modal_y + 192))

    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and self.entering_n:
                    self.handle_n_input(event)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_paused = not self.is_paused
                    elif event.key == pygame.K_RIGHT:
                        self.is_paused = True
                        self.step_game()
                    elif event.key == pygame.K_LEFT:
                        self.is_paused = True
                        self.undo_game()
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_n:
                        self.is_paused = True
                        self.n_input = ""
                        self.entering_n = True

            # tự động chơi khi không tạm dừng
            if not self.is_paused and not self.entering_n and not self.env.is_game_over():
                if current_time - self.last_step_time >= self.step_delay:
                    self.step_game()
                    self.last_step_time = current_time

            self.screen.fill(self.color_bg)
            self.draw_board()
            self.draw_game_over_modal()
            self.draw_sidebar()
            if self.entering_n:
                self.draw_n_input_modal()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    map_file = os.path.join(root_dir, 'maps', 'map_competitive.txt')
    steps = 60
    p1_mod = 'two_agent.player1'
    p2_mod = 'two_agent.player2'

    # nhận tham số dòng lệnh: bản đồ (.txt), số bước n (số nguyên), module hoặc đường dẫn file .py của 2 agent
    custom_mods = []
    has_cli_steps = False
    for arg in sys.argv[1:]:
        if arg.isdigit():
            steps = max(1, int(arg))
            has_cli_steps = True
        elif arg.endswith('.txt'):
            map_file = arg
        else:
            custom_mods.append(arg)

    if len(custom_mods) >= 1:
        p1_mod = custom_mods[0]
    if len(custom_mods) >= 2:
        p2_mod = custom_mods[1]

    if not os.path.exists(map_file):
        print(f"Khong tim thay file ban do: {map_file}")
        sys.exit(1)

    # yêu cầu 6: số bước n do người dùng nhập
    # nếu không truyền qua dòng lệnh thì hiện khung nhập n ngay khi mở game
    try:
        gui = SokobanTwoPlayerGUI(map_path=map_file, max_steps=steps, player1_mod=p1_mod, player2_mod=p2_mod, ask_steps=not has_cli_steps)
        gui.run()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
