"""Chạy một thuật toán Sokoban trên bản đồ được chọn."""

import sys

from sokoban.board import draw_board, get_next_states, read_map
from sokoban.solver import solve


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 3:
        print("Cách chạy: python main.py maps/map_small.txt ucs")
        print("Hoặc:     python main.py maps/map_small.txt astar")
        return

    map_file = sys.argv[1]
    algorithm = sys.argv[2].lower()
    board = read_map(map_file)
    result = solve(board, algorithm)

    print(f"Thuật toán: {algorithm.upper()}")
    print(f"Bản đồ: {map_file}")
    if result["actions"] is None:
        print("Không tìm thấy lời giải.")
    else:
        print(f"Chi phí (số bước): {result['cost']}")
        print("Các hành động:", " -> ".join(result["actions"]) or "Đã ở trạng thái đích")
        print("Bàn cờ sau khi giải:")
        state = board["start"]
        # Vẽ trạng thái đầu và từng trạng thái sau hành động để dễ theo dõi.
        print("Bắt đầu:")
        print(draw_board(board, state))
        for step, wanted_action in enumerate(result["actions"], start=1):
            for action, next_state in get_next_states(board, state):
                if action == wanted_action:
                    state = next_state
                    break
            print(f"\nBước {step}: {wanted_action}")
            print(draw_board(board, state))

    print(f"Trạng thái đã mở rộng: {result['expanded']}")
    print(f"Trạng thái đã sinh: {result['generated']}")
    print(f"Frontier lớn nhất: {result['peak_frontier']}")
    print(f"Thời gian: {result['time']:.6f} giây")


if __name__ == "__main__":
    main()
