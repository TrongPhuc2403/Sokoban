"""Thí nghiệm YC3: so sánh UCS và A* trên cùng bản đồ."""

from pathlib import Path
import sys

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from single_agent.game_env import SokobanEnv
from single_agent.solver import SokobanSolver


def compare_map(map_file):
    env = SokobanEnv(map_file)
    solver = SokobanSolver(env)
    print(f"\nBản đồ: {map_file}")
    print("Thuật toán | Chi phí | Mở rộng | Sinh | Frontier lớn nhất | Thời gian (ms)")

    for name, run in [('UCS', solver.solve_ucs), ('A*', solver.solve_astar)]:
        result = run()
        print(
            f"{name} | {result['cost']} | {result['expanded']} | "
            f"{result['generated']} | {result['peak_frontier']} | "
            f"{result['time_ms']:.3f}"
        )


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    maps = [
        PROJECT_FOLDER / 'maps' / 'map_small.txt',
        PROJECT_FOLDER / 'maps' / 'map_medium.txt',
    ]
    for map_file in maps:
        compare_map(map_file)


if __name__ == '__main__':
    main()
