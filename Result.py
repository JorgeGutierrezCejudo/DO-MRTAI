import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json

DATA_FILE = "simulation_data.json"

class VisualizationWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation Events Data")
        self.root.geometry("900x600")  # Width x Height
        
        # Crear un estilo mas neutral
        style = ttk.Style()
        style.theme_use("clam")  # Usar un tema moderno
        style.configure("Treeview",
                        font=("Roboto", 12),
                        background="#f9f9f9",
                        foreground="#333",
                        rowheight=30,
                        fieldbackground="#f9f9f9")
        style.configure("Treeview.Heading",
                        font=("Roboto", 14, "bold"),
                        background="#cccccc",
                        foreground="black")
        style.map("Treeview", background=[("selected", "#cccccc")], foreground=[("selected", "black")])

        # Encabezado con logos
        header_frame = tk.Frame(root, bg="white")
        header_frame.pack(fill=tk.X)

        # Logo 1
        logo1_image = Image.open("URJC-Logo.png")
        logo1_image = logo1_image.resize((192, 108), Image.ANTIALIAS)
        logo1_photo = ImageTk.PhotoImage(logo1_image)
        logo1_label = tk.Label(header_frame, image=logo1_photo, bg="white")
        logo1_label.image = logo1_photo
        logo1_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Titulo
        title_label = tk.Label(header_frame, text="Simulation Events", font=("Roboto", 20, "bold"), bg="white", fg="black")
        title_label.pack(side=tk.LEFT, expand=True, padx=10)

        # Logo 2
        logo2_image = Image.open("Logo-Universita-Roma-Tor-Vergata.png")
        logo2_image = logo2_image.resize((192, 50), Image.ANTIALIAS)
        logo2_photo = ImageTk.PhotoImage(logo2_image)
        logo2_label = tk.Label(header_frame, image=logo2_photo, bg="white")
        logo2_label.image = logo2_photo
        logo2_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Crear un marco para la tabla
        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Tabla para mostrar los datos
        self.tree = ttk.Treeview(frame, columns=("Description", "Value"), show="headings")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Value", text="Value")
        self.tree.column("Description", anchor="center", width=450)
        self.tree.column("Value", anchor="center", width=300)

        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.close_button = ttk.Button(root, text="Close", command=root.destroy, style="TButton")
        self.close_button.pack(pady=10)

        style.configure("TButton",
                        font=("Roboto", 12, "bold"),
                        background="#b3b3b3",
                        foreground="black",
                        padding=10)
        style.map("TButton",
                   background=[("active", "#999999")])

        # Actualizar datos en la tabla
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
            pass  

        # Actualizar los datos cada 500 ms
        self.root.after(500, self.update_data)

# Crear la ventana
def main():
    root = tk.Tk()
    app = VisualizationWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
