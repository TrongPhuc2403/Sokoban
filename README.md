# Sokoban AI Project

Dự án AI giữa kỳ: Trò chơi Sokoban chế độ 1 Agent (UCS, A*) và chế độ 2 Agent đối kháng (A* vs GBFS).

## 1. Cài đặt môi trường
- Python 3.10+ (tương thích cả Windows và macOS)
- Cài đặt thư viện phụ thuộc:
```bash
pip install pygame
```

## 2. Cấu trúc thư mục
```
AI/
├── maps/
│   ├── example_map.txt        # Bản đồ gốc của đề bài
│   ├── map_small.txt          # Bản đồ nhỏ kiểm thử nhanh
│   ├── map_medium.txt         # Bản đồ kiểm thử 1 agent
│   └── map_competitive.txt    # Bản đồ 2 agent đối kháng
├── single_agent/
│   ├── game_env.py            # Môi trường 1 agent và undo
│   ├── solver.py              # Thuật toán UCS và A* (Maze Distance)
│   └── main_gui.py            # Giao diện Pygame 1 agent
├── two_agent/
│   ├── game_env_2p.py         # Môi trường 2 agent đối kháng đồng thời
│   ├── player1.py             # Agent 1 (Thuật toán A*)
│   ├── player2.py             # Agent 2 (Thuật toán Greedy Best-First Search)
│   └── main_gui_2p.py         # Giao diện Pygame thi đấu 2 agent
├── test_all.py                # Kiểm thử tự động toàn bộ tính năng
└── HUONG_DAN_CHAY.txt         # Hướng dẫn chi tiết
```

## 3. Cách chạy chương trình

### Chạy kiểm thử tự động
```bash
python test_all.py
```

### Chế độ 1 Agent (Sokoban)
```bash
python single_agent/main_gui.py maps/map_medium.txt
```
- Phím 1: Chạy thuật toán UCS
- Phím 2: Chạy thuật toán A*
- Space: Tự động chạy / Tạm dừng
- Phím mũi tên Phải (->): Tiến 1 bước
- Phím mũi tên Trái (<-): Lùi 1 bước (Undo)
- Phím R: Đặt lại trạng thái ban đầu

### Chế độ 2 Agent đối kháng
```bash
python two_agent/main_gui_2p.py maps/map_competitive.txt 60
```
- Space: Tự động thi đấu / Tạm dừng
- Phím mũi tên Phải (->): Tiến 1 bước
- Phím mũi tên Trái (<-): Lùi 1 bước (Undo)
- Phím R: Bắt đầu lại trận đấu
