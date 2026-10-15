# Dự án Sokoban

Dự án gồm phần Sokoban một tác nhân (Yêu cầu 1–4) và phần thi đấu hai tác nhân (Yêu cầu 5–8). Mã nguồn được chia theo module rõ ràng, có đầy đủ kiểm thử tự động và tài liệu thực nghiệm.

## Cấu trúc thư mục

```text
AI/
├── maps/                         # Các file bản đồ (.txt)
├── single_agent/                 # Sokoban một người chơi
│   ├── game_env.py               # Môi trường, trạng thái, undo
│   ├── solver.py                 # Bộ giải UCS, A* (khoảng cách mê cung BFS)
│   ├── main_cli.py               # Chạy giải thuật trên terminal
│   └── main_gui.py               # Giao diện đồ họa Pygame
├── two_agent/                    # Sokoban đối kháng hai người chơi
│   ├── game_env_2p.py            # Luật thi đấu đồng thời, va chạm, xác suất p, điểm số
│   ├── player1.py                # Agent 1: thuật toán A* (f = g + h)
│   ├── player2.py                # Agent 2: thuật toán GBFS (f = h)
│   └── main_gui_2p.py            # Giao diện thi đấu Pygame
├── experiments/
│   ├── compare_algorithms.py     # YC3: Thực nghiệm so sánh UCS và A*
│   └── check_heuristic.py        # YC4: Kiểm chứng tính admissible và consistent của heuristic
├── docs/
│   └── bao_cao.md                # Báo cáo mô hình không gian trạng thái & thực nghiệm
├── test_all.py                   # File kiểm tra tự động toàn bộ chức năng
└── HUONG_DAN_CHAY.txt            # Hướng dẫn chạy nhanh
```

## Cài đặt môi trường

- Python 3.10 trở lên (tương thích Windows, Linux và macOS Ventura).
- Cài đặt thư viện đồ họa:
```bash
pip install -r requirements.txt
```

---

## Hướng dẫn chạy các chức năng

### 1. Kiểm tra tự động
```bash
python test_all.py
```

### 2. YC1–4: Một tác nhân & Thực nghiệm
- Chạy giải thuật tìm kiếm trên terminal:
```bash
python single_agent/main_cli.py maps/map_small.txt astar
python single_agent/main_cli.py maps/map_small.txt ucs
```
- Chạy thực nghiệm so sánh UCS và A* (YC3):
```bash
python experiments/compare_algorithms.py
```
- Chạy kiểm chứng tính chất Heuristic (YC4):
```bash
python experiments/check_heuristic.py
```
- Chạy giao diện 1 người chơi (YC5 - Pygame):
```bash
python single_agent/main_gui.py maps/example_map.txt
```
  - Phím `1` / Nút UCS: Chạy UCS.
  - Phím `2` / Nút A*: Chạy A*.
  - Phím `Space`: Tạm dừng / Tiếp tục tự động.
  - Mũi tên `->`: Đi tới 1 bước.
  - Mũi tên `<-`: Lùi 1 bước (Undo).
  - Phím `R`: Đặt lại trạng thái ban đầu.

---

### 3. YC5–8: Thi đấu hai tác nhân đối kháng
- Chạy giao diện thi đấu:
```bash
python two_agent/main_gui_2p.py maps/map_competitive.txt 60
```
- Có thể chỉ định file code của 2 bot (hỗ trợ thi đấu giữa các nhóm):
```bash
python two_agent/main_gui_2p.py maps/map_competitive.txt 60 two_agent/player1.py two_agent/player2.py
```

#### Quy tắc thi đấu (Yêu cầu 6):
- Trận đấu kết thúc sau đúng `n` bước do người dùng nhập (nhập trên dòng lệnh hoặc bấm phím `N` trên giao diện).
- Hai agent hành động đồng thời trong mỗi lượt, không đi xuyên qua nhau.
- Agent được phép đẩy hộp của đối thủ ra khỏi ô đích rồi đặt lại để cướp điểm.
- **Xử lý tranh chấp:** Nếu hai agent cùng muốn đi vào một vị trí hoặc cùng đẩy một hộp:
  - Sinh ngẫu nhiên xác suất $p$ theo phân bố đều liên tục $U(0, 1)$.
  - Nếu $p < 0.5$: **Agent 1** thực hiện được hành động, **Agent 2** đứng yên (mất lượt).
  - Ngược lại ($p \ge 0.5$): **Agent 2** thực hiện được hành động, **Agent 1** đứng yên (mất lượt).
  - Giá trị $p$ và người thắng tranh chấp hiển thị trực tiếp ở bảng điều khiển bên phải.

#### Phím điều khiển trong giao diện 2 người chơi:
- `Space`: Tạm dừng / Tiếp tục.
- `->`: Tiến 1 bước.
- `<-`: Lùi 1 bước (Undo).
- `R`: Bắt đầu lại trận đấu.
- `N`: Nhập lại số bước `n`.
