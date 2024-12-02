from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import QTimer
from drawing_area import DrawingArea
from main_menu import MainMenu
from initial_menu import InitialMenu
from emotion_detection import init_emotion_detection, start_emotion_detection, stop_emotion_detection, detect_emotion

class LineWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        self.drawing_area = DrawingArea(self)
        self.main_menu = MainMenu(self.stacked_widget, self.drawing_area)
        self.initial_menu = InitialMenu(self.stacked_widget, self.drawing_area)
        self.stacked_widget.addWidget(self.initial_menu)
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.drawing_area)
        self.setCentralWidget(self.stacked_widget)
        self.centralWidget().layout().setContentsMargins(0, 50, 0, 0)

        # Configuración del tamaño de la ventana principal
        self.resize(1600, 900)  # Ancho: 800 px, Alto: 600 px
        # self.setGeometry(100, 100, 800, 600)  # Alternativa: también configura posición (descomentar si lo necesitas)

        self.drawing_area.connect_back_button(self.on_back_button_clicked)
        self.drawing_area.connect_cancel_button(self.on_cancel_button_clicked)

        init_emotion_detection(self)

    def on_back_button_clicked(self):
        self.drawing_area.save_lines_to_file()
        self.stacked_widget.setCurrentIndex(1)
        stop_emotion_detection(self)

    def on_cancel_button_clicked(self):
        self.stacked_widget.setCurrentIndex(1)
        stop_emotion_detection(self)

    def start_emotion_detection(self):
        start_emotion_detection(self)

    def stop_emotion_detection(self):
        stop_emotion_detection(self)

    def detect_emotion(self):
        detect_emotion(self)

    def show_popup(self, emotion, stress=False, congratulation=False):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning if stress else QMessageBox.Icon.Information)
        if congratulation:
            msg.setText("¡Felicitaciones!")
            msg.setInformativeText("¡Sigue con el buen trabajo!")
            msg.setWindowTitle("Nivel de Estrés Bajo Detectado")
        else:
            msg.setText(f"Emoción detectada: {emotion}")
            msg.setInformativeText("Parece que estás estresado o distraído. ¿Te gustaría recibir ayuda?" if stress else "¡Sigue con el buen trabajo!")
            msg.setWindowTitle("Emoción Detectada")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg.exec()

    def closeEvent(self, event):
        self.cap.release()
        self.timer.stop()
        event.accept()
