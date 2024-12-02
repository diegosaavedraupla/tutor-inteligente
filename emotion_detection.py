from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox
from deepface import DeepFace
import cv2
import time
from collections import deque
import numpy as np

# Definimos la longitud del intervalo en segundos para calcular el promedio de emociones
INTERVAL_LENGTH = 30  # 30 segundos
# Definimos el umbral para mostrar un mensaje de estrés o distracción
STRESS_THRESHOLD = 0.6  # Umbral de estrés
DISTRACTION_THRESHOLD = 0.4  # Umbral de distracción
# Definimos el tiempo mínimo entre mensajes de felicitaciones y de distracción
CONGRATULATION_INTERVAL = 600  # 10 minutos
DISTRACTION_INTERVAL = 300  # 5 minutos

def init_emotion_detection(widget):
    widget.timer = QTimer()
    widget.timer.timeout.connect(lambda: detect_emotion(widget))
    widget.cap = cv2.VideoCapture(0)
    if not widget.cap.isOpened():
        QMessageBox.critical(widget, "Error de Cámara", "No se puede abrir la cámara.")
        return
    widget.last_emotion_time = time.time()
    widget.last_congratulation_time = time.time() - CONGRATULATION_INTERVAL  # Para permitir un mensaje inicial si es necesario
    widget.last_distraction_time = time.time() - DISTRACTION_INTERVAL  # Para permitir un mensaje inicial si es necesario
    widget.emotion_queue = deque(maxlen=20)  # Almacenamos más emociones para análisis temporal
    widget.emotion_interval_queue = deque()  # Almacenamos emociones para promedios por intervalos

def start_emotion_detection(widget):
    widget.timer.start(2000)

def stop_emotion_detection(widget):
    widget.timer.stop()

def detect_emotion(widget):
    ret, frame = widget.cap.read()
    if ret:
        try:
            result = DeepFace.analyze(frame, actions=['emotion'])
            if isinstance(result, list):
                result = result[0]
            emotion = result.get('dominant_emotion', None)
            print(f"Emoción detectada: {emotion}")

            widget.emotion_queue.append(emotion)
            widget.emotion_interval_queue.append((time.time(), emotion))
            clean_old_emotions(widget.emotion_interval_queue)

            if len(widget.emotion_queue) == widget.emotion_queue.maxlen:
                stress_level = calculate_stress_level(widget.emotion_queue)
                print(f"Nivel de estrés calculado: {stress_level}")

                current_time = time.time()
                interval_stress_level = calculate_interval_stress_level(widget.emotion_interval_queue)
                
                # Notificación de estrés alto
                if interval_stress_level > STRESS_THRESHOLD and current_time - widget.last_emotion_time > INTERVAL_LENGTH:
                    widget.show_popup("Alto Estrés", True)
                    widget.last_emotion_time = current_time
                
                # Notificación de distracción o estrés moderado
                elif interval_stress_level > DISTRACTION_THRESHOLD and current_time - widget.last_distraction_time > DISTRACTION_INTERVAL:
                    widget.show_popup("Distracción o Estrés Moderado", False)
                    widget.last_distraction_time = current_time
                
                # Notificación de bajo estrés
                elif interval_stress_level <= DISTRACTION_THRESHOLD and current_time - widget.last_congratulation_time > CONGRATULATION_INTERVAL:
                    widget.show_popup("Bajo Estrés", False, congratulation=True)
                    widget.last_congratulation_time = current_time
        except Exception as e:
            print(f"Error al detectar emoción: {e}")
    else:
        print("Error al leer el frame de la cámara.")

def calculate_stress_level(emotion_queue):
    emotion_scores = {'happy': -1, 'sad': 1, 'fear': 1, 'angry': 1, 'neutral': 0, 'surprise': 0.5, 'disgust': 0.5}
    scores = [emotion_scores.get(emotion, 0) for emotion in emotion_queue]
    stress_level = np.mean(scores)
    return (stress_level + 1) / 2  # Normalizamos a un rango de 0 a 1

def calculate_interval_stress_level(emotion_interval_queue):
    emotion_scores = {'happy': -1, 'sad': 1, 'fear': 1, 'angry': 1, 'neutral': 0, 'surprise': 0.5, 'disgust': 0.5}
    scores = [emotion_scores.get(emotion, 0) for _, emotion in emotion_interval_queue]
    stress_level = np.mean(scores)
    return (stress_level + 1) / 2  # Normalizamos a un rango de 0 a 1

def clean_old_emotions(emotion_interval_queue):
    current_time = time.time()
    while emotion_interval_queue and current_time - emotion_interval_queue[0][0] > INTERVAL_LENGTH:
        emotion_interval_queue.popleft()

def show_popup(widget, emotion, stress=False, congratulation=False):
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
