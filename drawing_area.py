from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QInputDialog,
    QMessageBox,
)
from PyQt6.QtGui import QPainter, QPen, QFont, QPixmap
from PyQt6.QtCore import Qt, QPoint, QTimer
import os
import random  # Asegúrate de incluir esta línea
from math import cos, sin, radians, degrees, atan2, sqrt


class DrawingArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.random_points = {}  # Inicializa el diccionario para almacenar puntos aleatorios

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
        self.expected_vectors = {
            1: (3, 0, 0),  # Caso 1
            2: (2, 2, 0),  # Caso 2
            3: (2, 1, 1),  # Caso 3
            4: (2, 1, 0),  # Caso 4
            5: (0, 3, 1),  # Caso 5
            6: (1, 2, 0),  # Caso 6
            7: (0, 0, 1),  # Caso 7
        }

        self.setMouseTracking(True)
        self.setup_layout()

        # Generar las líneas paralelas al inicio
        self.generate_parallel_lines()

    def setup_layout(self):
        main_layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.back_button = self.create_button(
            button_layout, "Guardar y Volver", "back_button"
        )
        self.cancel_button = self.create_button(
            button_layout, "Volver sin guardar", "cancel_button"
        )
        self.delete_button = self.create_button(
            button_layout, "Borrar última línea", "delete_button", self.delete_last_line
        )
        self.add_button = self.create_button(
            button_layout, "Agregar línea", "add_button", self.add_new_line
        )
        self.data_button = self.create_button(
            button_layout, "Mostrar Datos", "data_button", self.show_lines_data
        )
        self.data_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007bff; /* Azul */
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3; /* Azul más oscuro al pasar el mouse */
            }
        """
        )

        self.describe_button = self.create_button(
            button_layout, "Describir Caso", "describe_button", self.describe_case
        )
        self.describe_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007bff; /* Azul */
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3; /* Azul más oscuro al pasar el mouse */
            }
        """
        )

        # Nuevo botón para mostrar los datos
        self.check_button = self.create_button(
            button_layout,
            "Verificar Respuestas",
            "check_button",
            self.check_case_answers,
        )
        self.check_button.setStyleSheet(
            """
            QPushButton {
                background-color: #ffc107; /* Amarillo */
                color: black;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0a800; /* Amarillo más oscuro al pasar el mouse */
            }
        """
        )

        self.equations_label = QLabel("Ecuaciones de las líneas:")
        self.equations_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.equations_label.setStyleSheet("font-size: 14px; margin: 10px;")
        main_layout.addWidget(self.equations_label)


        top_layout = QHBoxLayout()
        top_layout.addStretch()

        self.instructions_button = self.create_button(
            top_layout, "Instrucciones", "instructions_button", self.show_instructions
        )
        top_layout.addWidget(
            self.instructions_button, alignment=Qt.AlignmentFlag.AlignRight
        )

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
        self.lines = []  # Limpiar las líneas existentes
        self.generate_parallel_lines()  # Generar automáticamente tres líneas
        self.configurations[config_number] = self.lines
        self.update()

    def generate_parallel_lines(self):
        self.lines.clear()
        self.random_points.clear()  # Limpia los puntos aleatorios al cambiar de configuración
        start_x, start_y, length, spacing = 100, 100, 200, 50

        for i in range(3):
            p1 = QPoint(start_x, start_y + i * spacing)
            p2 = QPoint(start_x + length, start_y + i * spacing)
            self.lines.append(([p1, p2], Qt.GlobalColor.blue))
            # Genera y almacena puntos aleatorios para cada línea
            self.get_random_points_on_line((p1, p2), i)

        self.update()


    def calculate_slope(self, line):
        """Calcula la pendiente de una recta."""
        p1, p2 = line
        if p2.x() - p1.x() == 0:  # Evitar división por cero
            return None  # Recta vertical
        return round((p2.y() - p1.y()) / (p2.x() - p1.x()), 2)

    def get_random_points_on_line(self, line, line_index):
        # Verifica si los puntos para esta línea ya están generados
        if line_index in self.random_points:
            return self.random_points[line_index]
        
        # Si no están generados, los crea
        p1, p2 = line
        random_points = []
        for _ in range(2):  # Genera dos puntos aleatorios sobre la línea
            t = round(random.uniform(0, 1), 2)  # Genera un valor entre 0 y 1
            x = round(((1 - t) * p1.x() + t * p2.x()) / 100, 2)  # Normaliza a escala 100
            y = round(((1 - t) * p1.y() + t * p2.y()) / 100, 2)
            random_points.append((x, y))
        
        # Guarda los puntos generados para la línea actual
        self.random_points[line_index] = random_points
        return random_points


    def check_directions(self):
        """Verifica cuántas rectas tienen la misma pendiente (paralelas) y cuáles son coincidentes."""
        if len(self.lines) < 3:
            return {"paralelas": 0, "coincidentes": 0}

        pendientes = []
        for line, _ in self.lines:
            pendientes.append(self.calculate_slope(line))

        # Contar rectas con la misma pendiente (paralelismo)
        paralelas = sum(pendientes.count(p) > 1 for p in set(pendientes))

        # Verificar coincidencia (pendiente + mismos puntos)
        coincidentes = 0
        for i in range(len(self.lines)):
            for j in range(i + 1, len(self.lines)):
                if (
                    pendientes[i] == pendientes[j]
                    and self.lines[i][0] == self.lines[j][0]
                ):
                    coincidentes += 1

        return {"paralelas": paralelas, "coincidentes": coincidentes}

    def check_directions(self):
        """Verifica cuántas rectas tienen la misma pendiente (paralelas) y cuáles son coincidentes."""
        if len(self.lines) < 2:
            return {"paralelas": 0, "coincidentes": 0}

        pendientes = []
        for line, _ in self.lines:
            pendientes.append(self.calculate_slope(line))

        # Contar rectas paralelas
        paralelas = 0
        coincidentes = 0
        for i in range(len(pendientes)):
            for j in range(i + 1, len(pendientes)):
                if pendientes[i] == pendientes[j]:
                    # Verificar si también son coincidentes
                    if self.lines[i][0] == self.lines[j][0]:
                        coincidentes += 1
                    else:
                        paralelas += 1

        return {"paralelas": paralelas, "coincidentes": coincidentes}

    def calculate_intersection(self, line1, line2):
        """Calcula el punto de intersección entre dos líneas si existe."""
        p1, q1 = line1
        p2, q2 = line2

        # Convertir los puntos a coordenadas
        x1, y1 = p1.x(), p1.y()
        x2, y2 = q1.x(), q1.y()
        x3, y3 = p2.x(), p2.y()
        x4, y4 = q2.x(), q2.y()

        # Calcular el determinante
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if denominator == 0:  # Líneas paralelas o coincidentes
            return None

        # Calcular las coordenadas del punto de intersección
        px = (
            (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
        ) / denominator
        py = (
            (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
        ) / denominator

        # Verificar si el punto está dentro de los segmentos de línea
        if not (min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2)):
            return None
        if not (min(x3, x4) <= px <= max(x3, x4) and min(y3, y4) <= py <= max(y3, y4)):
            return None

        return QPoint(
            int(round(px)), int(round(py))
        )  # Convierte a enteros después de redondear

    def count_intersections(self):
        """Cuenta el número de intersecciones entre todas las líneas."""
        num_intersections = 0
        for i in range(len(self.lines)):
            for j in range(i + 1, len(self.lines)):
                if self.check_intersection(self.lines[i][0], self.lines[j][0]):
                    num_intersections += 1
        return num_intersections

    def check_intersection(self, line1, line2):
        """Comprueba si dos líneas se intersectan."""
        p1, q1 = line1
        p2, q2 = line2

        def orientation(p, q, r):
            """Calcula la orientación de tres puntos:
            0 -> Colineares
            1 -> Horario
            2 -> Antihorario
            """
            val = (q.y() - p.y()) * (r.x() - q.x()) - (q.x() - p.x()) * (r.y() - q.y())
            if val == 0:
                return 0
            return 1 if val > 0 else 2

        def on_segment(p, q, r):
            """Comprueba si el punto q está en el segmento pr."""
            return min(p.x(), r.x()) <= q.x() <= max(p.x(), r.x()) and min(
                p.y(), r.y()
            ) <= q.y() <= max(p.y(), r.y())

        # Encuentra las orientaciones necesarias para verificar la intersección
        o1 = orientation(p1, q1, p2)
        o2 = orientation(p1, q1, q2)
        o3 = orientation(p2, q2, p1)
        o4 = orientation(p2, q2, q1)

        # Condiciones generales
        if o1 != o2 and o3 != o4:
            return True

        # Casos especiales
        # p1, q1 y p2 son colineares y p2 está en el segmento p1q1
        if o1 == 0 and on_segment(p1, p2, q1):
            return True
        # p1, q1 y q2 son colineares y q2 está en el segmento p1q1
        if o2 == 0 and on_segment(p1, q2, q1):
            return True
        # p2, q2 y p1 son colineares y p1 está en el segmento p2q2
        if o3 == 0 and on_segment(p2, p1, q2):
            return True
        # p2, q2 y q1 son colineares y q1 está en el segmento p2q2
        if o4 == 0 and on_segment(p2, q1, q2):
            return True

        return False

    def check_directions(self):
        """Verifica cuántas rectas tienen la misma pendiente (paralelas) y cuáles son coincidentes."""
        if len(self.lines) < 2:
            return {"paralelas": 0, "coincidentes": 0}

        pendientes = []
        for line, _ in self.lines:
            pendientes.append(self.calculate_slope(line))

        # Contar rectas paralelas
        paralelas = 0
        coincidentes = 0
        for i in range(len(pendientes)):
            for j in range(i + 1, len(pendientes)):
                if pendientes[i] == pendientes[j]:  # Misma pendiente
                    # Verificar si los puntos también coinciden
                    if (
                        self.lines[i][0][0] == self.lines[j][0][0]
                        and self.lines[i][0][1] == self.lines[j][0][1]
                    ):
                        coincidentes += 1
                    else:
                        paralelas += 1

        return {"paralelas": paralelas, "coincidentes": coincidentes}

    def common_point_for_three_lines(self):
        """Verifica si hay un punto en común entre las tres rectas y devuelve un tuple."""
        if len(self.lines) < 3:
            return None

        intersection_12 = self.calculate_intersection(
            self.lines[0][0], self.lines[1][0]
        )
        intersection_13 = self.calculate_intersection(
            self.lines[0][0], self.lines[2][0]
        )

        if intersection_12 and intersection_12 == intersection_13:
            # Devuelve el punto común como un tuple con coordenadas divididas entre 100
            return (
                round(intersection_12.x() / 100, 2),
                round(intersection_12.y() / 100, 2),
            )
        return None

    def get_lines_data(self):
        """Devuelve un diccionario con datos de todas las rectas."""
        data = {}
        for i, (line, color) in enumerate(self.lines):
            slope = self.calculate_slope(line)
            random_points = self.get_random_points_on_line(line)
            intersections = []
            for j, (other_line, _) in enumerate(self.lines):
                if i != j and self.check_intersection(line, other_line):
                    intersections.append(j + 1)
            data[f"Recta {i + 1}"] = {
                "Pendiente": round(slope, 2) if slope is not None else "Vertical",
                "Puntos Aleatorios": [
                    (round(p.x()), round(p.y())) for p in random_points
                ],
                "Intersecciones": intersections,
            }
        return data

    def show_lines_data(self):
        """Muestra los datos de las rectas: pendientes, intersecciones y puntos en común."""
        message = "<b>Datos de las rectas:</b><br><br>"
        directions = self.check_directions()
        num_intersections = self.count_intersections()
        common_point = self.common_point_for_three_lines()

        for i, (line, _) in enumerate(self.lines):
            slope = (
                round(self.calculate_slope(line), 2)
                if self.calculate_slope(line) is not None
                else "Vertical"
            )
            random_points = self.get_random_points_on_line(line, i)  # Pasa el índice aquí
            message += f"<b>Recta {i + 1}:</b><br>"
            message += f"• <b>Pendiente:</b> {slope}<br>"
            message += f"• <b>Puntos Aleatorios:</b> {random_points}<br><br>"

        message += f"<b>Paralelas:</b> {directions['paralelas']}<br>"
        message += f"<b>Coincidentes:</b> {directions['coincidentes']}<br><br>"

        message += f"<b>Número de Intersecciones:</b> {num_intersections}<br>"
        if common_point:
            message += f"<b>Punto en común para las tres rectas:</b> ({common_point[0]}, {common_point[1]})<br>"
        else:
            message += "<b>No hay un punto común para las tres rectas.</b><br>"

        QMessageBox.information(self, "Datos de las Rectas", message)


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
                self.resize_line(
                    self.selected_line_index, self.selected_point_index, pos
                )
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
        self.draw_lines(painter)

    def draw_background(self, painter):
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

    def draw_lines(self, painter):
        if self.current_configuration is not None:
            lines = self.configurations.get(self.current_configuration, [])
            for i, (line, color) in enumerate(lines):
                # Configurar el estilo del lápiz para las líneas
                pen = QPen(
                    color if i != self.selected_line_index else Qt.GlobalColor.red,
                    3,
                    Qt.PenStyle.DashLine
                    if i == self.selected_line_index
                    else Qt.PenStyle.SolidLine,
                )
                painter.setPen(pen)
                painter.drawLine(line[0], line[1])
                
                # Dibujar puntos extremos de la línea
                self.draw_points(painter, line)

                # Calcular y dibujar la ecuación cerca de la línea
                p1, p2 = line
                if p2.x() - p1.x() != 0:  # Si no es una línea vertical
                    slope = (p2.y() - p1.y()) / (p2.x() - p1.x())
                    intercept = p1.y() - slope * p1.x()
                    equation = f"y = {slope:.2f}x + {intercept:.2f}"
                else:  # Línea vertical
                    equation = f"x = {p1.x()}"

                # Posicionar el texto cerca de la línea
                text_x = (p1.x() + p2.x()) // 2
                text_y = (p1.y() + p2.y()) // 2 - 10  # Elevar el texto un poco
                painter.setPen(QPen(Qt.GlobalColor.black, 1))
                painter.setFont(QFont("Arial", 10))
                painter.drawText(text_x, text_y, equation)

        if self.temp_line is not None:
            # Dibujar la línea temporal si existe
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
            self.lines.append(
                (
                    [QPoint(start_x, start_y), QPoint(start_x + length, start_y)],
                    Qt.GlobalColor.blue,
                )
            )
            self.update()
        else:
            QMessageBox.information(
                self, "Límite alcanzado", "Solo se permiten tres líneas en el dibujo."
            )
        self.update_equations()


    def show_instructions(self):
        instructions = (
            "Para interactuar con el área de dibujo:"
            "- Puedes mover las líneas desde los puntos rojos."
            "- Usa el botón derecho para rotar líneas."
            "- Se permiten hasta 3 líneas simultáneamente."
            "- Usa los botones para agregar o borrar líneas."
        )
        QMessageBox.information(self, "Instrucciones", instructions)

    def is_point_near_point(self, p1, p2, margin=8):
        return (p1 - p2).manhattanLength() <= margin

    def is_point_near_line(self, point, line, margin=5):
        p1, p2 = line
        line_length = sqrt((p2.x() - p1.x()) ** 2 + (p2.y() - p1.y()) ** 2)
        if line_length == 0:  # Evita dividir por cero si la línea es un punto
            return False
        distance = (
            abs(
                (p2.y() - p1.y()) * point.x()
                - (p2.x() - p1.x()) * point.y()
                + p2.x() * p1.y()
                - p2.y() * p1.x()
            )
            / line_length
        )
        return distance <= margin

    def move_line(self, index, delta):
        line, color = self.lines[index]
        self.lines[index] = ([point + delta for point in line], color)
        self.update_equations()


    def resize_line(self, index, point_index, new_pos):
        line, color = self.lines[index]
        line[point_index] = new_pos  # Actualiza la posición del extremo seleccionado
        self.lines[index] = (line, color)
        self.update_equations()


    def save_all_cases(self):
        if not self.data_name:
            QMessageBox.warning(
                self,
                "Advertencia",
                "No se especificó un nombre para guardar los datos.",
            )
            return
        filename = f"{self.data_name}.txt"
        with open(filename, "w") as file:
            for config_number, lines in self.configurations.items():
                for line, color in lines:
                    file.write(
                        f"{config_number},{line[0].x()},{line[0].y()},{line[1].x()},{line[1].y()}\n"
                    )

    def describe_case(self):
        """Recoge las respuestas de las preguntas base y las almacena."""
        questions = [
            "¿Cuántas rectas tienen la misma dirección?",
            "¿Cuántos puntos de intersección hay?",
            "¿Cuántos puntos en común a las tres rectas hay?",
        ]

        responses = []
        for question in questions:
            response, ok = QInputDialog.getInt(
                self, "Describir Caso", question, min=0, max=10
            )
            if not ok:
                QMessageBox.warning(
                    self, "Advertencia", "Debe responder todas las preguntas."
                )
                return  # Salir si el usuario cancela alguna pregunta
            responses.append(response)

        # Almacena las respuestas en el atributo 'answers'
        if not hasattr(self, "answers"):
            self.answers = {}
        self.answers[self.current_configuration] = {
            "RP1": responses[0],
            "RP2": responses[1],
            "RP3": responses[2],
        }

        print("Respuestas almacenadas:", self.answers)  # Depuración
        QMessageBox.information(
            self, "Descripción Guardada", "Las respuestas del caso han sido guardadas."
        )

    def check_case_answers(self):
        if (
            not hasattr(self, "answers")
            or self.current_configuration not in self.answers
        ):
            QMessageBox.warning(
                self, "Error", "No hay respuestas guardadas para este caso."
            )
            return

        user_answers = self.answers[self.current_configuration]
        expected = self.expected_vectors.get(self.current_configuration)

        if not expected:
            QMessageBox.warning(
                self, "Error", "No se ha configurado el vector esperado para este caso."
            )
            return

        is_correct = (
            user_answers["RP1"] == expected[0]
            and user_answers["RP2"] == expected[1]
            and user_answers["RP3"] == expected[2]
        )

        if is_correct:
            QMessageBox.information(self, "Correcto", "¡Las respuestas son correctas!")
        else:
            QMessageBox.warning(
                self,
                "Incorrecto",
                f"Las respuestas son incorrectas.\n"
                f"Vector esperado: {expected}\n"
                f"Tus respuestas: ({user_answers['RP1']}, {user_answers['RP2']}, {user_answers['RP3']})",
            )

    def save_lines_to_file(self):
        """Guarda todas las configuraciones y respuestas en un archivo."""
        if not self.data_name:
            QMessageBox.warning(self, "Advertencia", "No se especificó un nombre para guardar los datos.")
            return

        filename = f"{self.data_name}.txt"
        with open(filename, "w") as file:
            for config_number, lines in self.configurations.items():
                file.write(f"Caso {config_number}:\n")

                # Guardar líneas
                file.write("Lineas:\n")
                for i, (line, _) in enumerate(lines):
                    file.write(f"  ({line[0].x()}, {line[0].y()}) -> ({line[1].x()}, {line[1].y()})\n")
                    
                    # Guardar los puntos aleatorios asociados
                    if i in self.random_points:
                        random_points = self.random_points[i]
                        file.write(f"  Puntos Aleatorios: {random_points}\n")

                # Guardar respuestas asociadas al caso
                if hasattr(self, "answers") and config_number in self.answers:
                    rp = self.answers[config_number]
                    file.write(f"Respuestas: RP1={rp['RP1']}, RP2={rp['RP2']}, RP3={rp['RP3']}\n")

                file.write("\n")  # Espacio entre casos

        QMessageBox.information(self, "Guardado exitoso", f"Los datos se guardaron en '{filename}'.")



    def set_current_configuration(self, config_number):
        self.current_configuration = config_number
        self.lines = self.load_lines_from_file(config_number)  # Carga las líneas desde el archivo

        if not self.lines:  # Si no hay líneas, genera tres por defecto
            self.generate_parallel_lines()

        # Limpia los puntos aleatorios para la configuración actual
        self.random_points.clear()

        # Genera puntos aleatorios para las líneas cargadas
        for i, (line, _) in enumerate(self.lines):
            self.get_random_points_on_line(line, i)

        self.configurations[config_number] = self.lines
        self.update()


    def load_lines_from_file(self):
        if not self.data_name:
            return {}
        filename = f"{self.data_name}.txt"
        if not os.path.exists(filename):
            return {}
        configurations = {}
        with open(filename, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) != 5:
                    continue
                config, x1, y1, x2, y2 = parts
                config_number = int(config)
                p1 = QPoint(int(x1), int(y1))
                p2 = QPoint(int(x2), int(y2))
                if config_number not in configurations:
                    configurations[config_number] = []
                configurations[config_number].append(([p1, p2], Qt.GlobalColor.blue))
        return configurations

    def set_current_configuration(self, config_number):
        if (
            not self.configurations
        ):  # Carga las configuraciones desde el archivo solo una vez
            self.configurations = self.load_lines_from_file()
        self.current_configuration = config_number
        self.lines = self.configurations.get(
            config_number, []
        )  # Carga las líneas del caso actual
        if not self.lines:  # Si no hay líneas, genera tres por defecto
            self.generate_parallel_lines()
        self.configurations[config_number] = self.lines
        self.update()

    def show_rotation_dialog(self):
        if self.selected_line_index is None:
            QMessageBox.warning(
                self, "Advertencia", "No se ha seleccionado ninguna línea."
            )
            return
        angle, ok = QInputDialog.getInt(
            self,
            "Rotar línea",
            "Ingrese el ángulo de rotación (en grados):",
            min=-360,
            max=360,
        )
        if ok:
            self.rotate_line(self.selected_line_index, angle)
            self.update()

    def rotate_line(self, index, angle):
        line, color = self.lines[index]
        center = QPoint(
            (line[0].x() + line[1].x()) // 2, (line[0].y() + line[1].y()) // 2
        )
        new_line = [
            self.rotate_point(line[0], center, angle),
            self.rotate_point(line[1], center, angle),
        ]
        self.lines[index] = (new_line, color)
        self.update_equations()


    def rotate_point(self, point, center, angle):
        angle = radians(angle)
        x = point.x() - center.x()
        y = point.y() - center.y()
        new_x = x * cos(angle) - y * sin(angle) + center.x()
        new_y = x * sin(angle) + y * cos(angle) + center.y()
        return QPoint(int(new_x), int(new_y))

    def generate_parallel_lines(self):
        self.lines.clear()
        # Coordenadas ajustadas para que las líneas queden dentro del cuadro
        start_x = 100  # Dentro del rango del cuadro (1500 a 1800)
        start_y = 100  # Dentro del rango del cuadro (800 a 950)
        length = 200  # Ajustado para que las líneas no excedan el ancho del cuadro
        spacing = (
            50  # Espaciado entre líneas para que quepan dentro de la altura del cuadro
        )

        for i in range(3):
            p1 = QPoint(start_x, start_y + i * spacing)
            p2 = QPoint(start_x + length, start_y + i * spacing)
            self.lines.append(([p1, p2], Qt.GlobalColor.blue))
        self.update()
        self.update_equations()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.draw_background(painter)
        self.draw_lines(painter)
        self.draw_instruction_box(painter)

    def draw_instruction_box(self, painter):
        rect_x, rect_y, rect_width, rect_height = (
            55,
            30,
            300,
            200,
        )  # Coordenadas ajustadas para mover el cuadro
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(Qt.GlobalColor.transparent)  # Hacer el fondo transparente
        painter.drawRect(rect_x, rect_y, rect_width, rect_height)

        text = "Arrastra las líneas para que realices tu caso"
        painter.setFont(QFont("Arial", 10))
        painter.drawText(
            rect_x + 10,
            rect_y + 30,
            rect_width - 20,
            rect_height - 20,
            Qt.AlignmentFlag.AlignTop,
            text,
        )

    def update_equations(self):
        """Actualiza el QLabel con las ecuaciones de las líneas."""
        equations = []
        for i, (line, _) in enumerate(self.lines):
            p1, p2 = line
            if p2.x() - p1.x() == 0:
                # Línea vertical
                equation = f"Recta {i + 1}: x = {p1.x()}"
            else:
                slope = (p2.y() - p1.y()) / (p2.x() - p1.x())
                intercept = p1.y() - slope * p1.x()
                equation = f"Recta {i + 1}: y = {slope:.2f}x + {intercept:.2f}"
            equations.append(equation)

        # Depuración
        print("Ecuaciones actualizadas:", equations)

        self.equations_label.setText("Ecuaciones de las líneas:\n" + "\n".join(equations))

