# thuat toan gbfs cho agent 2
import time
import heapq
import random
from collections import deque

NAME = "GBFS"

_maze_dist_cache = {}
_deadlock_cache = {}
# nho trang thai luot truoc de phat hien hai agent ket nhau (livelock)
_last_seen = {}


def _update_stuck(agent_id, key):
    # tra ve so luot lien tiep trang thai khong doi
    prev_key, count = _last_seen.get(agent_id, (None, 0))
    count = count + 1 if prev_key == key else 0
    _last_seen[agent_id] = (key, count)
    return count

def _precompute_maze_distances(walls, targets, width, height):
    # tinh khoang cach me cung tu cac o dich bang bfs
    key = (frozenset(walls), frozenset(targets), width, height)
    if key in _maze_dist_cache:
        return _maze_dist_cache[key]

    dist_map = {}
    for target in targets:
        dist_map[target] = {}
        queue = deque([(target, 0)])
        visited = {target}
        while queue:
            pos, d = queue.popleft()
            dist_map[target][pos] = d
            r, c = pos
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < height and 0 <= nc < width and (nr, nc) not in walls and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), d + 1))
    _maze_dist_cache[key] = dist_map
    return dist_map


def _compute_deadlocks(walls, targets, width, height):
    # xac dinh cac o deadlock khong the day den dich
    key = (frozenset(walls), frozenset(targets), width, height)
    if key in _deadlock_cache:
        return _deadlock_cache[key]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    reachable = set(targets)
    queue = deque(list(targets))

    while queue:
        r, c = queue.popleft()
        for dr, dc in dirs:
            prev = (r - dr, c - dc)
            behind = (r - 2 * dr, c - 2 * dc)
            if not (0 <= prev[0] < height and 0 <= prev[1] < width):
                continue
            if not (0 <= behind[0] < height and 0 <= behind[1] < width):
                continue
            if prev in walls or prev in reachable or behind in walls:
                continue
            reachable.add(prev)
            queue.append(prev)

    deadlocks = set()
    for r in range(height):
        for c in range(width):
            pos = (r, c)
            if pos not in walls and pos not in reachable:
                deadlocks.add(pos)

    _deadlock_cache[key] = deadlocks
    return deadlocks


class Player2:
    def __init__(self, agent_id=2):
        self.agent_id = agent_id
        self.moves = [
            ('North', -1, 0),
            ('South', 1, 0),
            ('West', 0, -1),
            ('East', 0, 1)
        ]

    def _plan_gbfs(self, agent_pos, box_pos, target, other_boxes, enemy_block, walls, width, height, maze_dist, deadlocks, timeout_time):
        # tim duong bang gbfs
        # neu hop dang nam san tren dich (cuop hop doi thu) thi hop phai roi
        # khoi dich it nhat mot lan roi moi duoc tinh la dat lai
        start_left = box_pos != target
        start_state = (box_pos, agent_pos, start_left)
        h0 = maze_dist.get(target, {}).get(box_pos, 999) if start_left else 2
        # Hàng đợi: (h, g, counter, state, actions)
        frontier = [(h0, 0, 0, start_state, [])]
        visited = {start_state}
        counter = 0

        while frontier:
            if time.time() > timeout_time:
                break

            h_val, g, _, cur_state, actions = heapq.heappop(frontier)
            b_curr, a_curr, left = cur_state

            if b_curr == target and left:
                return actions

            for act, dr, dc in self.moves:
                na = (a_curr[0] + dr, a_curr[1] + dc)
                if na in walls or na in other_boxes or na in enemy_block:
                    continue
                if not (0 <= na[0] < height and 0 <= na[1] < width):
                    continue

                nb = b_curr
                if na == b_curr:
                    # Đẩy hộp
                    nb = (b_curr[0] + dr, b_curr[1] + dc)
                    if nb in walls or nb in other_boxes or nb in enemy_block:
                        continue
                    if nb in deadlocks and nb != target:
                        continue

                n_left = left or nb != target
                nxt_state = (nb, na, n_left)
                if nxt_state not in visited:
                    visited.add(nxt_state)
                    nh = maze_dist.get(target, {}).get(nb, 999) if n_left else 2
                    counter += 1
                    heapq.heappush(frontier, (nh, g + 1, counter, nxt_state, actions + [act]))

        return None

    def get_action(self, state):
        # chon nuoc di bang gbfs
        start_time = time.time()
        timeout_time = start_time + 0.90 # gioi han 900ms

        my_pos = state['agent2'] if self.agent_id == 2 else state['agent1']
        enemy_pos = state['agent1'] if self.agent_id == 2 else state['agent2']

        enemy_id = 1 if self.agent_id == 2 else 2

        boxes = set(state['boxes'])
        owners = state['box_owners']
        targets = set(state['targets'])
        walls = set(state['walls'])
        width = state['width']
        height = state['height']

        maze_dist = _precompute_maze_distances(walls, targets, width, height)
        deadlocks = _compute_deadlocks(walls, targets, width, height)

        # phat hien ket: neu trang thai khong doi qua nhieu luot thi ne doi thu
        stuck = _update_stuck(self.agent_id, (my_pos, enemy_pos, frozenset(boxes)))
        enemy_block = {enemy_pos}
        if stuck >= 2:
            for _, dr, dc in self.moves:
                enemy_block.add((enemy_pos[0] + dr, enemy_pos[1] + dc))
        if stuck >= 4:
            free_moves = []
            for act, dr, dc in self.moves:
                na = (my_pos[0] + dr, my_pos[1] + dc)
                if na not in walls and na not in boxes and na != enemy_pos:
                    free_moves.append(act)
            if free_moves:
                return random.choice(free_moves)

        # 1. Đích còn trống
        empty_targets = [t for t in targets if t not in boxes]

        # 2. Hộp tự do
        free_boxes = [b for b in boxes if b not in targets]

        best_plan = None
        best_score = float('inf')

        # Đánh giá các cặp (hộp tự do, đích trống)
        candidates = []
        for b in free_boxes:
            for t in empty_targets:
                d = maze_dist.get(t, {}).get(b, 999)
                if d < 999:
                    candidates.append((d, b, t))
        # Greedy: ưu tiên hộp gần đích nhất
        candidates.sort(key=lambda x: x[0])

        for _, b, t in candidates:
            if time.time() > timeout_time:
                break
            other_b = boxes - {b}
            plan = self._plan_gbfs(my_pos, b, t, other_b, enemy_block, walls, width, height, maze_dist, deadlocks, timeout_time)
            if plan:
                cost = len(plan)
                # Ưu tiên nửa sân của mình (Agent 2 là bên phải)
                mid_col = width // 2
                if self.agent_id == 2 and b[1] < mid_col:
                    cost += 4
                elif self.agent_id == 1 and b[1] >= mid_col:
                    cost += 4

                if cost < best_score:
                    best_score = cost
                    best_plan = plan
                    if cost <= 6:
                        break

        # Nếu có kế hoạch, trả về bước đầu tiên
        if best_plan and len(best_plan) > 0:
            return best_plan[0]

        # 3. Không còn hộp tự do khả thi: cướp hộp đang nằm trên đích không thuộc về mình
        # (đẩy ra khỏi đích rồi đặt lại vào một đích trống hoặc chính đích cũ)
        if time.time() < timeout_time:
            steal_boxes = [b for b in boxes if b in targets and owners.get(b) != self.agent_id]
            steal_cands = []
            for b in steal_boxes:
                for t in empty_targets + [b]:
                    d = maze_dist.get(t, {}).get(b, 999)
                    if t == b:
                        d = 2
                    if d < 999:
                        steal_cands.append((d, b, t))
            # Greedy: thử cặp có ước lượng nhỏ nhất trước, có kế hoạch là dùng ngay
            steal_cands.sort(key=lambda x: x[0])
            for _, b, t in steal_cands:
                if time.time() > timeout_time:
                    break
                other_b = boxes - {b}
                plan = self._plan_gbfs(my_pos, b, t, other_b, enemy_block, walls, width, height, maze_dist, deadlocks, timeout_time)
                if plan:
                    return plan[0]

        return 'Wait'


def get_action(*args, **kwargs):
    if len(args) == 1:
        game_state = args[0]
        agent_id = 2
    elif len(args) >= 2:
        agent_id = args[0]
        game_state = args[1]
    else:
        game_state = kwargs.get('game_state', kwargs.get('state'))
        agent_id = kwargs.get('agent_id', 2)

    agent = Player2(agent_id)
    return agent.get_action(game_state)
