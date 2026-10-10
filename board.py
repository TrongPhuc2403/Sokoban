"""Đọc bản đồ Sokoban, sinh nước đi và vẽ bàn cờ."""

from pathlib import Path


# Một trạng thái được lưu thành (vị trí người chơi, các vị trí hộp).
# Tọa độ có dạng (hàng, cột); danh sách hộp được sắp xếp để dễ so sánh.


def read_map(file_name):
    """Đọc tệp bản đồ và trả về dữ liệu bàn cờ."""
    lines = Path(file_name).read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError("Tệp bản đồ đang trống.")

    walls = set()
    goals = set()
    boxes = []
    players = []
    width = max(len(line) for line in lines)

    for row in range(len(lines)):
        for col in range(width):
            # Tệp bản đồ trong ZIP xem phần dòng bị thiếu là ô trống.
            cell = lines[row][col] if col < len(lines[row]) else " "
            position = (row, col)

            if cell == "%":
                walls.add(position)
            elif cell == "A":
                players.append(position)
            elif cell == "B":
                boxes.append(position)
            elif cell == "D":
                goals.add(position)
            elif cell == "C":
                boxes.append(position)
                goals.add(position)
            elif cell != " ":
                raise ValueError(f"Ký hiệu {cell!r} không hợp lệ ở dòng {row + 1}.")

    if len(players) != 1:
        raise ValueError("Bản đồ cần có đúng một người chơi A.")
    if len(boxes) != len(goals):
        raise ValueError("Số hộp phải bằng số đích.")

    board = {
        "walls": walls,
        "goals": goals,
        "height": len(lines),
        "width": width,
        "start": (players[0], tuple(sorted(boxes))),
    }
    return board


def get_next_states(board, state):
    """Trả về các nước đi hợp lệ cùng trạng thái sau mỗi nước đi."""
    player, boxes = state
    box_set = set(boxes)
    # Mỗi mục gồm tên hướng và thay đổi hàng, cột.
    directions = [
        ("North", -1, 0),
        ("East", 0, 1),
        ("South", 1, 0),
        ("West", 0, -1),
    ]
    next_states = []

    def is_blocked(position):
        row, col = position
        outside_board = row < 0 or row >= board["height"] or col < 0 or col >= board["width"]
        return outside_board or position in board["walls"]

    for name, row_change, col_change in directions:
        next_player = (player[0] + row_change, player[1] + col_change)
        if is_blocked(next_player):
            continue

        next_boxes = boxes
        if next_player in box_set:
            # Người chơi đang đẩy hộp; ô phía sau hộp phải trống.
            box_destination = (next_player[0] + row_change, next_player[1] + col_change)
            if is_blocked(box_destination) or box_destination in box_set:
                continue
            moved_boxes = box_set.copy()
            moved_boxes.remove(next_player)
            moved_boxes.add(box_destination)
            next_boxes = tuple(sorted(moved_boxes))

        next_states.append((name, (next_player, next_boxes)))

    return next_states


def is_goal(board, state):
    """Đích đạt được khi mọi hộp đều ở trên ô đích."""
    _player, boxes = state
    return set(boxes) == board["goals"]


def draw_board(board, state):
    """Tạo chuỗi bàn cờ để in ra terminal."""
    player, boxes = state
    box_set = set(boxes)
    rows = []

    for row in range(board["height"]):
        cells = []
        for col in range(board["width"]):
            position = (row, col)
            if position in board["walls"]:
                cell = "%"
            elif position == player:
                cell = "A"
            elif position in box_set and position in board["goals"]:
                cell = "C"
            elif position in box_set:
                cell = "B"
            elif position in board["goals"]:
                cell = "D"
            else:
                cell = " "
            cells.append(cell)
        rows.append("".join(cells).rstrip())

    return "\n".join(rows)
