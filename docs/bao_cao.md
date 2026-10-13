# Báo cáo Sokoban theo yêu cầu 1–4

## YC1 – Mô hình hóa bài toán tìm kiếm

- **Trạng thái:** `s = (p, B)`, trong đó `p` là tọa độ người chơi và `B` là tập vị trí các hộp. Tường và đích cố định được lưu trong môi trường.
- **Trạng thái đầu:** đọc từ tệp bản đồ, ký hiệu `A` là người chơi, `B` là hộp, `C` là hộp đang ở trên đích.
- **Hành động:** đi một ô theo Bắc, Đông, Nam hoặc Tây. Nếu ô kế bên có hộp thì đẩy hộp đi cùng hướng.
- **Hành động hợp lệ:** người chơi không đi vào tường hoặc ra ngoài bản đồ; hộp không thể bị đẩy vào tường, ra ngoài hoặc đè lên hộp khác.
- **Mô hình chuyển:** cập nhật tọa độ người chơi; khi đẩy, cập nhật thêm vị trí của hộp.
- **Trạng thái đích:** mọi hộp nằm trên một đích. Bản đồ đầu vào yêu cầu số hộp bằng số đích.
- **Chi phí:** mỗi lần đi bộ hoặc đẩy hộp có chi phí 1; tổng chi phí là số hành động.

## YC2 – UCS, A* và heuristic

### UCS

Uniform Cost Search chọn trạng thái có `g(n)` nhỏ nhất, với `g(n)` là số bước đã đi. Với chi phí mỗi bước bằng 1, UCS tìm được lời giải có ít bước nhất.

### A*

A* chọn trạng thái theo `f(n) = g(n) + h(n)`. Mã dùng BFS từ từng đích để tính khoảng cách ngắn nhất qua các ô không phải tường. Heuristic cộng khoảng cách mê cung nhỏ nhất từ mỗi hộp tới một đích bất kỳ. Cách tính không dùng Manhattan hoặc Euclid.

Heuristic bỏ qua đường vòng mà người chơi cần đi để đứng phía sau hộp và bỏ qua tương tác giữa hộp. Vì mỗi bước mà hộp di chuyển cần một lần đẩy và mỗi lần đẩy là một hành động trong bài toán, tổng khoảng cách ngắn nhất của hộp không vượt quá chi phí lời giải thật. Khi người chơi đi bộ, vị trí hộp không đổi; khi đẩy một hộp một ô, khoảng cách của hộp đó có thể giảm tối đa một. Do vậy heuristic có cận dưới và nhất quán theo chi phí bước bằng 1.

## YC3 – Thí nghiệm so sánh UCS và A*

Chạy `python experiments/compare_algorithms.py`. UCS và A* nhận cùng một bản đồ và cùng điều kiện đích. Chương trình ghi chi phí lời giải, số trạng thái mở rộng, số trạng thái sinh, frontier lớn nhất và thời gian chạy.

| Bản đồ | Thuật toán | Chi phí | Mở rộng | Sinh | Frontier lớn nhất | Thời gian (ms) |
|---|---|---:|---:|---:|---:|---:|
| nhỏ | UCS | 1 | 2 | 8 | 5 | 0,033 |
| nhỏ | A* | 1 | 1 | 5 | 4 | 0,014 |
| vừa | UCS | 11 | 1.481 | 4.714 | 604 | 4,507 |
| vừa | A* | 11 | 448 | 1.450 | 280 | 1,948 |

Trên bản đồ vừa, hai thuật toán tìm cùng chi phí, trong khi A* mở rộng ít trạng thái hơn. Thời gian đo trong lần chạy này phụ thuộc máy tính; chạy script để ghi số mới trên máy đang sử dụng.

Với `V` trạng thái và `E` chuyển tiếp đã khám phá, heap và bảng chi phí cho thời gian thường được mô tả là `O((V + E) log V)`. Trong trường hợp xấu nhất, không gian trạng thái Sokoban tăng theo số cách đặt các hộp và người chơi lên ô trống; cả UCS và A* có thể cần thời gian và bộ nhớ theo hàm mũ. Thí nghiệm dùng số trạng thái mở rộng và frontier lớn nhất để so sánh lượng công việc/bộ nhớ quan sát được, cùng với thời gian chạy. Mã lưu danh sách hành động trên các nhánh đang chờ nên bộ nhớ thực tế còn phụ thuộc độ dài các đường đi được giữ trong frontier.

## YC4 – Thí nghiệm kiểm tra heuristic, độc lập với YC3

Đây là thí nghiệm riêng cho tính chất heuristic. Không dùng bảng hoặc số liệu so sánh UCS/A* ở YC3 làm bằng chứng cho YC4.

Chạy `python experiments/check_heuristic.py`. Chương trình:

1. Liệt kê toàn bộ trạng thái đi tới được từ trạng thái đầu và lưu các cạnh chuyển tiếp hợp lệ.
2. Duyệt ngược từ mọi trạng thái đích bằng BFS để tính khoảng cách tối ưu thật `h*(n)` cho từng trạng thái có lời giải.
3. Kiểm tra `h(n) ≤ h*(n)` trên mọi trạng thái có đường tới đích và kiểm tra `h(n)=0` tại trạng thái đích.
4. Trên mọi cạnh `n → n'`, kiểm tra `h(n) ≤ 1 + h(n')`. Chi phí cạnh là 1. Với heuristic vô cực, kiểm tra trạng thái kế tiếp cũng vô cực.

Lệnh `assert` làm chương trình dừng nếu tìm thấy vi phạm. Trạng thái không có đường tới đích có `h*(n)=∞`; với heuristic không âm thì bất đẳng thức admissible vẫn được thỏa mãn.

| Bản đồ | Trạng thái đạt được | Có lời giải tới đích | Bế tắc | Admissibility đã kiểm tra | Cạnh consistency đã kiểm tra | Thời gian (giây) | Kết quả |
|---|---:|---:|---:|---:|---:|---:|---|
| nhỏ | 132 | 33 | 99 | 33 trạng thái | 360 cạnh | 0,0010 | Không phát hiện vi phạm |
| vừa | 6.068 | 2.376 | 3.692 | 2.376 trạng thái | 18.724 cạnh | 0,0732 | Không phát hiện vi phạm |

Kết quả này phù hợp với lập luận ở YC2 trên toàn bộ trạng thái đạt được của hai bản đồ đã thử. Đây là kiểm tra thực nghiệm hữu hạn, không thay thế chứng minh cho mọi bản đồ Sokoban.

## Gợi ý trình bày và câu hỏi

1. Giới thiệu trạng thái, hành động, trạng thái đầu và trạng thái đích.
2. Mô tả UCS: chọn trạng thái có chi phí đã đi nhỏ nhất.
3. Mô tả A*: cộng chi phí đã đi với heuristic BFS.
4. Chạy `python experiments/compare_algorithms.py` để nói về YC3.
5. Chạy `python experiments/check_heuristic.py` để trình bày riêng YC4.
6. Mở GUI để minh họa chuyển động; giải thích các ký hiệu trên bản đồ.

**Vì sao UCS tối ưu?** Chi phí mỗi hành động không âm; UCS mở rộng theo chi phí đường đi tăng dần.

**A* khác UCS thế nào?** UCS dùng `g(n)`, còn A* dùng `g(n)+h(n)` để ưu tiên trạng thái ước lượng gần đích.

**Heuristic dùng Manhattan không?** Không. Khoảng cách được tính bằng BFS trên lưới và có xét tường.

**YC4 khác YC3 thế nào?** YC3 so sánh hiệu quả UCS/A*. YC4 kiểm tra bất đẳng thức admissible và consistent của heuristic trên đồ thị trạng thái.
