import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json


class TutorInteligente:
    def __init__(self, root):
        self.root = root
        self.root.title("Tutor Inteligente - Álgebra Lineal")
        self.root.geometry("1000x700")

        # Espacio gráfico
        self.canvas_frame = tk.Frame(root, bg="white")
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Matplotlib (sin ejes coordenados)
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.axis("off")  # Desactivar ejes
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Botones
        self.add_line_button = tk.Button(root, text="Agregar Recta", command=self.agregar_recta)
        self.add_line_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.describe_case_button = tk.Button(root, text="Describir Caso", command=self.describir_caso)
        self.describe_case_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.evaluate_button = tk.Button(root, text="Evaluar Configuración", command=self.evaluar_configuracion)
        self.evaluate_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.save_config_button = tk.Button(root, text="Guardar Configuración", command=self.guardar_configuracion)
        self.save_config_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Variables de interacción
        self.rectas = []  # Lista de rectas
        self.selected_line = None  # Recta seleccionada
        self.previous_mouse_position = None

        # Eventos del mouse
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("motion_notify_event", self.on_drag)
        self.canvas.mpl_connect("button_release_event", self.on_release)

    def agregar_recta(self):
        # Solicitar pendiente e intercepto
        pendiente_str = simpledialog.askstring("Ingrese Pendiente", "Pendiente (m):", parent=self.root)
        intercepto_str = simpledialog.askstring("Ingrese Intercepto", "Intercepto (b):", parent=self.root)

        if pendiente_str is None or intercepto_str is None:
            return  # Cancelar si el usuario no introduce datos

        try:
            pendiente = float(pendiente_str)
            intercepto = float(intercepto_str)
        except ValueError:
            messagebox.showerror("Error", "Debe ingresar valores numéricos válidos.")
            return

        # Dibujar recta
        x = [-10, 10]
        y = [pendiente * xi + intercepto for xi in x]
        line, = self.ax.plot(x, y, label=f"y={pendiente}x+{intercepto}", picker=True, linewidth=2)

        # Guardar la recta
        self.rectas.append({"line": line, "pendiente": pendiente, "intercepto": intercepto})
        self.ax.legend()
        self.canvas.draw()

    def describir_caso(self):
        if not self.rectas:
            messagebox.showinfo("Información", "No hay rectas para describir.")
            return

        descripcion = []
        for i, recta in enumerate(self.rectas, start=1):
            pendiente = recta["pendiente"]
            intercepto = recta["intercepto"]
            descripcion.append(f"Recta {i}: y = {pendiente}x + {intercepto}")
        descripcion.append("\nPreguntas:")
        descripcion.append("1. ¿Cuántas rectas tienen la misma dirección?")
        descripcion.append("2. ¿Cuántos puntos de intersección hay?")
        descripcion.append("3. ¿Cuántos puntos en común tienen las rectas?")

        messagebox.showinfo("Descripción del Caso", "\n".join(descripcion))

    def evaluar_configuracion(self):
        if len(self.rectas) < 2:
            messagebox.showinfo("Evaluación", "Se necesitan al menos 2 rectas.")
            return

        pendientes = [recta["pendiente"] for recta in self.rectas]
        intersecciones = self.calcular_intersecciones()

        if len(set(pendientes)) == 1:
            paralelismo = "Todas las rectas son paralelas."
        else:
            paralelismo = "Las rectas no son todas paralelas."

        # Mostrar resultados
        messagebox.showinfo("Evaluación", f"{paralelismo}\nIntersecciones encontradas: {len(intersecciones)}")
        for inter in intersecciones:
            self.ax.plot(*inter, "ro")  # Mostrar intersecciones en rojo
        self.canvas.draw()

    def calcular_intersecciones(self):
        # Calcula los puntos de intersección entre rectas
        intersecciones = []
        for i in range(len(self.rectas)):
            for j in range(i + 1, len(self.rectas)):
                m1, b1 = self.rectas[i]["pendiente"], self.rectas[i]["intercepto"]
                m2, b2 = self.rectas[j]["pendiente"], self.rectas[j]["intercepto"]
                if m1 != m2:  # Si no son paralelas
                    x_inter = (b2 - b1) / (m1 - m2)
                    y_inter = m1 * x_inter + b1
                    intersecciones.append((x_inter, y_inter))
        return intersecciones

    def guardar_configuracion(self):
        # Guardar las rectas y sus propiedades en un archivo JSON
        data = [{"pendiente": r["pendiente"], "intercepto": r["intercepto"]} for r in self.rectas]
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])

        if file_path:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
            messagebox.showinfo("Éxito", f"Configuración guardada en {file_path}")

    def on_click(self, event):
        # Seleccionar una recta cercana al clic
        if event.inaxes != self.ax:
            return

        for recta in self.rectas:
            line = recta["line"]
            contains, _ = line.contains(event)
            if contains:
                self.selected_line = recta
                self.previous_mouse_position = (event.xdata, event.ydata)
                break

    def on_drag(self, event):
        if self.selected_line is None or event.xdata is None or event.ydata is None:
            return

        # Calcular el desplazamiento del mouse
        dx = event.xdata - self.previous_mouse_position[0]
        dy = event.ydata - self.previous_mouse_position[1]

        # Actualizar pendiente e intercepto
        self.selected_line["intercepto"] += dy
        self.selected_line["pendiente"] += dx * 0.1  # Modificar pendiente al mover horizontalmente

        # Actualizar la recta gráficamente
        m = self.selected_line["pendiente"]
        b = self.selected_line["intercepto"]
        x = [-10, 10]
        y = [m * xi + b for xi in x]
        self.selected_line["line"].set_data(x, y)

        self.previous_mouse_position = (event.xdata, event.ydata)
        self.canvas.draw()

    def on_release(self, event):
        self.selected_line = None
        self.previous_mouse_position = None


# Iniciar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = TutorInteligente(root)
    root.mainloop()
