# Hướng dẫn và báo cáo Sokoban

## Đối chiếu rubric

| Mục rubric | Nội dung trong dự án |
|---|---|
| Formulation – 2 điểm | Mô hình trạng thái, hành động, trạng thái đầu, trạng thái đích và chi phí ở phần 1. |
| Uninformed Search – 3 điểm | UCS ở phần 2; chạy được và xem được từng bước bằng `main.py`. |
| Informed Search – 3 điểm | A* cùng heuristic BFS ở phần 3; so sánh bằng `compare.py`. |
| Trình bày – 1 điểm | Dàn ý và lời nói gợi ý ở phần 5. |
| Trả lời câu hỏi – 1 điểm | Câu hỏi thường gặp và câu trả lời ngắn ở phần 6. |

## 1. Mô hình hóa bài toán

- **Trạng thái:** vị trí người chơi và vị trí tất cả các hộp. Có thể viết là `s = (p, B)`, trong đó `p` là tọa độ người chơi và `B` là tập tọa độ các hộp. Tường và đích không đổi nên lưu riêng trong bản đồ.
- **Trạng thái đầu:** đọc từ bản đồ: `A` là vị trí người chơi; `B` là hộp; `C` là hộp đã nằm trên đích.
- **Hành động:** đi lên, phải, xuống hoặc trái một ô. Nếu ô kế tiếp có hộp, người chơi đẩy hộp thêm một ô cùng hướng.
- **Điều kiện hành động hợp lệ:** không đi vào tường; không đẩy hộp vào tường hoặc vào một hộp khác.
- **Trạng thái đích:** mọi hộp được đặt lên đích. Với bản đồ hợp lệ có cùng số hộp và số đích, điều này tương đương vị trí hộp trùng với vị trí các đích.
- **Chi phí:** mỗi lần người chơi di chuyển một ô có chi phí 1, dù đó là đi bộ hay đẩy hộp. Mục tiêu là tìm chuỗi hành động có tổng chi phí nhỏ nhất.

## 2. Tìm kiếm không thông tin: UCS

UCS là Uniform Cost Search. Trong dự án này mỗi hành động tốn 1, vì vậy UCS luôn lấy khỏi hàng đợi trạng thái có chi phí đường đi `g` nhỏ nhất.

Các bước chính trong chương trình:

1. Đưa trạng thái đầu vào hàng đợi với chi phí 0.
2. Lấy trạng thái có chi phí nhỏ nhất.
3. Nếu trạng thái đã giải xong, trả về danh sách hành động.
4. Nếu chưa, tạo các trạng thái sau những hành động hợp lệ.
5. Cập nhật trạng thái nếu vừa tìm được đường đi rẻ hơn.

UCS đảm bảo tìm đường đi có chi phí nhỏ nhất khi mọi chi phí hành động không âm. Vì chi phí của bài này bằng 1, nó cũng cho lời giải tối ưu. Nhược điểm là có thể mở rộng nhiều trạng thái vì UCS không biết trạng thái nào gần đích hơn.

## 3. Tìm kiếm có thông tin: A*

A* ưu tiên trạng thái theo `f(n) = g(n) + h(n)`:

- `g(n)` là số bước đã đi từ đầu tới trạng thái hiện tại.
- `h(n)` là ước lượng số bước còn lại để đưa hộp tới đích.

### Heuristic được dùng

1. Với mỗi đích, BFS tính khoảng cách ngắn nhất tới các ô có thể đi qua mà không xuyên tường.
2. Với mỗi hộp, lấy khoảng cách nhỏ nhất tới một đích bất kỳ.
3. Cộng các khoảng cách nhỏ nhất đó làm `h(n)`.

Heuristic cố ý bỏ qua việc người chơi phải đi tới phía sau hộp để đẩy, và bỏ qua tương tác giữa các hộp. Các khoảng cách vì vậy là ước lượng đơn giản, thường thấp hơn chi phí lời giải thực tế. Heuristic không dùng khoảng cách Manhattan hay Euclid.

### Tính chất heuristic

- **Chấp nhận được:** mỗi hộp cần ít nhất một số bước di chuyển để tới một đích. Khoảng cách ngắn nhất qua ô đi được không lớn hơn đường đi thực tế; bỏ qua đường vòng của người chơi và cản trở giữa các hộp cũng không làm ước lượng tăng. Do đó `h(n)` là cận dưới của số bước còn lại.
- **Nhất quán:** khi người chơi chỉ đi bộ, vị trí hộp không đổi nên `h` giữ nguyên. Khi đẩy một hộp một ô, khoảng cách tới đích của hộp đó có thể giảm tối đa một; các hộp khác không đổi. Vì mỗi hành động tốn 1 nên `h(n) ≤ 1 + h(n')`.
- Tại trạng thái đích, mọi hộp đã ở đích nên `h(n) = 0`.

Đây là lập luận cho cách tính heuristic trong mã. Thí nghiệm ở dưới là kiểm tra thực nghiệm trên bản đồ nhỏ, không thay thế chứng minh tổng quát.

## 4. Thí nghiệm so sánh

Chạy `python compare.py maps/map_small.txt` hoặc `python compare.py maps/map_medium.txt`. Hai thuật toán chạy trên cùng bản đồ và cùng hàm kiểm tra đích. Chương trình ghi lại chi phí lời giải, số trạng thái mở rộng, số trạng thái sinh, kích thước frontier lớn nhất và thời gian chạy.

| Bản đồ | Thuật toán | Chi phí | Mở rộng | Sinh | Frontier lớn nhất | Thời gian (giây) |
|---|---|---:|---:|---:|---:|---:|
| nhỏ | UCS | 1 | 2 | 8 | 5 | 0,000220 |
| nhỏ | A* | 1 | 1 | 5 | 4 | 0,000024 |
| vừa | UCS | 11 | 1.481 | 4.714 | 604 | 0,003985 |
| vừa | A* | 11 | 448 | 1.450 | 280 | 0,001985 |

Cả hai thuật toán trả về cùng chi phí trên từng bản đồ, phù hợp với yêu cầu lời giải tối ưu. A* mở rộng ít trạng thái hơn: 1 so với 2 trên bản đồ nhỏ và 448 so với 1.481 trên bản đồ vừa. Thời gian rất ngắn và phụ thuộc máy tính, nên số trạng thái mở rộng dễ đối chiếu hơn thời gian.

Các số đo có thể thay đổi nhẹ ở mỗi lần chạy do môi trường. Nếu muốn cập nhật báo cáo, hãy chạy lại lệnh `compare.py` và thay các dòng trong bảng bằng số vừa in.

## 5. Dàn ý thuyết trình ngắn

1. **Giới thiệu:** “Em xây dựng chương trình tìm lời giải Sokoban bằng UCS và A*. Mỗi hành động có chi phí 1 và chương trình có thể in trạng thái bàn cờ sau từng bước.”
2. **Mô hình hóa:** giải thích trạng thái là vị trí người chơi cộng với vị trí các hộp; hành động gồm bốn hướng; đích là đưa tất cả hộp lên đích.
3. **UCS:** giải thích chương trình chọn trạng thái có tổng số bước đã đi nhỏ nhất; ưu điểm là tối ưu, nhược điểm là có thể duyệt nhiều trạng thái.
4. **A*:** giải thích A* cộng chi phí đã đi và ước lượng còn lại. Nêu heuristic dùng BFS trên bản đồ và không dùng Manhattan/Euclid.
5. **Kết quả:** chạy `python compare.py maps/map_medium.txt`; chỉ vào chi phí bằng nhau và số trạng thái A* mở rộng ít hơn.
6. **Kết thúc:** chạy `python main.py maps/map_small.txt astar` để minh họa chuỗi hành động và bàn cờ sau mỗi bước.

## 6. Câu hỏi có thể được hỏi

**Hỏi: Trạng thái của bài toán gồm những gì?**  
Đáp: Vị trí người chơi và vị trí của tất cả các hộp. Tường và đích là dữ liệu cố định của bản đồ.

**Hỏi: Vì sao UCS tìm được lời giải tối ưu?**  
Đáp: UCS mở rộng trạng thái có chi phí đã đi nhỏ nhất. Mỗi hành động có chi phí 1, nên trạng thái đích đầu tiên được lấy ra cho ta lời giải ít bước nhất.

**Hỏi: A* khác UCS ở điểm nào?**  
Đáp: UCS chỉ nhìn chi phí đã đi `g`; A* dùng `g + h`, trong đó `h` ước lượng khoảng cách còn lại.

**Hỏi: Heuristic có dùng Manhattan hoặc Euclid không?**  
Đáp: Không. Chương trình dùng BFS để tính khoảng cách qua các ô không phải tường.

**Hỏi: Vì sao heuristic không đếm chính xác số bước?**  
Đáp: Để đơn giản, heuristic bỏ qua đường vòng người chơi phải đi và sự cản trở giữa các hộp. Nó chỉ cần cho một cận dưới để hướng A*.

**Hỏi: Chương trình có luôn tìm được lời giải không?**  
Đáp: Nếu có lời giải và đủ thời gian/bộ nhớ để duyệt không gian trạng thái thì UCS và A* sẽ tìm được. Bản đồ lớn có thể khiến việc tìm kiếm tốn nhiều tài nguyên.

**Hỏi: Vì sao A* có lúc không nhanh hơn nhiều?**  
Đáp: Hiệu quả phụ thuộc bản đồ và chất lượng heuristic. Nếu heuristic chỉ ước lượng thấp, A* vẫn phải mở rộng nhiều trạng thái.

## 7. Giới hạn phạm vi

ZIP có mã cho chế độ hai người chơi A* đối đầu GBFS. Tài liệu rubric được gửi kèm chỉ phân điểm cho mô hình hóa, tìm kiếm không thông tin, tìm kiếm có thông tin và trình bày/trả lời; không nêu phần thi đấu hai người chơi. Bản viết lại vì thế làm rõ các mục rubric đó, chưa cài chế độ hai người chơi.
