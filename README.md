# Sokoban AI Project

Dự án AI giữa kỳ: Trò chơi Sokoban chế độ 1 Agent (UCS, A*) và chế độ 2 Agent đối kháng (A* vs GBFS).

## 1. Cài đặt môi trường
- Python 3.10 - 3.13 (tương thích Windows và macOS 13.7.8 Ventura chip Intel)
- Cài đặt thư viện phụ thuộc (pygame==2.6.1):
```bash
pip install -r requirements.txt
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
- Phím 1 hoặc bấm nút UCS: Chạy thuật toán UCS
- Phím 2 hoặc bấm nút A*: Chạy thuật toán A*
- Thanh bên hiển thị số action, tổng chi phí, chuỗi action (N/E/S/W) và thông số thuật toán
- Space: Tự động chạy / Tạm dừng
- Phím mũi tên Phải (->): Tiến 1 bước
- Phím mũi tên Trái (<-): Lùi 1 bước (Undo)
- Phím R: Đặt lại trạng thái ban đầu

### Chế độ 2 Agent đối kháng
```bash
python two_agent/main_gui_2p.py maps/map_competitive.txt 60
```
- Số bước `n` do người dùng nhập: truyền qua dòng lệnh (ví dụ `60`), hoặc bỏ trống để nhập ngay trong cửa sổ game.
- Trận đấu kết thúc sau đúng `n` bước; agent có nhiều hộp trên đích hơn thắng.
- Agent có thể đẩy hộp đối thủ đã đặt vào đích ra ngoài rồi đặt lại để giành điểm.
- Thi đấu với nhóm khác: `python two_agent/main_gui_2p.py maps/map_competitive.txt 60 path/to/p1.py path/to/p2.py`
- Space: Tự động thi đấu / Tạm dừng
- Phím mũi tên Phải (->): Tiến 1 bước
- Phím mũi tên Trái (<-): Lùi 1 bước (Undo)
- Phím R: Bắt đầu lại trận đấu
- Phím N: Nhập lại số bước n
