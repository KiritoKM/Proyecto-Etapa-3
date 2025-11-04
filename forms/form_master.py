import tkinter as tk
from tkinter.font import BOLD
import util.generic as utl


class masterpanel:
    def __init__(self, current_user=None, logo_url=None):
        """Panel principal.

        Args:
            current_user: objeto usuario (puede tener atributo .role con 'admin'/'user').
            logo_url: URL o ruta local de la imagen de fondo/logo (opcional).
        """
        self.current_user = current_user
        self.ventana = tk.Tk()
        self.ventana.title("Master Panel")
        w, h = self.ventana.winfo_screenwidth(), self.ventana.winfo_screenheight()
        self.ventana.geometry("%dx%d+0+0" % (w, h))
        self.ventana.config(bg="#fcfcfc")
        self.ventana.resizable(width=0, height=0)

        # Cargar logo (puede venir de URL pública)
        url = logo_url or "https://i.ibb.co/LDmvxzzT/Gemini-Generated-Image-tvjs5ltvjs5ltvjs.png"
        self.logo = utl.leer_imagen(url, (500, 500))

        if self.logo:
            bg_label = tk.Label(self.ventana, image=self.logo, bg="#3a7ff6")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.lower()
            bg_label.image = self.logo
        else:
            # fallback de color si no hay imagen
            self.ventana.config(bg="#3a7ff6")

        # Contenedor para widgets encima del fondo
        content = tk.Frame(self.ventana, bg="", padx=10, pady=10)
        content.place(relx=0.5, rely=0.05, anchor="n")

        # Botones visibles siempre
        btn_agregar = tk.Button(content, text="Agregar", width=12, command=self.on_agregar)
        btn_mostrar = tk.Button(content, text="Refrescar", width=12, command=self.on_mostrar)
        btn_salir = tk.Button(content, text="Salir", width=12, command=self.ventana.destroy)
        btn_agregar.grid(row=0, column=0, padx=6, pady=6)
        btn_mostrar.grid(row=0, column=1, padx=6, pady=6)
        btn_salir.grid(row=0, column=2, padx=6, pady=6)

        # Botones administrativos (solo para admin)
        is_admin = getattr(self.current_user, "role", None) == "admin"
        self.btn_eliminar = tk.Button(content, text="Eliminar", width=12, command=self.on_eliminar)
        self.btn_actualizar = tk.Button(content, text="Actualizar", width=12, command=self.on_actualizar)
        self.btn_eliminar.grid(row=1, column=0, padx=6, pady=6)
        self.btn_actualizar.grid(row=1, column=1, padx=6, pady=6)

        if not is_admin:
            self.btn_eliminar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")

        self.ventana.mainloop()

    # Callbacks de ejemplo — reemplaza con tu lógica real
    def on_agregar(self):
        print("Agregar pulsado")

    def on_mostrar(self):
        print("Refrescar pulsado")

    def on_eliminar(self):
        print("Eliminar pulsado")

    def on_actualizar(self):
        print("Actualizar pulsado")

