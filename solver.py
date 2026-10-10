"""Hai thuật toán tìm kiếm UCS và A* cho Sokoban."""

import heapq
import time
from collections import deque

from sokoban.board import get_next_states, is_goal


def build_goal_distances(board):
    """Dùng BFS để đo đường đi qua các ô không phải tường từ từng đích."""
    all_distances = {}

    for goal in board["goals"]:
        distances = {goal: 0}
        queue = deque([goal])

        while queue:
            current = queue.popleft()
            row, col = current
            for change_row, change_col in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                neighbor = (row + change_row, col + change_col)
                if neighbor in board["walls"] or neighbor in distances:
                    continue
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)

        all_distances[goal] = distances

    return all_distances


def heuristic(boxes, goals, goal_distances):
    """Cộng khoảng cách mê cung nhỏ nhất từ mỗi hộp tới một đích."""
    estimate = 0

    for box in boxes:
        nearest_distance = float("inf")
        for goal in goals:
            if box in goal_distances[goal]:
                nearest_distance = min(nearest_distance, goal_distances[goal][box])
        if nearest_distance == float("inf"):
            return nearest_distance
        estimate += nearest_distance

    return estimate


def solve(board, algorithm):
    """Giải bản đồ bằng UCS hoặc A*, trả lời giải và vài số liệu dễ đọc."""
    if algorithm not in ("ucs", "astar"):
        raise ValueError("Tên thuật toán cần là 'ucs' hoặc 'astar'.")

    start_time = time.perf_counter()
    start_state = board["start"]
    goal_distances = build_goal_distances(board)
    order = 0
    start_h = heuristic(start_state[1], board["goals"], goal_distances) if algorithm == "astar" else 0

    # Phần tử trong hàng đợi: (độ ưu tiên, chi phí, số thứ tự, trạng thái, đường đi).
    frontier = [(start_h, 0, order, start_state, [])]
    best_cost = {start_state: 0}
    expanded = 0
    generated = 1
    peak_frontier = 1

    while frontier:
        _priority, cost, _order, state, actions = heapq.heappop(frontier)

        # Có thể còn mục cũ trong hàng đợi nếu sau đó tìm được đường đi tốt hơn.
        if cost != best_cost.get(state):
            continue

        if is_goal(board, state):
            return {
                "actions": actions,
                "cost": cost,
                "expanded": expanded,
                "generated": generated,
                "peak_frontier": peak_frontier,
                "time": time.perf_counter() - start_time,
            }

        expanded += 1
        for action, next_state in get_next_states(board, state):
            generated += 1
            new_cost = cost + 1
            if new_cost >= best_cost.get(next_state, float("inf")):
                continue

            best_cost[next_state] = new_cost
            if algorithm == "astar":
                estimate = heuristic(next_state[1], board["goals"], goal_distances)
            else:
                estimate = 0

            # Nếu giá trị vô cực thì hộp không thể đi tới đích theo đường không xuyên tường.
            if estimate == float("inf"):
                continue

            order += 1
            priority = new_cost + estimate
            heapq.heappush(
                frontier,
                (priority, new_cost, order, next_state, actions + [action]),
            )
        peak_frontier = max(peak_frontier, len(frontier))

    return {
        "actions": None,
        "cost": None,
        "expanded": expanded,
        "generated": generated,
        "peak_frontier": peak_frontier,
        "time": time.perf_counter() - start_time,
    }
