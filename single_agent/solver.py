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
