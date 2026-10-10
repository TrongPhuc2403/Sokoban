# thuat toan a* cho agent 1
import time
import heapq
from collections import deque

NAME = "A*"

_maze_dist_cache = {}
_deadlock_cache = {}

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


class Player1:
    def __init__(self, agent_id=1):
        self.agent_id = agent_id
        self.moves = [
            ('North', -1, 0),
            ('South', 1, 0),
            ('West', 0, -1),
            ('East', 0, 1)
        ]

    def _plan_astar(self, agent_pos, box_pos, target, other_boxes, enemy_pos, walls, width, height, maze_dist, deadlocks, timeout_time):
        # tim duong a* dua hop ve dich
        start_state = (box_pos, agent_pos)
        h0 = maze_dist.get(target, {}).get(box_pos, 999)
        frontier = [(h0, 0, 0, start_state, [])]
        cost_so_far = {start_state: 0}
        counter = 0

        while frontier:
            if time.time() > timeout_time:
                break

            f, g, _, (b_curr, a_curr), actions = heapq.heappop(frontier)

            if b_curr == target:
                return actions

            if g > cost_so_far.get((b_curr, a_curr), float('inf')):
                continue

            for act, dr, dc in self.moves:
                na = (a_curr[0] + dr, a_curr[1] + dc)
                if na in walls or na in other_boxes or na == enemy_pos:
                    continue

                if na == b_curr:
                    # Agent thực hiện đẩy hộp
                    nb = (b_curr[0] + dr, b_curr[1] + dc)
                    if nb in walls or nb in other_boxes or nb == enemy_pos:
                        continue
                    # Cấm đẩy vào deadlock nếu ô đó không phải là đích
                    if nb in deadlocks and nb != target:
                        continue

                    nxt_state = (nb, na)
                    new_g = g + 1
                    if nxt_state not in cost_so_far or new_g < cost_so_far[nxt_state]:
                        cost_so_far[nxt_state] = new_g
                        h = maze_dist.get(target, {}).get(nb, 999)
                        counter += 1
                        heapq.heappush(frontier, (new_g + h, new_g, counter, nxt_state, actions + [act]))
                else:
                    # Agent di chuyển bình thường không đẩy hộp
                    nxt_state = (b_curr, na)
                    new_g = g + 1
                    if nxt_state not in cost_so_far or new_g < cost_so_far[nxt_state]:
                        cost_so_far[nxt_state] = new_g
                        h = maze_dist.get(target, {}).get(b_curr, 999)
                        counter += 1
                        heapq.heappush(frontier, (new_g + h, new_g, counter, nxt_state, actions + [act]))

        return None

    def get_action(self, state):
        # chon nuoc di bang a*
        start_time = time.time()
        timeout_time = start_time + 0.90 # gioi han 900ms

        my_pos = state['agent1'] if self.agent_id == 1 else state['agent2']
        enemy_pos = state['agent2'] if self.agent_id == 1 else state['agent1']
        enemy_id = 2 if self.agent_id == 1 else 1

        boxes = set(state['boxes'])
        owners = state['box_owners']
        targets = set(state['targets'])
        walls = set(state['walls'])
        width = state['width']
        height = state['height']

        maze_dist = _precompute_maze_distances(walls, targets, width, height)
        deadlocks = _compute_deadlocks(walls, targets, width, height)

        # 1. Đích còn trống (chưa có hộp nào nằm trên đó)
        empty_targets = [t for t in targets if t not in boxes]

        # 2. Hộp tự do (chưa nằm trên bất kỳ đích nào)
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
        # Ưu tiên cặp có khoảng cách ngắn
        candidates.sort(key=lambda x: x[0])

        for _, b, t in candidates:
            if time.time() > timeout_time:
                break
            other_b = boxes - {b}
            plan = self._plan_astar(my_pos, b, t, other_b, enemy_pos, walls, width, height, maze_dist, deadlocks, timeout_time)
            if plan:
                cost = len(plan)
                # Ưu tiên bảo vệ và đẩy hộp thuộc nửa sân của mình trước
                mid_col = width // 2
                if self.agent_id == 1 and b[1] >= mid_col:
                    cost += 4
                elif self.agent_id == 2 and b[1] < mid_col:
                    cost += 4

                if cost < best_score:
                    best_score = cost
                    best_plan = plan
                    # Tìm thấy kế hoạch rất ngắn thì chọn ngay để tiết kiệm thời gian
                    if cost <= 6:
                        break

        # Nếu có kế hoạch, trả về bước đầu tiên
        if best_plan and len(best_plan) > 0:
            return best_plan[0]

        # 3. Nếu không còn hộp tự do khả thi và đích trống còn, xem xét cướp hộp của đối thủ
        if not best_plan and empty_targets and time.time() < timeout_time:
            enemy_boxes = [b for b in boxes if b in targets and owners.get(b) == enemy_id]
            for b in enemy_boxes:
                for t in empty_targets:
                    other_b = boxes - {b}
                    plan = self._plan_astar(my_pos, b, t, other_b, enemy_pos, walls, width, height, maze_dist, deadlocks, timeout_time)
                    if plan and len(plan) > 0:
                        return plan[0]

        # 4. Tránh đứng yên khi bị cản đường: nếu có thể giữ nguyên vị trí an toàn
        return 'Wait'


def get_action(*args, **kwargs):
    if len(args) == 1:
        game_state = args[0]
        agent_id = 1
    elif len(args) >= 2:
        agent_id = args[0]
        game_state = args[1]
    else:
        game_state = kwargs.get('game_state', kwargs.get('state'))
        agent_id = kwargs.get('agent_id', 1)

    agent = Player1(agent_id)
    return agent.get_action(game_state)
