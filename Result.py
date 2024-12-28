import tkinter as tk
from tkinter import ttk
import json

# Archivo donde se almacenarán los datos
DATA_FILE = "simulation_data.json"

class VisualizationWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation Events Data")

        # Configurar el tamaño inicial de la ventana
        self.root.geometry("800x600")  # Ancho x Alto

        # Crear un estilo para mejorar la apariencia
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14))  # Fuente de los datos
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))  # Fuente de los encabezados

        # Tabla para mostrar los datos
        self.tree = ttk.Treeview(root, columns=("Description", "Value"), show="headings", height=20)
        self.tree.heading("Description", text="Description")
        self.tree.heading("Value", text="Value")
        self.tree.column("Description", anchor="center", width=400)  # Ancho de la columna
        self.tree.column("Value", anchor="center", width=300)
        self.tree.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Botón para cerrar la ventana
        self.close_button = ttk.Button(root, text="Close", command=root.destroy, style="TButton")
        self.close_button.grid(row=1, column=0, padx=20, pady=10)

        # Configurar filas y columnas para expandirse
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Iniciar la actualización de datos
        self.update_data()

    def update_data(self):
        try:
            # Leer los datos desde el archivo JSON
            with open(DATA_FILE, "r") as file:
                data = json.load(file)

            # Limpiar la tabla
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Llenar la tabla con los datos actuales
            for row in data:
                self.tree.insert("", "end", values=row)

        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Ignorar errores iniciales si el archivo no está listo aún

        # Actualizar los datos cada 500 ms
        self.root.after(500, self.update_data)

# Crear la ventana
def main():
    root = tk.Tk()
    app = VisualizationWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
