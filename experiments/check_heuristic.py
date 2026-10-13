"""Thí nghiệm YC4: kiểm tra admissibility và consistency của heuristic."""

from collections import deque
from pathlib import Path
import sys
import time

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from single_agent.game_env import SokobanEnv
from single_agent.solver import SokobanSolver


def check_map(map_file):
    """Tính khoảng cách tối ưu thật và kiểm tra mọi trạng thái/cạnh đạt được."""
    started = time.perf_counter()
    env = SokobanEnv(map_file)
    solver = SokobanSolver(env)
    start = (env.initial_agent, tuple(sorted(env.initial_boxes)))

    # Liệt kê toàn bộ đồ thị trạng thái đi tới được từ trạng thái đầu.
    states = {start}
    edges = []
    reverse_edges = {}
    queue = deque([start])

    while queue:
        state = queue.popleft()
        for _action, next_state in solver._get_successors(state):
            edges.append((state, next_state))
            reverse_edges.setdefault(next_state, []).append(state)
            if next_state not in states:
                states.add(next_state)
                queue.append(next_state)

    # BFS ngược từ mọi trạng thái đích cho khoảng cách tối ưu h*(n).
    goal_states = [state for state in states if solver._is_goal(state)]
    exact_cost = {state: 0 for state in goal_states}
    queue = deque(goal_states)
    while queue:
        state = queue.popleft()
        for previous in reverse_edges.get(state, []):
            if previous not in exact_cost:
                exact_cost[previous] = exact_cost[state] + 1
                queue.append(previous)

    # Admissible: h(n) không vượt quá khoảng cách thật ở trạng thái giải được.
    admissible_checks = 0
    for state in states:
        h_value = solver.heuristic(state[1])
        if state in exact_cost:
            assert h_value != float('inf')
            assert h_value <= exact_cost[state], (state, h_value, exact_cost[state])
            admissible_checks += 1
        if solver._is_goal(state):
            assert h_value == 0

    # Consistent: h(n) <= 1 + h(n') cho mỗi hành động có chi phí 1.
    for state, next_state in edges:
        h_current = solver.heuristic(state[1])
        h_next = solver.heuristic(next_state[1])
        if h_current == float('inf'):
            assert h_next == float('inf'), (state, next_state)
        elif h_next != float('inf'):
            assert h_current <= 1 + h_next, (state, next_state, h_current, h_next)

    return {
        'map': Path(map_file).name,
        'states': len(states),
        'solvable': len(exact_cost),
        'dead_ends': len(states) - len(exact_cost),
        'admissible': admissible_checks,
        'edges': len(edges),
        'seconds': time.perf_counter() - started,
    }


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    maps = [
        PROJECT_FOLDER / 'maps' / 'map_small.txt',
        PROJECT_FOLDER / 'maps' / 'map_medium.txt',
    ]
    print('YC4 – KIỂM TRA HEURISTIC, ĐỘC LẬP VỚI THÍ NGHIỆM YC3')
    for map_file in maps:
        result = check_map(map_file)
        print(
            f"{result['map']}: {result['states']} trạng thái; "
            f"{result['solvable']} trạng thái có lời giải; "
            f"{result['dead_ends']} trạng thái bế tắc; "
            f"admissibility {result['admissible']} trạng thái đạt; "
            f"consistency {result['edges']} cạnh đạt; "
            f"{result['seconds']:.4f} giây."
        )
    print('Không phát hiện vi phạm trong các trạng thái và cạnh đã kiểm tra.')


if __name__ == '__main__':
    main()
