import tkinter as tk 
from tkinter import ttk, messagebox
import util.generic as utl
from forms.form_master import masterpanel
from tkinter import Button
from auth_roles import authenticate, User

class loginform:
    
    def verificar_credenciales(self):
        usuario = self.usuario_entry.get()
        contrasena = self.contrasena_entry.get()
        user = authenticate(usuario, contrasena)
        if user is not None:
            messagebox.showinfo("Éxito", f"Inicio de sesión exitoso ({user.username})")
            self.user_authenticated = True
            self.current_user = user
            self.ventana.destroy()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")


    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Inicio de Sesion")
        self.ventana.geometry("800x500")
        self.ventana.config(bg="#e9e9e9")
        self.ventana.resizable(width=0, height=0)
        utl.centrar_ventana(self.ventana, 800, 500)

        logo = utl.leer_imagen("https://i.ibb.co/LDmvxzzT/Gemini-Generated-Image-tvjs5ltvjs5ltvjs.png", (500, 500))

        frame_logo = tk.Frame(self.ventana, bd=0, width=300,
                              relief=tk.SOLID, padx=10, pady=10, bg='#3a7ff6')
        frame_logo.pack(side="left", expand=tk.YES, fill=tk.BOTH)
        label = tk.Label(frame_logo, image=logo, bg='#3a7ff6')
        label.place(x=0, y=0, relwidth=1, relheight=1)

        # frame_form
        frame_form = tk.Frame(self.ventana, bd=0,
                              relief=tk.SOLID, bg='#fcfcfc')
        frame_form.pack(side="right", expand=tk.YES, fill=tk.BOTH)
        # frame_form

        # frame_form_top
        frame_form_top = tk.Frame(
            frame_form, height=50, bd=0, relief=tk.SOLID, bg='black')
        frame_form_top.pack(side="top", fill=tk.X)
        title = tk.Label(frame_form_top, text="Inicio de sesion", font=(
            'Times', 30), fg="#666a88", bg='#fcfcfc', pady=50)
        title.pack(expand=tk.YES, fill=tk.BOTH)
        # end frame_form_top

        # frame_form_fill
        frame_form_fill = tk.Frame(
            frame_form, height=50,  bd=0, relief=tk.SOLID, bg='#fcfcfc')
        frame_form_fill.pack(side="bottom", expand=tk.YES, fill=tk.BOTH)

        etiqueta_usuario = tk.Label(frame_form_fill, text="Usuario", font=(
            'Times', 14), fg="#666a88", bg='#fcfcfc', anchor="w")
        etiqueta_usuario.pack(fill=tk.X, padx=20, pady=5)
        self.usuario_entry = ttk.Entry(frame_form_fill, font=('Times', 14))
        self.usuario_entry.pack(fill=tk.X, padx=20, pady=10)

        etiqueta_password = tk.Label(frame_form_fill, text="Contraseña", font=(
            'Times', 14), fg="#666a88", bg='#fcfcfc', anchor="w")
        etiqueta_password.pack(fill=tk.X, padx=20, pady=5)
        self.contrasena_entry = ttk.Entry(
            frame_form_fill, font=('Times', 14))
        self.contrasena_entry.pack(fill=tk.X, padx=20, pady=10)
        self.contrasena_entry.config(show="*")


        inicio = tk.Button(frame_form_fill, text="Iniciar sesion", font=(
            'Times', 15), bg='#3a7ff6', bd=0, fg="#fff", command=self.verificar_credenciales)
        inicio.pack(fill=tk.X, padx=20, pady=20)        
        inicio.bind("<Return>", (lambda event: self.verificar_credenciales()))
        # end frame_form_fill
        salir = tk.Button(frame_form_fill, text="Salir", font=(
            'Times', 15), bg='#ff3a3a', bd=0, fg="#fff", command=self.ventana.destroy)
        salir.pack(fill=tk.X, padx=20, pady=10)
        salir.bind("<Return>", (lambda event: self.ventana.destroy()))
        


        self.ventana.mainloop()


# Si quieres probarlo directamente:
# loginform()