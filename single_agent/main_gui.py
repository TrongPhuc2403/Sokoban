# giao diện trò chơi sokoban 1 agent bằng pygame
import os
import sys
import pygame

# thêm thư mục hiện tại vào đường dẫn hệ thống
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from single_agent.game_env import SokobanEnv
from single_agent.solver import SokobanSolver

class SokobanGUI:
    def __init__(self, map_path='maps/example_map.txt'):
        pygame.init()
        pygame.display.set_caption("Sokoban Single Agent - AI Midterm")

        self.map_path = map_path
        self.env = SokobanEnv(map_path)
        self.solver = SokobanSolver(self.env)
        self.inside = self._find_inside_cells()

        # kích thước mỗi ô trên lưới
        self.tile_size = 56
        self.sidebar_width = 280
        self.grid_width = self.env.width * self.tile_size
        self.grid_height = self.env.height * self.tile_size

        self.screen_width = max(600, self.grid_width + self.sidebar_width + 20)
        self.screen_height = max(640, self.grid_height + 40)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        # cài đặt phông chữ tương thích cả windows và macos
        try:
            self.font_large = pygame.font.SysFont('arial', 22, bold=True)
            self.font_medium = pygame.font.SysFont('arial', 16)
            self.font_small = pygame.font.SysFont('arial', 13)
        except Exception:
            self.font_large = pygame.font.Font(None, 26)
            self.font_medium = pygame.font.Font(None, 20)
            self.font_small = pygame.font.Font(None, 16)

        # bảng màu giao diện
        self.color_bg = (30, 32, 40)
        self.color_sidebar = (42, 45, 56)
        self.color_wall = (70, 75, 90)
        self.color_floor = (48, 52, 65)
        self.color_grid_line = (55, 60, 75)
        self.color_target = (220, 80, 80)
        self.color_box = (200, 140, 60)
        self.color_box_done = (46, 204, 113)
        self.color_agent = (52, 152, 219)
        self.color_text = (240, 240, 240)
        self.color_text_muted = (170, 175, 190)
        self.color_accent = (241, 196, 15)

        # trạng thái điều khiển
        self.solution_actions = []
        self.solution_index = 0
        self.action_history = []
        self.current_algo = 'A*'
        self.is_paused = True
        self.is_auto_playing = False
        self.step_delay = 350
        self.last_step_time = 0

        # thông số thuật toán
        self.algo_stats = {
            'time_ms': 0,
            'expanded': 0,
            'cost': 0,
            'status': 'chua chay'
        }

        # nút bấm chọn thuật toán bằng chuột
        sb_x = self.screen_width - self.sidebar_width + 25
        self.btn_ucs = pygame.Rect(sb_x, 58, 110, 34)
        self.btn_astar = pygame.Rect(sb_x + 120, 58, 110, 34)

    def draw_button(self, rect, label, active):
        # vẽ 1 nút, nút đang chọn được tô sáng, nút đang rê chuột được làm nổi
        hover = rect.collidepoint(pygame.mouse.get_pos())
        if active:
            bg = self.color_accent
            fg = (30, 32, 40)
        else:
            bg = (80, 86, 104) if hover else (60, 65, 80)
            fg = self.color_text
        pygame.draw.rect(self.screen, bg, rect, border_radius=8)
        txt = self.font_medium.render(label, True, fg)
        self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    def show_solving(self, algo_name):
        # hiện thông báo đang giải trước khi chạy thuật toán (tránh cảm giác bị treo)
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((12, 15, 22, 170))
        self.screen.blit(overlay, (0, 0))
        txt = self.font_large.render(f"Dang giai bang {algo_name}...", True, self.color_accent)
        self.screen.blit(txt, ((self.screen_width - txt.get_width()) // 2, (self.screen_height - txt.get_height()) // 2))
        pygame.display.flip()

    def _find_inside_cells(self):
        # loang từ vị trí agent để biết ô nào nằm trong tường (ô ngoài bản đồ không vẽ sàn)
        start = self.env.initial_agent
        inside = {start}
        stack = [start]
        while stack:
            r, c = stack.pop()
            for dr, dc in self.env.directions.values():
                nxt = (r + dr, c + dc)
                if nxt in inside or nxt in self.env.walls:
                    continue
                if not (0 <= nxt[0] < self.env.height and 0 <= nxt[1] < self.env.width):
                    continue
                inside.add(nxt)
                stack.append(nxt)
        return inside

    def run_algorithm(self, algo_name):
        # chạy thuật toán được chọn và lưu danh sách nước đi
        self.env.reset()
        self.solution_index = 0
        self.current_algo = algo_name
        self.is_auto_playing = False
        self.is_paused = True

        if algo_name == 'UCS':
            res = self.solver.solve_ucs()
        else:
            res = self.solver.solve_astar()

        if res['success']:
            self.solution_actions = res['actions']
            self.algo_stats = {
                'time_ms': round(res['time_ms'], 2),
                'expanded': res['expanded'],
                'cost': res['cost'],
                'status': 'thanh cong'
            }
        else:
            self.solution_actions = []
            self.algo_stats = {
                'time_ms': round(res['time_ms'], 2),
                'expanded': res['expanded'],
                'cost': 0,
                'status': 'khong tim thay'
            }

    def step_forward(self):
        # tiến thêm 1 bước theo lời giải hoặc khi đang chạy
        if self.solution_index < len(self.solution_actions):
            act = self.solution_actions[self.solution_index]
            ok = self.env.step(act)
            if ok:
                self.solution_index += 1

    def step_backward(self):
        # lùi lại 1 bước trong lịch sử
        if self.env.undo():
            if self.solution_index > 0:
                self.solution_index -= 1

    def draw_board(self):
        # vẽ bản đồ chơi
        offset_x = 20
        offset_y = 20

        # vẽ nền sàn và lưới
        for r in range(self.env.height):
            for c in range(self.env.width):
                rect = pygame.Rect(offset_x + c * self.tile_size, offset_y + r * self.tile_size, self.tile_size, self.tile_size)
                pos = (r, c)

                if pos in self.env.walls:
                    # vẽ ô tường
                    pygame.draw.rect(self.screen, self.color_wall, rect, border_radius=4)
                    pygame.draw.rect(self.screen, (90, 95, 115), rect, width=2, border_radius=4)
                elif pos in self.inside or pos in self.env.targets or pos in self.env.boxes:
                    # vẽ ô sàn
                    pygame.draw.rect(self.screen, self.color_floor, rect)
                    pygame.draw.rect(self.screen, self.color_grid_line, rect, width=1)

                    # vẽ điểm đích nếu có
                    if pos in self.env.targets:
                        center = rect.center
                        pygame.draw.circle(self.screen, self.color_target, center, 8)
                        pygame.draw.circle(self.screen, (255, 150, 150), center, 4)

        # vẽ các hộp
        for box_pos in self.env.boxes:
            r, c = box_pos
            rect = pygame.Rect(offset_x + c * self.tile_size + 6, offset_y + r * self.tile_size + 6, self.tile_size - 12, self.tile_size - 12)
            
            # hộp đã vào đích đổi sang màu xanh lá
            box_color = self.color_box_done if box_pos in self.env.targets else self.color_box
            pygame.draw.rect(self.screen, box_color, rect, border_radius=6)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2, border_radius=6)
            
            # vẽ đường chéo trang trí cho hộp
            pygame.draw.line(self.screen, (80, 50, 20), (rect.left + 4, rect.top + 4), (rect.right - 4, rect.bottom - 4), 2)
            pygame.draw.line(self.screen, (80, 50, 20), (rect.left + 4, rect.bottom - 4), (rect.right - 4, rect.top + 4), 2)

        # vẽ agent (người chơi)
        if self.env.agent_pos is not None:
            ar, ac = self.env.agent_pos
            center = (offset_x + ac * self.tile_size + self.tile_size // 2, offset_y + ar * self.tile_size + self.tile_size // 2)
            radius = self.tile_size // 2 - 8
            # vẽ thân người
            pygame.draw.circle(self.screen, self.color_agent, center, radius)
            pygame.draw.circle(self.screen, (255, 255, 255), center, radius, width=2)
            # vẽ mắt
            eye_offset_y = -3
            pygame.draw.circle(self.screen, (255, 255, 255), (center[0] - 5, center[1] + eye_offset_y), 3)
            pygame.draw.circle(self.screen, (255, 255, 255), (center[0] + 5, center[1] + eye_offset_y), 3)

    def draw_sidebar(self):
        # vẽ khung thông tin bên phải
        sb_x = self.screen_width - self.sidebar_width + 10
        sb_y = 20
        sb_w = self.sidebar_width - 30
        sb_h = self.screen_height - 40

        panel_rect = pygame.Rect(sb_x, sb_y, sb_w, sb_h)
        pygame.draw.rect(self.screen, self.color_sidebar, panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (60, 65, 80), panel_rect, width=2, border_radius=8)

        cur_y = sb_y + 10
        line_spacing = 22

        # tiêu đề
        title = self.font_large.render("SOKOBAN 1P", True, self.color_accent)
        self.screen.blit(title, (sb_x + 15, cur_y))

        # nút chọn thuật toán
        self.draw_button(self.btn_ucs, "UCS  [1]", self.current_algo == 'UCS')
        self.draw_button(self.btn_astar, "A*  [2]", self.current_algo == 'A*')
        cur_y = self.btn_ucs.bottom + 12

        # số bước hiện tại / tổng số bước
        total_act = len(self.solution_actions)
        txt_actions = self.font_medium.render(f"So action: {self.solution_index} / {total_act}", True, self.color_text)
        self.screen.blit(txt_actions, (sb_x + 15, cur_y))
        cur_y += line_spacing

        txt_cost = self.font_medium.render(f"Tong chi phi (cost): {self.algo_stats['cost']}", True, self.color_text)
        self.screen.blit(txt_cost, (sb_x + 15, cur_y))
        cur_y += line_spacing

        last_action_str = self.solution_actions[self.solution_index - 1] if self.solution_index > 0 else "None"
        txt_cur_act = self.font_medium.render(f"Action vua di: {last_action_str}", True, self.color_accent)
        self.screen.blit(txt_cur_act, (sb_x + 15, cur_y))
        cur_y += line_spacing

        # trạng thái phát
        play_status = "Tam dung" if self.is_paused else "Dang chay"
        txt_status = self.font_medium.render(f"Trang thai: {play_status}", True, (100, 220, 255) if not self.is_paused else (255, 180, 100))
        self.screen.blit(txt_status, (sb_x + 15, cur_y))
        cur_y += 28

        # thông số thực thi
        stat_head = self.font_large.render("Thong so:", True, self.color_text)
        self.screen.blit(stat_head, (sb_x + 15, cur_y))
        cur_y += 26

        self.screen.blit(self.font_small.render(f"Ket qua: {self.algo_stats['status']}", True, self.color_text_muted), (sb_x + 15, cur_y))
        cur_y += 18
        self.screen.blit(self.font_small.render(f"Thoi gian: {self.algo_stats['time_ms']} ms", True, self.color_text_muted), (sb_x + 15, cur_y))
        cur_y += 18
        self.screen.blit(self.font_small.render(f"Node da mo: {self.algo_stats['expanded']}", True, self.color_text_muted), (sb_x + 15, cur_y))
        cur_y += 26

        # chuỗi hành động (N/E/S/W), action đã đi được tô sáng
        self.screen.blit(self.font_medium.render("Chuoi action (N/E/S/W):", True, self.color_accent), (sb_x + 15, cur_y))
        cur_y += 22
        per_line = 18
        max_lines = 4
        char_w = 12
        for i, act in enumerate(self.solution_actions[:per_line * max_lines]):
            col = self.color_text if i < self.solution_index else self.color_text_muted
            if i == self.solution_index - 1:
                col = self.color_accent
            ch = self.font_small.render(act[0], True, col)
            self.screen.blit(ch, (sb_x + 15 + (i % per_line) * char_w, cur_y + (i // per_line) * 16))
        if len(self.solution_actions) > per_line * max_lines:
            more = self.font_small.render("...", True, self.color_text_muted)
            self.screen.blit(more, (sb_x + 15, cur_y + max_lines * 16))
        cur_y += max_lines * 16 + 22

        # hướng dẫn phím bấm
        guide_head = self.font_medium.render("Huong dan phim:", True, self.color_accent)
        self.screen.blit(guide_head, (sb_x + 15, cur_y))
        cur_y += 22

        keys_info = [
            ("Phim 1 / nut UCS", "Chay UCS"),
            ("Phim 2 / nut A*", "Chay A*"),
            ("Space", "Tam dung / Chay tiep"),
            ("Mui ten ->", "Tien 1 buoc"),
            ("Mui ten <-", "Lui 1 buoc (undo)"),
            ("Phim R", "Dat lai ban dau")
        ]
        for key_str, desc_str in keys_info:
            txt_k = self.font_small.render(f"- {key_str}: {desc_str}", True, self.color_text_muted)
            self.screen.blit(txt_k, (sb_x + 15, cur_y))
            cur_y += 18

    def draw_solved_modal(self):
        if not self.env.is_solved():
            return

        offset_x = 20
        offset_y = 20
        board_w = self.env.width * self.tile_size
        board_h = self.env.height * self.tile_size

        overlay = pygame.Surface((board_w, board_h), pygame.SRCALPHA)
        overlay.fill((12, 15, 22, 215))
        self.screen.blit(overlay, (offset_x, offset_y))

        modal_w = min(380, board_w - 20)
        modal_h = 220
        modal_x = offset_x + (board_w - modal_w) // 2
        modal_y = offset_y + (board_h - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        pygame.draw.rect(self.screen, (28, 32, 44), modal_rect, border_radius=12)
        pygame.draw.rect(self.screen, (46, 204, 113), modal_rect, width=2, border_radius=12)

        title_surf = self.font_large.render("MAN CHOI HOAN THANH!", True, (46, 204, 113))
        self.screen.blit(title_surf, (modal_x + (modal_w - title_surf.get_width()) // 2, modal_y + 18))

        algo_text = f"Thuat toan: {self.current_algo}  |  Chi phi: {len(self.solution_actions)} buoc"
        algo_surf = self.font_medium.render(algo_text, True, (240, 240, 240))
        self.screen.blit(algo_surf, (modal_x + (modal_w - algo_surf.get_width()) // 2, modal_y + 62))

        stat_text = f"Thoi gian: {self.algo_stats['time_ms']} ms  |  Node mo: {self.algo_stats['expanded']}"
        stat_surf = self.font_small.render(stat_text, True, (170, 180, 200))
        self.screen.blit(stat_surf, (modal_x + (modal_w - stat_surf.get_width()) // 2, modal_y + 100))

        pygame.draw.line(self.screen, (55, 62, 80), (modal_x + 20, modal_y + 140), (modal_x + modal_w - 20, modal_y + 140), 1)

        hint1 = "Nhan [R]: Dat lai   |   Nhan [<-]: Lui buoc (Undo)"
        hint1_surf = self.font_small.render(hint1, True, (210, 215, 230))
        self.screen.blit(hint1_surf, (modal_x + (modal_w - hint1_surf.get_width()) // 2, modal_y + 155))

        hint2 = "Nhan [1]: Chay UCS   |   Nhan [2]: Chay A*"
        hint2_surf = self.font_small.render(hint2, True, (241, 196, 15))
        self.screen.blit(hint2_surf, (modal_x + (modal_w - hint2_surf.get_width()) // 2, modal_y + 180))

    def run(self):
        # vòng lặp chính của chương trình
        # mặc định tính sẵn lời giải a*
        self.run_algorithm('A*')

        running = True
        while running:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # bấm chuột vào nút chọn thuật toán
                    if self.btn_ucs.collidepoint(event.pos):
                        self.show_solving('UCS')
                        self.run_algorithm('UCS')
                    elif self.btn_astar.collidepoint(event.pos):
                        self.show_solving('A*')
                        self.run_algorithm('A*')
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # phím space tạm dừng hoặc chạy tiếp
                        self.is_paused = not self.is_paused
                        self.is_auto_playing = not self.is_paused
                    elif event.key == pygame.K_RIGHT:
                        # tiến 1 bước
                        self.is_paused = True
                        self.is_auto_playing = False
                        self.step_forward()
                    elif event.key == pygame.K_LEFT:
                        # lùi 1 bước
                        self.is_paused = True
                        self.is_auto_playing = False
                        self.step_backward()
                    elif event.key == pygame.K_1:
                        # chọn ucs
                        self.show_solving('UCS')
                        self.run_algorithm('UCS')
                    elif event.key == pygame.K_2:
                        # chọn a*
                        self.show_solving('A*')
                        self.run_algorithm('A*')
                    elif event.key == pygame.K_r:
                        # đặt lại ban đầu
                        self.env.reset()
                        self.solution_index = 0
                        self.is_paused = True
                        self.is_auto_playing = False

            # tự động diễn hoạt khi không bị tạm dừng
            if self.is_auto_playing and not self.is_paused:
                if current_time - self.last_step_time >= self.step_delay:
                    if self.solution_index < len(self.solution_actions):
                        self.step_forward()
                        self.last_step_time = current_time
                    else:
                        self.is_auto_playing = False
                        self.is_paused = True

            # vẽ màn hình
            self.screen.fill(self.color_bg)
            self.draw_board()
            self.draw_solved_modal()
            self.draw_sidebar()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == '__main__':
    # đường dẫn bản đồ mặc định tính theo thư mục gốc dự án
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    map_file = os.path.join(root_dir, 'maps', 'example_map.txt')
    if len(sys.argv) > 1:
        map_file = sys.argv[1]
    if not os.path.exists(map_file):
        print(f"Khong tim thay file ban do: {map_file}")
        sys.exit(1)
    try:
        gui = SokobanGUI(map_file)
        gui.run()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
