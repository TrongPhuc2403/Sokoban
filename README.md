# Dự án Sokoban

Dự án gồm phần Sokoban một tác nhân theo yêu cầu 1–4 và phần thi đấu hai tác nhân theo các mục 5–8 trong mã nguồn gốc. Mã được tách theo chức năng; chú thích và tài liệu dùng tiếng Việt có dấu. Các thuật toán được viết thành những bước nhỏ để thuận tiện đọc và chỉnh sửa.

## Cấu trúc thư mục

```text
AI/
├── maps/                         # Bản đồ đầu vào
├── single_agent/                 # Sokoban một người chơi
│   ├── game_env.py               # Trạng thái, luật đi, undo và hiển thị
│   ├── solver.py                 # UCS, A* và heuristic khoảng cách mê cung
│   ├── main_cli.py               # Chạy lời giải trong terminal
│   └── main_gui.py               # Giao diện Pygame
├── two_agent/                    # Sokoban đối kháng hai người chơi
│   ├── game_env_2p.py            # Luật lượt đồng thời, va chạm, điểm và undo
│   ├── player1.py                # Agent 1 dùng A* (f = g + h)
│   ├── player2.py                # Agent 2 dùng GBFS (f = h)
│   └── main_gui_2p.py            # Giao diện trận đấu
├── experiments/
│   ├── compare_algorithms.py     # YC3: đo riêng UCS và A*
│   └── check_heuristic.py        # YC4: kiểm tra tính chất heuristic
├── docs/bao_cao.md                # Mô hình, phân tích và kết quả YC1–4
├── test_all.py                   # Kiểm tra nhanh phần một và hai tác nhân
└── HUONG_DAN_CHAY.txt            # Hướng dẫn ngắn
```

## Yêu cầu môi trường

- Python 3.10 trở lên.
- Chỉ cần cài `pygame` nếu chạy giao diện đồ họa.
- Mở terminal tại thư mục `AI/` trước khi chạy các lệnh bên dưới.

```text
python -m pip install pygame
```

## YC1–4: Sokoban một tác nhân

Mỗi trạng thái gồm vị trí người chơi và tập vị trí các hộp. Mỗi hành động là một bước lên, xuống, trái hoặc phải; hành động đẩy hộp chỉ hợp lệ nếu ô phía sau hộp trống. Trạng thái kết thúc khi tất cả hộp ở trên đích. Chi phí mỗi bước bằng 1.

UCS mở rộng trạng thái có chi phí đường đi nhỏ nhất. A* dùng `f(n) = g(n) + h(n)`, trong đó `h` là tổng khoảng cách mê cung từ hộp tới đích gần nhất tương ứng; khoảng cách được tính bằng BFS trên bản đồ, không dùng khoảng cách Euclid hay Manhattan. YC3 đo UCS và A* riêng trên bản đồ mẫu. YC4 có chương trình kiểm tra riêng tính admissible và consistency bằng duyệt trạng thái, cạnh chuyển tiếp và so sánh với chi phí tối ưu.

Chạy kiểm tra cơ bản và thí nghiệm:

```text
python test_all.py
python single_agent/main_cli.py maps/map_small.txt astar
python experiments/compare_algorithms.py
python experiments/check_heuristic.py
```

Tham số thuật toán của CLI nhận `ucs` hoặc `astar`. Có thể thay `map_small.txt` bằng một tệp bản đồ khác.

Giao diện đồ họa:

```text
python single_agent/main_gui.py maps/map_medium.txt
```

Trong GUI, phím `1` chạy UCS, `2` chạy A*, phím cách chạy/tạm dừng, mũi tên phải tiến một bước, mũi tên trái hoàn tác và `R` đặt lại bản đồ.

## YC5–6: Môi trường thi đấu hai tác nhân

Hai tác nhân chọn hành động từ cùng một trạng thái rồi môi trường áp dụng trong một lượt đồng thời. Nếu hai người chơi va chạm, đổi chỗ, cùng muốn vào một ô hoặc xung đột khi đẩy hộp, các nước đi liên quan bị hủy để tránh chồng lấn trạng thái. Đi ra ngoài biên, vào tường, đẩy hộp ra ngoài bản đồ hoặc đẩy vào hộp khác đều không làm thay đổi vị trí. Mỗi lượt hợp lệ của trận đấu tăng bộ đếm một lần.

Hộp nằm trên đích được tính điểm cho tác nhân đã đẩy hộp vào đích. Đẩy hộp ra khỏi đích sẽ xóa quyền sở hữu điểm. Trận đấu kết thúc khi hết số lượt cấu hình, tất cả đích có hộp hoặc tất cả hộp nằm trên đích; điểm cao hơn thắng, bằng điểm thì hòa. Môi trường có `undo()` để quay lại trạng thái trước đó.

## YC7–8: Agent A* và GBFS

Agent 1 trong `player1.py` dùng A* với `f = g + h`; Agent 2 trong `player2.py` dùng GBFS với `f = h`. Cả hai tính khoảng cách mê cung bằng BFS, tránh các ô deadlock phát hiện bằng duyệt ngược từ đích và trả về một trong các hướng `North`, `South`, `West`, `East` hoặc `Wait`. GUI đưa trạng thái chung cho cả hai bộ chọn, sau đó gửi hai hành động vào môi trường trong cùng lượt.

Chạy trận đấu mặc định trên bản đồ đối kháng, giới hạn 60 lượt:

```text
python two_agent/main_gui_2p.py maps/map_competitive.txt 60
```

Có thể đổi bản đồ hoặc số lượt, ví dụ:

```text
python two_agent/main_gui_2p.py maps/map_competitive.txt 30
```

Trong giao diện hai tác nhân: phím cách chạy/tạm dừng, mũi tên phải tính và chạy một lượt, mũi tên trái hoàn tác, `R` bắt đầu lại. Bảng bên phải hiển thị số lượt, điểm và hành động gần nhất.

## Định dạng bản đồ

Mỗi ký tự tương ứng một ô; giữ nguyên khoảng trắng ở cuối dòng nếu cần để bảo toàn bề rộng bản đồ.

| Ký hiệu | Ý nghĩa |
|---|---|
| `%` | Tường |
| `A` | Người chơi trong chế độ một tác nhân; vị trí Agent 1 trong chế độ hai tác nhân |
| `Z` | Vị trí Agent 2 trong chế độ hai tác nhân |
| `B` | Hộp |
| `D` | Đích |
| `C` | Hộp đang nằm trên đích |
| Dấu cách | Ô trống |

## Tài liệu kết quả

Kết quả đo UCS/A* và kiểm chứng heuristic được ghi trong [docs/bao_cao.md](docs/bao_cao.md). Thời gian chạy có thể thay đổi tùy máy; số trạng thái mở rộng, sinh ra và kích thước frontier hữu ích hơn để so sánh giữa các lần chạy.
