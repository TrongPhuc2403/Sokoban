# Thuật toán Greedy Best-First Search (GBFS) tìm đường đẩy hộp cho Agent 2
# Yêu cầu 8: File mã nguồn độc lập, sử dụng thuật toán GBFS (f = h)
# kết hợp Heuristic Maze Distance và kiểm tra Deadlock.
import time
import heapq
from collections import deque

_maze_dist_cache = {}
_deadlock_cache = {}

def _precompute_maze_distances(walls, targets, width, height):
    """Tính khoảng cách đường đi thực tế (Maze Distance) tránh tường từ các ô đích."""
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
    """Tính các ô deadlock (góc kẹt, hành lang cụt) mà hộp không thể nào đẩy tới đích."""
    key = (frozenset(walls), frozenset(targets), width, height)
    if key in _deadlock_cache:
        return _deadlock_cache[key]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    # Reverse-push BFS: từ đích tìm tất cả ô mà hộp có thể được đẩy tới đích
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

    def _plan_gbfs(self, agent_pos, box_pos, target, other_boxes, enemy_pos, walls, width, height, maze_dist, deadlocks, timeout_time):
        """Thuật toán Greedy Best-First Search (GBFS) tìm chuỗi hành động đẩy hộp.
        Hàm đánh giá: f(n) = h(n)
        Ưu tiên duyệt theo giá trị heuristic h(n) nhỏ nhất trước (khoảng cách hộp tới đích).
        Tie-break bằng g(n) (số bước đã đi)."""
        start_state = (box_pos, agent_pos)
        h0 = maze_dist.get(target, {}).get(box_pos, 999)
        # Hàng đợi: (h, g, counter, state, actions)
        frontier = [(h0, 0, 0, start_state, [])]
        visited = {start_state}
        counter = 0

        while frontier:
            if time.time() > timeout_time:
                break

            h_val, g, _, (b_curr, a_curr), actions = heapq.heappop(frontier)

            if b_curr == target:
                return actions

            for act, dr, dc in self.moves:
                na = (a_curr[0] + dr, a_curr[1] + dc)
                if na in walls or na in other_boxes or na == enemy_pos:
                    continue

                if na == b_curr:
                    # Đẩy hộp
                    nb = (b_curr[0] + dr, b_curr[1] + dc)
                    if nb in walls or nb in other_boxes or nb == enemy_pos:
                        continue
                    if nb in deadlocks and nb != target:
                        continue

                    nxt_state = (nb, na)
                    if nxt_state not in visited:
                        visited.add(nxt_state)
                        nh = maze_dist.get(target, {}).get(nb, 999)
                        counter += 1
                        heapq.heappush(frontier, (nh, g + 1, counter, nxt_state, actions + [act]))
                else:
                    # Di chuyển agent
                    nxt_state = (b_curr, na)
                    if nxt_state not in visited:
                        visited.add(nxt_state)
                        nh = maze_dist.get(target, {}).get(b_curr, 999)
                        counter += 1
                        heapq.heappush(frontier, (nh, g + 1, counter, nxt_state, actions + [act]))

        return None

    def get_action(self, state):
        """Chọn hành động bằng GBFS trong thời gian < 1000ms."""
        start_time = time.time()
        timeout_time = start_time + 0.90 # Giới hạn 900ms

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
            plan = self._plan_gbfs(my_pos, b, t, other_b, enemy_pos, walls, width, height, maze_dist, deadlocks, timeout_time)
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

        # 3. Xem xét cướp hộp nếu không còn hộp tự do
        if not best_plan and empty_targets and time.time() < timeout_time:
            enemy_boxes = [b for b in boxes if b in targets and owners.get(b) == enemy_id]
            for b in enemy_boxes:
                for t in empty_targets:
                    other_b = boxes - {b}
                    plan = self._plan_gbfs(my_pos, b, t, other_b, enemy_pos, walls, width, height, maze_dist, deadlocks, timeout_time)
                    if plan and len(plan) > 0:
                        return plan[0]

        return 'Wait'


def get_action(agent_id, game_state):
    agent = Player2(agent_id)
    return agent.get_action(game_state)
