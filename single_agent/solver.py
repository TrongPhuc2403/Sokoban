# thuật toán ucs và a* giải sokoban
import heapq
import time
from collections import deque

class SokobanSolver:
    def __init__(self, env):
        self.env = env
        self.walls = env.walls
        self.targets = env.targets
        # tiền xử lý khoảng cách mê cung từ mỗi ô đến các ô đích bằng bfs
        # không dùng manhattan hay euclidean
        self.maze_dist = self._precompute_maze_distances()
        self.deadlocks = self._precompute_deadlocks()

    def _precompute_maze_distances(self):
        # tính khoảng cách ngắn nhất trên bản đồ vượt tường
        dist_map = {}
        for target in self.targets:
            dist_map[target] = {}
            queue = deque([(target, 0)])
            visited = {target}

            while queue:
                pos, d = queue.popleft()
                dist_map[target][pos] = d
                r, c = pos
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) not in self.walls and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append(((nr, nc), d + 1))
        return dist_map

    def _precompute_deadlocks(self):
        # xác định các vị trí deadlock (hộp không thể di chuyển đến đích)
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        reachable = set(self.targets)
        queue = deque(list(self.targets))

        while queue:
            r, c = queue.popleft()
            for dr, dc in dirs:
                prev = (r - dr, c - dc)
                behind = (r - 2 * dr, c - 2 * dc)
                if not (0 <= prev[0] < self.env.height and 0 <= prev[1] < self.env.width):
                    continue
                if not (0 <= behind[0] < self.env.height and 0 <= behind[1] < self.env.width):
                    continue
                if prev in self.walls or prev in reachable or behind in self.walls:
                    continue
                reachable.add(prev)
                queue.append(prev)

        deadlocks = set()
        for r in range(self.env.height):
            for c in range(self.env.width):
                pos = (r, c)
                if pos not in self.walls and pos not in reachable:
                    deadlocks.add(pos)
        return deadlocks

    def heuristic(self, boxes):
        # tổng khoảng cách mê cung ngắn nhất từ mỗi hộp đến một đích bất kỳ
        # thỏa mãn tính chất admissible và consistent
        total = 0
        for b in boxes:
            min_d = float('inf')
            for t in self.targets:
                if b in self.maze_dist[t]:
                    min_d = min(min_d, self.maze_dist[t][b])
            if min_d == float('inf'):
                # nếu không có đường đến đích coi như vô nghiệm
                return float('inf')
            total += min_d
        return total

    def _get_successors(self, agent_pos, boxes):
        # sinh các trạng thái kế tiếp hợp lệ
        successors = []
        r, c = agent_pos
        boxes_set = set(boxes)

        directions = [
            ('North', -1, 0),
            ('South', 1, 0),
            ('West', 0, -1),
            ('East', 0, 1)
        ]

        for action, dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (nr, nc) in self.walls:
                continue

            if (nr, nc) in boxes_set:
                # trường hợp đẩy hộp
                bnr, bnc = nr + dr, nc + dc
                if (bnr, bnc) in self.walls or (bnr, bnc) in boxes_set:
                    continue
                # không đẩy hộp vào góc kẹt deadlock nếu ô đó không phải đích
                if (bnr, bnc) in self.deadlocks and (bnr, bnc) not in self.targets:
                    continue
                # tạo tập hợp mới
                new_boxes = list(boxes_set)
                new_boxes.remove((nr, nc))
                new_boxes.append((bnr, bnc))
                new_boxes_tuple = tuple(sorted(new_boxes))
                successors.append((action, (nr, nc), new_boxes_tuple))
            else:
                # chỉ di chuyển agent
                successors.append((action, (nr, nc), boxes))

        return successors

    def solve_ucs(self):
        # ucs mở rộng theo g nhỏ nhất
        start_time = time.time()
        start_agent = self.env.initial_agent
        start_boxes = tuple(sorted(self.env.initial_boxes))
        start_state = (start_agent, start_boxes)

        # hàng đợi ưu tiên: (g, count, state, path)
        counter = 0
        frontier = [(0, counter, start_state, [])]
        visited = {start_state: 0}

        expanded_nodes = 0
        generated_nodes = 1

        while frontier:
            cost, _, current_state, path = heapq.heappop(frontier)
            agent_pos, boxes = current_state
            expanded_nodes += 1

            # kiểm tra đích
            if set(boxes).issubset(self.targets):
                exec_time = (time.time() - start_time) * 1000
                return {
                    'success': True,
                    'actions': path,
                    'cost': cost,
                    'time_ms': exec_time,
                    'expanded': expanded_nodes,
                    'generated': generated_nodes
                }

            # bỏ qua nếu đã có đường đi tốt hơn
            if cost > visited.get(current_state, float('inf')):
                continue

            for action, next_agent, next_boxes in self._get_successors(agent_pos, boxes):
                next_state = (next_agent, next_boxes)
                new_cost = cost + 1
                generated_nodes += 1

                if next_state not in visited or new_cost < visited[next_state]:
                    visited[next_state] = new_cost
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, next_state, path + [action]))

        exec_time = (time.time() - start_time) * 1000
        return {
            'success': False,
            'actions': [],
            'cost': 0,
            'time_ms': exec_time,
            'expanded': expanded_nodes,
            'generated': generated_nodes
        }

    def solve_astar(self):
        # a* mở rộng theo f = g + h
        start_time = time.time()
        start_agent = self.env.initial_agent
        start_boxes = tuple(sorted(self.env.initial_boxes))
        start_state = (start_agent, start_boxes)

        h_start = self.heuristic(start_boxes)
        counter = 0
        # hàng đợi: (f, g, counter, state, path)
        frontier = [(h_start, 0, counter, start_state, [])]
        cost_so_far = {start_state: 0}

        expanded_nodes = 0
        generated_nodes = 1

        while frontier:
            f, g, _, current_state, path = heapq.heappop(frontier)
            agent_pos, boxes = current_state
            expanded_nodes += 1

            if set(boxes).issubset(self.targets):
                exec_time = (time.time() - start_time) * 1000
                return {
                    'success': True,
                    'actions': path,
                    'cost': g,
                    'time_ms': exec_time,
                    'expanded': expanded_nodes,
                    'generated': generated_nodes
                }

            if g > cost_so_far.get(current_state, float('inf')):
                continue

            for action, next_agent, next_boxes in self._get_successors(agent_pos, boxes):
                next_state = (next_agent, next_boxes)
                new_g = g + 1
                generated_nodes += 1

                if next_state not in cost_so_far or new_g < cost_so_far[next_state]:
                    cost_so_far[next_state] = new_g
                    h_val = self.heuristic(next_boxes)
                    new_f = new_g + h_val
                    counter += 1
                    heapq.heappush(frontier, (new_f, new_g, counter, next_state, path + [action]))

        exec_time = (time.time() - start_time) * 1000
        return {
            'success': False,
            'actions': [],
            'cost': 0,
            'time_ms': exec_time,
            'expanded': expanded_nodes,
            'generated': generated_nodes
        }

if __name__ == '__main__':
    import os
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    # thêm thư mục cha vào sys.path để import game_env
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from single_agent.game_env import SokobanEnv

    map_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join('maps', 'example_map.txt')
    if not os.path.exists(map_path):
        print(f"Loi: Khong tim thay file ban do tai '{map_path}'")
        sys.exit(1)

    print("=" * 60)
    print(f"CHAY THU THUAT TOAN SOKOBAN TREN BAN DO: {map_path}")
    print("=" * 60)

    env = SokobanEnv(map_path)
    solver = SokobanSolver(env)

    # 1. Chay thuat toan A*
    print("\n--- 1. THUAT TOAN A* (HEURISTIC MAZE DISTANCE) ---")
    res_astar = solver.solve_astar()
    if res_astar['success']:
        print("Trang thai: Thanh cong!")
        print(f"Tong chi phi (buoc di): {res_astar['cost']}")
        print(f"Thoi gian thuc thi: {res_astar['time_ms']:.2f} ms")
        print(f"So node da mo (expanded): {res_astar['expanded']}")
        print(f"So node da tao (generated): {res_astar['generated']}")
        print(f"Danh sach hanh dong ({len(res_astar['actions'])} buoc):")
        print(res_astar['actions'])
    else:
        print("Khong tim thay loi giai!")

    # 2. Chay thuat toan UCS
    print("\n--- 2. THUAT TOAN UNIFORM-COST SEARCH (UCS) ---")
    res_ucs = solver.solve_ucs()
    if res_ucs['success']:
        print("Trang thai: Thanh cong!")
        print(f"Tong chi phi (buoc di): {res_ucs['cost']}")
        print(f"Thoi gian thuc thi: {res_ucs['time_ms']:.2f} ms")
        print(f"So node da mo (expanded): {res_ucs['expanded']}")
        print(f"So node da tao (generated): {res_ucs['generated']}")
        print(f"Danh sach hanh dong ({len(res_ucs['actions'])} buoc):")
        print(res_ucs['actions'])
    else:
        print("Khong tim thay loi giai!")
    print("=" * 60)

