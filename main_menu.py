from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class MainMenu(QWidget):
    def __init__(self, stacked_widget, drawing_area):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.drawing_area = drawing_area
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Etiqueta principal
        self.label = QLabel(
            "Muestra las 7 posibilidades que existen de representar un SEL de 3x2,\n"
            "utilizando tres líneas rectas de un plano.\n"
            "Seleccione una de las 7 configuraciones para dibujar 3 líneas con coeficientes configurables", self
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                padding: 20px;
                margin-bottom: 20px;
                qproperty-alignment: AlignCenter;
            }
        """)

        main_layout.addWidget(self.label)

        # Agregar imagen
        self.add_image(main_layout)

        # Crear botones
        self.create_buttons(main_layout)

    def add_image(self, layout):
        """Agrega una imagen entre el enunciado y los botones."""
        image_label = QLabel(self)
        pixmap = QPixmap("imagenes/imagen1.png")  # Asegúrate de que la imagen esté en esta ruta
        if not pixmap.isNull():
            # Escala la imagen a un tamaño más grande
            pixmap = pixmap.scaled(800, 400, Qt.AspectRatioMode.KeepAspectRatio)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(image_label)
        else:
            image_label.setText("No se pudo cargar la imagen.")
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(image_label)

    def create_buttons(self, layout):
        """Crea los botones de selección de caso."""
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.setVerticalSpacing(5)

        for i in range(1, 8):
            button = QPushButton(f"Caso {i}", self)
            button.clicked.connect(lambda checked, i=i: self.on_config_button_clicked(i))
            if i < 7:
                row = (i - 1) // 3
                col = (i - 1) % 3
                grid_layout.addWidget(button, row + 1, col)
            else:
                grid_layout.addWidget(button, 3, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(grid_layout)

    def on_config_button_clicked(self, config_number):
        self.drawing_area.set_current_configuration(config_number)
        self.stacked_widget.setCurrentIndex(2)
        self.stacked_widget.parent().start_emotion_detection()
