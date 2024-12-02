import sys
from PyQt6.QtWidgets import QApplication
from line_widget import LineWidget

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        MainMenu QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 14px;
        }
        MainMenu QPushButton:hover {
            background-color: #0056b3;
        }

        #drawing_area #back_button, #drawing_area #delete_button, #drawing_area #cancel_button, #drawing_area #add_button, #drawing_area #instructions_button {
            background-color: #ff0000;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 14px;
        }
        #drawing_area #back_button:hover, #drawing_area #delete_button:hover, #drawing_area #cancel_button:hover, #drawing_area #add_button:hover, #drawing_area #instructions_button:hover {
            background-color: #cc0000;
        }
    """)

    window = LineWidget()
    window.setWindowTitle("Dibujo de Líneas y Detección de Emociones")
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
