"""Chạy UCS và A* trên cùng một bản đồ để đối chiếu."""

import sys

from sokoban.board import read_map
from sokoban.solver import solve


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    map_file = sys.argv[1] if len(sys.argv) > 1 else "maps/map_medium.txt"
    board = read_map(map_file)

    print(f"So sánh trên bản đồ: {map_file}")
    print("Thuật toán | Chi phí | Mở rộng | Sinh | Frontier lớn nhất | Thời gian (giây)")
    for algorithm in ("ucs", "astar"):
        result = solve(board, algorithm)
        print(
            f"{algorithm.upper()} | {result['cost']} | {result['expanded']} | "
            f"{result['generated']} | {result['peak_frontier']} | {result['time']:.6f}"
        )


if __name__ == "__main__":
    main()
