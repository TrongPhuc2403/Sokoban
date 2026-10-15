# môi trường trò chơi sokoban đối kháng 2 agent
import os
import random

class SokobanTwoPlayerEnv:
    def __init__(self, map_path, max_steps=50, seed=None):
        self.map_path = map_path
        # số bước n phải là số nguyên dương
        self.max_steps = max(1, int(max_steps))
        self.current_step = 0

        # bộ sinh số ngẫu nhiên riêng để phân xử tranh chấp (cố định seed khi test)
        self.rng = random.Random(seed)
        # thông tin tranh chấp lượt gần nhất: None hoặc {'type', 'p', 'winner'}
        self.last_conflict = None

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
        self.last_conflict = None
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
        # tran dau chi ket thuc khi di het so buoc quy dinh
        # cho phep agent day hop cua doi thu ra khoi dich de gianh diem
        return self.current_step >= self.max_steps

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

    def _detect_conflict(self, next_a1, push_from1, push_to1, next_a2, push_from2, push_to2):
        # trả về loại tranh chấp (chuỗi) hoặc None nếu không có tranh chấp
        moved1 = next_a1 != self.agent1_pos
        moved2 = next_a2 != self.agent2_pos
        if not (moved1 and moved2):
            return None

        # hai agent cùng đẩy một hộp
        if push_from1 is not None and push_from1 == push_from2:
            return 'same_box'
        # hai agent cùng đi vào một vị trí
        if next_a1 == next_a2:
            return 'same_cell'
        # hai hộp bị đẩy vào cùng một vị trí
        if push_to1 is not None and push_to1 == push_to2:
            return 'same_cell'
        # hộp do agent này đẩy và agent kia cùng đi vào một vị trí
        if push_to1 is not None and push_to1 == next_a2:
            return 'same_cell'
        if push_to2 is not None and push_to2 == next_a1:
            return 'same_cell'
        return None

    def _apply_push(self, agent_id, push_from, push_to):
        # di chuyển hộp và cập nhật quyền sở hữu
        if push_to is None or push_from not in self.boxes:
            return
        self.boxes.remove(push_from)
        self.boxes.add(push_to)
        self.box_owners.pop(push_from, None)
        # vào đích thì agent đẩy chiếm quyền sở hữu, ra khỏi đích thì mất
        self.box_owners[push_to] = agent_id if push_to in self.targets else None

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
            'step': self.current_step,
            'conflict': self.last_conflict
        })
        self.last_conflict = None

        # tính toán ý định di chuyển
        next_a1, push_from1, push_to1 = self._simulate_agent_intent(1, self.agent1_pos, action1, self.agent2_pos, self.boxes)
        next_a2, push_from2, push_to2 = self._simulate_agent_intent(2, self.agent2_pos, action2, self.agent1_pos, self.boxes)

        # hai agent đổi chỗ cho nhau: không đi vào cùng vị trí nên cả hai đứng yên
        # (thực tế _simulate_agent_intent đã chặn việc bước vào ô agent kia đang đứng)
        if next_a1 == self.agent2_pos and next_a2 == self.agent1_pos:
            next_a1, push_from1, push_to1 = self.agent1_pos, None, None
            next_a2, push_from2, push_to2 = self.agent2_pos, None, None

        # xu ly tranh chap khi hai agent cung vao mot o hoac cung day mot hop
        # xac suat p sinh theo phan bo deu U(0, 1)
        # p < 0.5 thi agent 1 di, agent 2 dung yen; nguoc lai agent 2 di
        conflict = self._detect_conflict(next_a1, push_from1, push_to1, next_a2, push_from2, push_to2)
        if conflict is not None:
            p = self.rng.uniform(0.0, 1.0)
            if p < 0.5:
                winner = 1
                next_a2, push_from2, push_to2 = self.agent2_pos, None, None
            else:
                winner = 2
                next_a1, push_from1, push_to1 = self.agent1_pos, None, None
            self.last_conflict = {'type': conflict, 'p': p, 'winner': winner}

        # áp dụng nước đi cho cả hai agent
        self.agent1_pos = next_a1
        self._apply_push(1, push_from1, push_to1)
        self.agent2_pos = next_a2
        self._apply_push(2, push_from2, push_to2)

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
        self.last_conflict = snap.get('conflict')
        return True
