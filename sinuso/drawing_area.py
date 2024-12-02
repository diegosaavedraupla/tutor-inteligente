from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QInputDialog, QMessageBox
from PyQt6.QtGui import QPainter, QPen, QFont, QPixmap
from PyQt6.QtCore import Qt, QPoint, QTimer
import os
from math import cos, sin, radians, degrees, atan2, sqrt

class DrawingArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setObjectName("drawing_area")
        self.configurations = {}
        self.current_configuration = None
        self.lines = []
        self.temp_line = None
        self.selected_line_index = None
        self.selected_point_index = None
        self.dragging = False
        self.resizing = False
        self.start_point = None
        self.data_name = None
        self.setMouseTracking(True)
        self.setup_layout()

    def setup_layout(self):
        main_layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.back_button = self.create_button(button_layout, "Guardar y Volver", "back_button")
        self.cancel_button = self.create_button(button_layout, "Volver sin guardar", "cancel_button")
        self.delete_button = self.create_button(button_layout, "Borrar última línea", "delete_button", self.delete_last_line)
        self.add_button = self.create_button(button_layout, "Agregar línea", "add_button", self.add_new_line)

        top_layout = QHBoxLayout()
        top_layout.addStretch()

        self.instructions_button = self.create_button(top_layout, "Instrucciones", "instructions_button", self.show_instructions)
        top_layout.addWidget(self.instructions_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(top_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(button_layout)
        main_layout.setContentsMargins(0, 0, 0, 20)

        self.setLayout(main_layout)

    def create_button(self, layout, text, obj_name, callback=None):
        button = QPushButton(text, self)
        button.setObjectName(obj_name)
        layout.addWidget(button)
        if callback:
            button.clicked.connect(callback)
        return button

    def connect_back_button(self, on_back_button_clicked_function):
        self.back_button.clicked.connect(on_back_button_clicked_function)

    def connect_cancel_button(self, on_cancel_button_clicked_function):
        self.cancel_button.clicked.connect(on_cancel_button_clicked_function)

    def set_current_configuration(self, config_number):
        self.current_configuration = config_number
        self.lines = self.load_lines_from_file(config_number)
        self.configurations[config_number] = self.lines
        self.update()

    def load_lines_from_file(self, config_number):
        if not self.data_name:
            return []

        filename = f"{self.data_name}.txt"
        if not os.path.exists(filename):
            return []

        lines = []
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) != 5:
                    continue
                config, x1, y1, x2, y2 = parts
                if int(config) == config_number:
                    p1 = QPoint(int(x1), int(y1))
                    p2 = QPoint(int(x2), int(y2))
                    lines.append(([p1, p2], Qt.GlobalColor.blue))
        return lines

    def save_lines_to_file(self):
        if self.current_configuration is None:
            return
        if not self.data_name:
            return
        filename = f"{self.data_name}.txt"
        with open(filename, 'w') as file:
            for config_number, lines in self.configurations.items():
                for line, color in lines:
                    file.write(f"{config_number},{line[0].x()},{line[0].y()},{line[1].x()},{line[1].y()}\n")

    def save_all_cases(self):
        if not self.data_name:
            return
        filename = f"{self.data_name}.txt"
        with open(filename, 'w') as file:
            for config_number in range(1, 8):
                lines = self.configurations.get(config_number, [])
                for line, color in lines:
                    file.write(f"{config_number},{line[0].x()},{line[0].y()},{line[1].x()},{line[1].y()}\n")

    def generate_parallel_lines(self):
        self.lines.clear()
        start_x, start_y, length, spacing = 100, 100, 200, 50
        for i in range(3):
            p1 = QPoint(start_x, start_y + i * spacing)
            p2 = QPoint(start_x + length, start_y + i * spacing)
            self.lines.append(([p1, p2], Qt.GlobalColor.blue))
        self.update()

    def mousePressEvent(self, event):
        if self.current_configuration is None:
            return
        pos = event.position().toPoint()

        if event.button() == Qt.MouseButton.LeftButton:
            self.handle_left_click(pos)
        elif event.button() == Qt.MouseButton.RightButton:
            self.handle_right_click(pos)

    def handle_left_click(self, pos):
        if self.selected_line_index is None:
            for i, (line, _) in enumerate(self.lines):
                if self.handle_line_or_point_selection(pos, line, i):
                    return
        else:
            self.dragging = True
            self.update()

    def handle_line_or_point_selection(self, pos, line, index):
        for j, point in enumerate(line):
            if self.is_point_near_point(pos, point):
                self.selected_line_index = index
                self.selected_point_index = j
                self.dragging = self.resizing = True
                self.start_point = pos
                self.update()
                return True
        if self.is_point_near_line(pos, line):
            self.selected_line_index = index
            self.dragging = True
            self.resizing = False
            self.start_point = pos
            self.update()
            return True
        return False

    def handle_right_click(self, pos):
        for i, (line, _) in enumerate(self.lines):
            if self.is_point_near_line(pos, line):
                self.selected_line_index = i
                self.show_rotation_dialog()
                return

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()

        if self.dragging and self.selected_line_index is not None:
            if self.resizing and self.selected_point_index is not None:
                self.resize_line(self.selected_line_index, self.selected_point_index, pos)
            else:
                delta = pos - self.start_point
                self.move_line(self.selected_line_index, delta)
                self.start_point = pos
            self.update()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            self.selected_line_index = self.selected_point_index = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.draw_background(painter)
        self.draw_grid(painter)
        self.draw_axes(painter)
        self.draw_lines(painter)

    def draw_background(self, painter):
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

    def draw_grid(self, painter):
        grid_size = self.width() // 10
        painter.setPen(QPen(Qt.GlobalColor.lightGray, 1))
        for x in range(0, self.width(), grid_size):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), grid_size):
            painter.drawLine(0, y, self.width(), y)

    def draw_axes(self, painter):
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        center_x, center_y = self.width() // 2, self.height() // 2
        painter.drawLine(0, center_y, self.width(), center_y)
        painter.drawLine(center_x, 0, center_x, self.height())
        self.draw_axis_labels(painter, center_x, center_y)

    def draw_axis_labels(self, painter, center_x, center_y):
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        grid_size = self.width() // 10
        for x in range(0, self.width(), grid_size):
            if (x - center_x) % grid_size == 0:
                painter.drawText(x, center_y + 15, str((x - center_x) // grid_size))
        for y in range(0, self.height(), grid_size):
            if (center_y - y) % grid_size == 0:
                painter.drawText(center_x + 5, y, str((center_y - y) // grid_size))

    def draw_lines(self, painter):
        if self.current_configuration is not None:
            lines = self.configurations.get(self.current_configuration, [])
            for i, (line, color) in enumerate(lines):
                pen = QPen(color if i != self.selected_line_index else Qt.GlobalColor.red, 3, Qt.PenStyle.DashLine if i == self.selected_line_index else Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.drawLine(line[0], line[1])
                self.draw_points(painter, line)

        if self.temp_line is not None:
            painter.setPen(QPen(Qt.GlobalColor.blue, 1, Qt.PenStyle.DashLine))
            painter.drawLine(self.temp_line[0], self.temp_line[1])

    def draw_points(self, painter, line):
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        for point in line:
            painter.setBrush(Qt.GlobalColor.red)
            painter.drawEllipse(point, 5, 5)

    def delete_last_line(self):
        if self.lines:
            self.lines.pop()
            self.update()

    def add_new_line(self):
        if len(self.lines) < 3:
            start_x, start_y, length = 100, 100 + len(self.lines) * 50, 200
            self.lines.append(([QPoint(start_x, start_y), QPoint(start_x + length, start_y)], Qt.GlobalColor.blue))
            self.update()

    def check_intersection(self, line1, line2):
        p1, q1 = line1
        p2, q2 = line2
        dx1, dy1 = q1.x() - p1.x(), q1.y() - p1.y()
        dx2, dy2 = q2.x() - p2.x(), q2.y() - p2.y()
        determinant = dx1 * dy2 - dy1 * dx2
        if determinant == 0:
            return False
        s = (-dy1 * (p1.x() - p2.x()) + dx1 * (p1.y() - p2.y())) / determinant
        t = (dx2 * (p1.y() - p2.y()) - dy2 * (p1.x() - p2.x())) / determinant
        return (0 <= s <= 1) and (0 <= t <= 1)

    def move_line(self, index, delta):
        line, color = self.lines[index]
        self.lines[index] = ([point + delta for point in line], color)

    def resize_line(self, index, point_index, new_pos):
        line, color = self.lines[index]
        line[point_index] = new_pos
        self.lines[index] = (line, color)

    def rotate_line(self, index, angle):
        line, color = self.lines[index]
        center = (line[0] + line[1]) / 2
        new_line = [self.rotate_point(line[0], center, angle), self.rotate_point(line[1], center, angle)]
        self.lines[index] = (new_line, color)

    def rotate_point(self, point, center, angle):
        angle = radians(angle)
        x, y = point.x() - center.x(), point.y() - center.y()
        new_x = x * cos(angle) - y * sin(angle) + center.x()
        new_y = x * sin(angle) + y * cos(angle) + center.y()
        return QPoint(int(new_x), int(new_y))

    def is_point_near_line(self, point, line, margin=5):
        p1, p2 = line
        line_length = sqrt((p2.x() - p1.x()) ** 2 + (p2.y() - p1.y()) ** 2)
        if line_length == 0:
            return False
        distance = abs((p2.y() - p1.y()) * point.x() - (p2.x() - p1.x()) * point.y() + p2.x() * p1.y() - p2.y() * p1.x()) / line_length
        return distance <= margin

    def is_point_near_point(self, p1, p2, margin=8):
        return (p1 - p2).manhattanLength() <= margin

    def calculate_angle(self, line):
        dx = line[1].x() - line[0].x()
        dy = line[1].y() - line[0].y()
        return degrees(atan2(dy, dx))

    def show_rotation_dialog(self):
        angle, ok = QInputDialog.getInt(self, "Rotar línea", "Ingrese grados °")
        if ok:
            self.rotate_line(self.selected_line_index, angle)
            self.update()

    def show_instructions(self):
        instructions = (
            'Haz clic en el botón "Agregar línea", para agregar las líneas, serán 3 líneas '
            'donde deberás representar el SEL de 3x2. Podrás moverlas desde los puntos color rojo. '
            'Si quieres indicar un movimiento en una cierta cantidad de grados, deberás apretar el '
            'botón secundario del mouse sobre la línea y ingresar los grados.'
        )
        QMessageBox.information(self, "Instrucciones de uso", instructions)
