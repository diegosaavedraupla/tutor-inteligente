from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QInputDialog, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class InitialMenu(QWidget):
    def __init__(self, stacked_widget, main_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.main_widget = main_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Logo del programa
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap("path/to/logo.png"))  # Reemplaza con la ruta del logo
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        # Botón Iniciar
        self.start_button = QPushButton("Iniciar", self)
        self.start_button.clicked.connect(self.start)
        layout.addWidget(self.start_button)

    def start(self):
        text, ok = QInputDialog.getText(self, "Nombre del archivo", "Ingrese el RUT:")
        if ok and text:
            self.main_widget.data_name = text
            self.main_widget.save_all_cases()
            self.stacked_widget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Advertencia", "El RUT no puede estar vacío.")
