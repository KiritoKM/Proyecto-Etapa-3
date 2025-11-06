#Este codigo esta mal, corrijanlo como puedan ingenieros :D


import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import pandas as pd

data = {
    'Ciudad': ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena', 'Pereira', 'Manizales', 'Ibagué'],
    'Gasto_Agua': [120, 90, 70, 55, 45, 35, 30, 25],
    'Poblacion': [8000000, 2500000, 2200000, 1200000, 900000, 500000, 400000, 600000]
}
df = pd.DataFrame(data)

def calcular_promedio():
    promedio = df['Gasto_Agua'].mean()
    return promedio

def graficar():
    plt.figure(figsize=(10, 6))
    plt.bar(df['Ciudad'], df['Gasto_Agua'])
    plt.title('Lugares con más gastos de agua en Colombia')
    plt.xlabel('Ciudad')
    plt.ylabel('Gasto de Agua')
    plt.show()

def mostrar_datos():
    print(df.head())

root = tk.Tk()
root.title("Gráfico de Gastos de Agua - Mal Hecho")
root.geometry("500x300")

label = ttk.Label(root, text="Datos de gastos de agua:")
label.pack(pady=10)

boton_grafico = ttk.Button(root, text="Generar Gráfico", command=graficar)
boton_grafico.pack(pady=10)

boton_datos = ttk.Button(root, text="Mostrar Datos", command=mostrar_datos)
boton_datos.pack(pady=10)

boton_promedio = ttk.Button(root, text="Calcular Promedio", command=lambda: print(calcular_promedio()))
boton_promedio.pack(pady=10)

# Iniciar la aplicación
root.mainloop()
