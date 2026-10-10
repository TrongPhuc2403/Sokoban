# môi trường trò chơi sokoban đối kháng 2 agent
import os

class SokobanTwoPlayerEnv:
    def __init__(self, map_path, max_steps=50):
        self.map_path = map_path
        self.max_steps = max_steps
        self.current_step = 0

        self.walls = set()
        self.targets = set()
        self.initial_boxes = set()
        self.initial_agent1 = None
        self.initial_agent2 = None
        self.width = 0
        self.height = 0

        self.directions = {
            'North': (-1, 0),
            'South': (1, 0),
            'West': (0, -1),
            'East': (0, 1),
            'Wait': (0, 0)
        }

        # đọc thông tin bản đồ
        self.load_map(map_path)

        # vị trí và trạng thái hiện tại
        self.agent1_pos = self.initial_agent1
        self.agent2_pos = self.initial_agent2
        self.boxes = set(self.initial_boxes)

        # lưu người sở hữu hộp ở vị trí đích: box_pos -> 1 hoặc 2 (hoặc None)
        self.box_owners = {}
        for b in self.boxes:
            self.box_owners[b] = None

        # lịch sử để undo
        self.history = []

    def load_map(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\r\n') for line in f.readlines()]

        self.height = len(lines)
        self.width = max(len(l) for l in lines) if lines else 0

        for r, line in enumerate(lines):
            for c, ch in enumerate(line):
                pos = (r, c)
                if ch == '%':
                    self.walls.add(pos)
                elif ch in ('1', 'A'):
                    self.initial_agent1 = pos
                elif ch in ('2', 'Z'):
                    self.initial_agent2 = pos
                elif ch == 'B':
                    self.initial_boxes.add(pos)
                elif ch == 'D':
                    self.targets.add(pos)
                elif ch == 'C':
                    self.initial_boxes.add(pos)
                    self.targets.add(pos)

    def reset(self):
        # đặt lại toàn bộ trạng thái trận đấu
        self.current_step = 0
        self.agent1_pos = self.initial_agent1
        self.agent2_pos = self.initial_agent2
        self.boxes = set(self.initial_boxes)
        self.box_owners = {b: None for b in self.boxes}
        self.history = []
        return self.get_state()

    def get_state(self):
        # trả về thông tin trạng thái để các agent đọc dữ liệu
        return {
            'agent1': self.agent1_pos,
            'agent2': self.agent2_pos,
            'boxes': set(self.boxes),
            'box_owners': dict(self.box_owners),
            'targets': set(self.targets),
            'walls': set(self.walls),
            'current_step': self.current_step,
            'max_steps': self.max_steps,
            'width': self.width,
            'height': self.height
        }

    def get_scores(self):
        # tính điểm: số hộp ở vị trí đích thuộc về từng agent
        score1 = 0
        score2 = 0
        for b in self.boxes:
            if b in self.targets:
                if self.box_owners.get(b) == 1:
                    score1 += 1
                elif self.box_owners.get(b) == 2:
                    score2 += 1
        return score1, score2

    def is_game_over(self):
        # hết số bước quy định
        if self.current_step >= self.max_steps:
            return True
        # hoặc tất cả các ô đích đều đã có hộp
        if len(self.targets) > 0 and self.targets.issubset(self.boxes):
            return True
        # hoặc tất cả các hộp đều đã nằm trên đích
        if len(self.boxes) > 0 and self.boxes.issubset(self.targets):
            return True
        return False

    def get_winner(self):
        # xác định người chiến thắng
        s1, s2 = self.get_scores()
        if s1 > s2:
            return 1
        elif s2 > s1:
            return 2
        return 0 # hòa nhau

    def _simulate_agent_intent(self, agent_id, agent_pos, action, other_pos, current_boxes):
        # tính toán vị trí mong muốn của agent và hộp (nếu đẩy)
        if action not in self.directions or action == 'Wait':
            return agent_pos, None, None

        dr, dc = self.directions[action]
        nr, nc = agent_pos[0] + dr, agent_pos[1] + dc
        next_agent = (nr, nc)

        # đâm tường hoặc đâm vào agent kia
        if next_agent in self.walls or next_agent == other_pos:
            return agent_pos, None, None

        # nếu ô tiếp theo là hộp
        if next_agent in current_boxes:
            box_next = (nr + dr, nc + dc)
            # hộp bị vướng tường, vướng agent kia, hoặc vướng hộp khác
            if box_next in self.walls or box_next == other_pos or box_next in current_boxes:
                return agent_pos, None, None
            return next_agent, next_agent, box_next

        # đi vào ô trống
        return next_agent, None, None

    def step(self, action1, action2):
        # cả hai agent hành động đồng thời trong một lượt
        if self.is_game_over():
            return False

        # lưu lịch sử để hỗ trợ undo
        self.history.append({
            'a1': self.agent1_pos,
            'a2': self.agent2_pos,
            'boxes': set(self.boxes),
            'owners': dict(self.box_owners),
            'step': self.current_step
        })

        # tính toán ý định di chuyển
        next_a1, push_from1, push_to1 = self._simulate_agent_intent(1, self.agent1_pos, action1, self.agent2_pos, self.boxes)
        next_a2, push_from2, push_to2 = self._simulate_agent_intent(2, self.agent2_pos, action2, self.agent1_pos, self.boxes)

        # xử lý va chạm trực tiếp giữa hai agent
        # trường hợp 1: hai agent đổi chỗ nhau (swap)
        if next_a1 == self.agent2_pos and next_a2 == self.agent1_pos:
            next_a1 = self.agent1_pos
            next_a2 = self.agent2_pos
            push_from1, push_to1 = None, None
            push_from2, push_to2 = None, None

        # trường hợp 2: hai agent cùng bước vào cùng một ô
        if next_a1 == next_a2 and next_a1 != self.agent1_pos and next_a2 != self.agent2_pos:
            next_a1 = self.agent1_pos
            next_a2 = self.agent2_pos
            push_from1, push_to1 = None, None
            push_from2, push_to2 = None, None

        # trường hợp 3: cả hai cùng đẩy cùng một hộp hoặc đẩy hộp vào cùng một ô
        if push_to1 is not None and push_to2 is not None:
            if push_from1 == push_from2 or push_to1 == push_to2:
                # xung đột đẩy hộp hủy nước đi của cả hai
                next_a1 = self.agent1_pos
                next_a2 = self.agent2_pos
                push_from1, push_to1 = None, None
                push_from2, push_to2 = None, None

        # trường hợp 4: một agent đẩy hộp vào ô agent kia bước tới
        if push_to1 is not None and push_to1 == next_a2:
            next_a1 = self.agent1_pos
            next_a2 = self.agent2_pos
            push_from1, push_to1 = None, None
            push_from2, push_to2 = None, None

        if push_to2 is not None and push_to2 == next_a1:
            next_a1 = self.agent1_pos
            next_a2 = self.agent2_pos
            push_from1, push_to1 = None, None
            push_from2, push_to2 = None, None

        # áp dụng nước đi cho agent 1
        self.agent1_pos = next_a1
        if push_to1 is not None and push_from1 in self.boxes:
            old_owner = self.box_owners.get(push_from1, None)
            self.boxes.remove(push_from1)
            self.boxes.add(push_to1)
            del self.box_owners[push_from1]

            # nếu hộp được đẩy vào ô đích thì agent 1 chiếm quyền sở hữu
            if push_to1 in self.targets:
                self.box_owners[push_to1] = 1
            else:
                # nếu bị đẩy ra khỏi đích thì mất trạng thái hoàn thành
                self.box_owners[push_to1] = None

        # áp dụng nước đi cho agent 2
        self.agent2_pos = next_a2
        if push_to2 is not None and push_from2 in self.boxes:
            old_owner = self.box_owners.get(push_from2, None)
            self.boxes.remove(push_from2)
            self.boxes.add(push_to2)
            del self.box_owners[push_from2]

            # nếu hộp được đẩy vào ô đích thì agent 2 chiếm quyền sở hữu
            if push_to2 in self.targets:
                self.box_owners[push_to2] = 2
            else:
                self.box_owners[push_to2] = None

        self.current_step += 1
        return True

    def undo(self):
        # lùi lại 1 lượt chơi
        if not self.history:
            return False
        snap = self.history.pop()
        self.agent1_pos = snap['a1']
        self.agent2_pos = snap['a2']
        self.boxes = set(snap['boxes'])
        self.box_owners = dict(snap['owners'])
        self.current_step = snap['step']
        return True
