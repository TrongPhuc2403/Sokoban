# môi trường trò chơi sokoban cho 1 agent
import os

class SokobanEnv:
    def __init__(self, map_path):
        # đường dẫn file bản đồ
        self.map_path = map_path
        self.walls = set()
        self.targets = set()
        self.initial_boxes = set()
        self.initial_agent = None
        self.width = 0
        self.height = 0

        # các hướng di chuyển cơ bản
        self.directions = {
            'North': (-1, 0),
            'South': (1, 0),
            'West': (0, -1),
            'East': (0, 1)
        }

        # nạp dữ liệu bản đồ
        self.load_map(map_path)
        
        # trạng thái hiện tại
        self.agent_pos = self.initial_agent
        self.boxes = set(self.initial_boxes)

        # lịch sử các bước đi để phục vụ tính năng undo
        self.history = []

    def load_map(self, path):
        # đọc file và lấy kích thước
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\r\n') for line in f.readlines()]

        self.height = len(lines)
        self.width = max(len(line) for line in lines) if lines else 0

        # quét các ký tự trên bản đồ
        for r, line in enumerate(lines):
            for c, ch in enumerate(line):
                if ch == '%':
                    self.walls.add((r, c))
                elif ch == 'A':
                    self.initial_agent = (r, c)
                elif ch == 'B':
                    self.initial_boxes.add((r, c))
                elif ch == 'D':
                    self.targets.add((r, c))
                elif ch == 'C':
                    # hộp đã nằm đúng vị trí đích
                    self.initial_boxes.add((r, c))
                    self.targets.add((r, c))

    def reset(self):
        # đặt lại vị trí ban đầu
        self.agent_pos = self.initial_agent
        self.boxes = set(self.initial_boxes)
        self.history = []
        return self.get_state()

    def get_state(self):
        # trả về trạng thái hiện tại dạng tuple để hash
        return (self.agent_pos, tuple(sorted(self.boxes)))

    def is_solved(self):
        # kiểm tra tất cả các hộp đều đã ở vị trí đích
        return len(self.boxes) > 0 and self.boxes.issubset(self.targets)

    def can_move(self, action):
        # kiểm tra xem hành động có hợp lệ hay không
        if action not in self.directions:
            return False, None, None

        dr, dc = self.directions[action]
        curr_r, curr_c = self.agent_pos
        next_r, next_c = curr_r + dr, curr_c + dc

        # đâm vào tường
        if (next_r, next_c) in self.walls:
            return False, None, None

        # nếu ô tiếp theo có hộp
        if (next_r, next_c) in self.boxes:
            box_next_r, box_next_c = next_r + dr, next_c + dc
            # hộp bị cản bởi tường hoặc hộp khác
            if (box_next_r, box_next_c) in self.walls or (box_next_r, box_next_c) in self.boxes:
                return False, None, None
            return True, (next_r, next_c), (box_next_r, box_next_c)

        # di chuyển vào ô trống
        return True, (next_r, next_c), None

    def step(self, action):
        # thực hiện bước đi nếu hợp lệ
        valid, next_agent, next_box = self.can_move(action)
        if not valid:
            return False

        # lưu trạng thái trước khi đi để undo
        self.history.append((self.agent_pos, set(self.boxes)))

        # cập nhật vị trí agent
        self.agent_pos = next_agent

        # nếu có đẩy hộp
        if next_box is not None:
            self.boxes.remove(next_agent)
            self.boxes.add(next_box)

        return True

    def undo(self):
        # lùi lại một bước
        if not self.history:
            return False
        prev_agent, prev_boxes = self.history.pop()
        self.agent_pos = prev_agent
        self.boxes = set(prev_boxes)
        return True
