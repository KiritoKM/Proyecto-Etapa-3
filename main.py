#Proyecto3.py

import random
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import pandas as pd
import calendar
import logging 
from datetime import datetime
import faker as fk
import pickle
import util.generic as utl

# Configurar logging con archivo
log_filename = f"inventario_log_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Estilos ANSI (compatibilidad consola)
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m' 
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

faker = fk.Faker()



from forms.form_login import loginform
# Mostrar el formulario de login y obtener la instancia
login = loginform()
if getattr(login, 'user_authenticated', False):
  current_user = login.current_user
  logger.info(f"Usuario autenticado: {current_user.username if hasattr(current_user, 'username') else 'Usuario'} - Rol: {getattr(current_user, 'role', 'N/A')}")
else:
  logger.warning("Autenticación fallida - Cerrando aplicación")
  exit(0)




class Producto:
  def __init__(self, nombre, precio_compra, precio_venta, cantidad, sku, proveedor):
    self.nombre = nombre.capitalize()
    self.precio_compra = float(precio_compra)
    self.precio_venta = float(precio_venta)
    self.cantidad = int(cantidad)
    self.sku = int(sku)
    self.proveedor = proveedor.capitalize()
    logger.info(f"Producto creado: {self.nombre} (SKU: {self.sku}) - Precio venta: ${int(self.precio_venta)} - Cantidad: {self.cantidad}")

  def actualizar_stock(self, nueva_cantidad):
    antigua_cantidad = self.cantidad
    self.cantidad = int(nueva_cantidad)
    logger.info(f"Stock actualizado para {self.nombre} (SKU: {self.sku}): {antigua_cantidad} -> {self.cantidad}")

  def actualizar_precio(self, nuevo_precioV):
    precio_anterior = self.precio_venta
    self.precio_venta = float(nuevo_precioV)
    logger.info(f"Precio actualizado para {self.nombre} (SKU: {self.sku}): ${int(precio_anterior)} -> ${int(self.precio_venta)}")

  def verificar_stock_bajo(self):
    return self.cantidad < 10

  def obtener_info(self):
    return (
      f"Nombre: {self.nombre} || Precio: ${int(self.precio_venta)} || "
      f"Cantidad: {self.cantidad} || Codigo: {self.sku} || Proveedor: {self.proveedor}"
    )


class inventario:
  def __init__(self):
    self.productos = []
    self.df = pd.DataFrame(columns=[
      'Nombre', 'PrecioCompra', 'PrecioVenta', 'Cantidad', 'SKU', 'Proveedor'
    ])

  def sincronizar_data(self):
    rows = [
      {
        'Nombre': p.nombre,
        'PrecioCompra': p.precio_compra,
        'PrecioVenta': p.precio_venta,
        'Cantidad': p.cantidad,
        'SKU': p.sku,
        'Proveedor': p.proveedor
      }
      for p in self.productos
    ]
    self.df = pd.DataFrame(rows, columns=[
      'Nombre', 'PrecioCompra', 'PrecioVenta', 'Cantidad', 'SKU', 'Proveedor'
    ])
  
  def guardar_inventario(self):
    """Guarda el inventario en un archivo pickle"""
    try:
      with open("inventario_data.pkl", "wb") as f:
        pickle.dump(self.productos, f)
      logger.debug("Inventario guardado en archivo pickle")
    except Exception as e:
      logger.error(f"Error al guardar inventario: {str(e)}")

  def get_dataframe(self):
    return self.df.copy()



  # --- Funciones en Tkinter---
  def agregar_producto_manual(self, nombre, precio_compra, precio_venta, cantidad, proveedor):
    nombre = str(nombre).strip().capitalize()
    proveedor = str(proveedor).strip().capitalize()
    if not nombre:
      raise ValueError("El nombre del producto no puede estar vacío.")
    if any(producto.nombre == nombre for producto in self.productos):
      raise ValueError(f"Ya existe un producto con el nombre '{nombre}'.")
    try:
      precio_compra = float(precio_compra)
      precio_venta = float(precio_venta)
    except:
      raise ValueError("El precio debe ser un número válido.")
    if precio_compra <= 0 or precio_venta <= 0:
      raise ValueError("El precio debe ser mayor que cero.")
    try:
      cantidad = int(cantidad)
    except:
      raise ValueError("La cantidad debe ser un número entero.")
    if cantidad <= 0:
      raise ValueError("La cantidad debe ser mayor que cero.")
    if not proveedor:
      raise ValueError("El proveedor del producto no puede estar vacío.")
    sku = random.randint(100000, 999999)
    while any(producto.sku == sku for producto in self.productos):
      sku = random.randint(100000, 999999)
    producto = Producto(nombre, precio_compra, precio_venta, cantidad, sku, proveedor)
    self.productos.append(producto)
    self.sincronizar_data()
    self.guardar_inventario()
    logger.info(f"Producto agregado al inventario: {producto.nombre} (SKU: {producto.sku}) - Total productos: {len(self.productos)}")
    return producto

  def buscar_producto_por_sku(self, sku):
    try:
      sku = int(sku)
    except:
      logger.warning(f"SKU inválido en búsqueda: {sku}")
      return None
    for producto in self.productos:
      if producto.sku == sku:
        logger.info(f"Producto encontrado por SKU: {sku} - {producto.nombre}")
        return producto
    logger.info(f"Producto no encontrado por SKU: {sku}")
    return None

  def buscar_producto_por_nombre(self, nombre):
    nombre = str(nombre).strip().capitalize()
    for producto in self.productos:
      if producto.nombre == nombre:
        logger.debug(f"Producto encontrado por nombre: {nombre} (SKU: {producto.sku})")
        return producto
    logger.debug(f"Producto no encontrado por nombre: {nombre}")
    return None


  def obtener_productos_stock_bajo(self):
    return [producto for producto in self.productos if producto.verificar_stock_bajo()]

  def calcular_valor_total_recursivo(self, idx=0):
    """Calcula el valor total del inventario de forma recursiva.

    Args:
        idx (int): índice actual; llamada inicial sin argumentos.

    Returns:
        float: valor total (suma precio_venta * cantidad)
    """
    if idx >= len(self.productos):
      return 0.0
    p = self.productos[idx]
    return (p.precio_venta * p.cantidad) + self.calcular_valor_total_recursivo(idx + 1)

  def eliminar_producto(self, nombre):
    nombre = str(nombre).strip().capitalize()
    if nombre not in [producto.nombre for producto in self.productos]:
      logger.warning(f"Intento de eliminar producto no encontrado: {nombre}")
      raise ValueError(f"No se encontró un producto con el nombre '{nombre}' en el inventario.")
    for producto in list(self.productos):
      if producto.nombre == nombre:
        self.productos.remove(producto)
        self.sincronizar_data()
        self.guardar_inventario()
        logger.info(f"Producto eliminado: {nombre} (SKU: {producto.sku}) - Total productos: {len(self.productos)}")
        return producto

  def actualizar_producto(self, nombre, nuevo_precio_compra, nuevo_precio_venta, nueva_cantidad):
    nombre = str(nombre).strip().capitalize()
    try:
      nuevo_precio_compra = float(nuevo_precio_compra)
      nuevo_precio_venta = float(nuevo_precio_venta)
      nueva_cantidad = int(nueva_cantidad)
    except:
      raise ValueError("Precios y cantidad deben ser numéricos válidos.")
    if not self.productos:
      raise ValueError("El inventario está vacío.")
    producto = self.buscar_producto_por_nombre(nombre)
    if not producto:
      raise ValueError(f"No se encontró un producto con el nombre '{nombre}' en el inventario.")
    if nuevo_precio_compra <= 0 or nuevo_precio_venta <= 0:
      raise ValueError("El nuevo precio debe ser mayor que cero.")
    if nueva_cantidad <= 0:
      raise ValueError("La nueva cantidad debe ser mayor que cero.")
    producto.precio_compra = nuevo_precio_compra
    producto.precio_venta = nuevo_precio_venta
    producto.actualizar_stock(nueva_cantidad)
    self.sincronizar_data()
    self.guardar_inventario()
    logger.info(f"Producto actualizado: {nombre} - Precio compra: ${int(nuevo_precio_compra)}, Precio venta: ${int(nuevo_precio_venta)}, Cantidad: {nueva_cantidad}")
    return producto

  def registrar_entrada_producto(self, nombre, cantidad_entrada):
    nombre = str(nombre).strip().capitalize()
    try:
      cantidad_entrada = int(cantidad_entrada)
    except:
      raise ValueError("La cantidad de entrada debe ser un número entero.")
    if cantidad_entrada <= 0:
      raise ValueError("La cantidad de entrada debe ser mayor que cero.")
    producto = self.buscar_producto_por_nombre(nombre)
    if not producto:
      logger.warning(f"Intento de entrada para producto no encontrado: {nombre}")
      raise ValueError(f"No se encontró un producto con el nombre '{nombre}' en el inventario.")
    cantidad_anterior = producto.cantidad
    producto.actualizar_stock(producto.cantidad + cantidad_entrada)
    self.sincronizar_data()
    self.guardar_inventario()
    logger.info(f"Entrada registrada: {nombre} - Cantidad agregada: {cantidad_entrada} - Stock anterior: {cantidad_anterior} - Stock nuevo: {producto.cantidad}")
    return producto

  def registrar_salida_producto(self, nombre, cantidad_salida):
    nombre = str(nombre).strip().capitalize()
    try:
      cantidad_salida = int(cantidad_salida)
    except:
      raise ValueError("La cantidad de salida debe ser un número entero.")
    if cantidad_salida <= 0:
      raise ValueError("La cantidad de salida debe ser mayor que cero.")
    producto = self.buscar_producto_por_nombre(nombre)
    if not producto:
      logger.warning(f"Intento de salida para producto no encontrado: {nombre}")
      raise ValueError(f"No se encontró un producto con el nombre '{nombre}' en el inventario.")
    if cantidad_salida > producto.cantidad:
      logger.warning(f"Intento de salida con stock insuficiente: {nombre} - Stock actual: {producto.cantidad}, Solicitado: {cantidad_salida}")
      raise ValueError(f"No hay suficiente stock de '{nombre}' para realizar la salida.")
    cantidad_anterior = producto.cantidad
    producto.actualizar_stock(producto.cantidad - cantidad_salida)
    self.sincronizar_data()
    self.guardar_inventario()
    logger.info(f"Salida registrada: {nombre} - Cantidad retirada: {cantidad_salida} - Stock anterior: {cantidad_anterior} - Stock nuevo: {producto.cantidad}")
    return producto


# Sistema de ventas -----------------------------------------------------------------------------
class Venta:
  def __init__(self, producto_nombre, cantidad, precio_unitario, total, fecha_hora, sku):
    self.producto_nombre = producto_nombre
    self.cantidad = int(cantidad)
    self.precio_unitario = float(precio_unitario)
    self.total = float(total)
    self.fecha_hora = fecha_hora
    self.sku = int(sku)

  def to_dict(self):
    return {
      'Producto': self.producto_nombre,
      'Cantidad': self.cantidad,
      'Precio Unitario': self.precio_unitario,
      'Total': self.total,
      'Fecha/Hora': self.fecha_hora,
      'SKU': self.sku
    }


class RegistroVentas:
  def __init__(self, inventario_obj):
    self.ventas = []
    self.inventario = inventario_obj
    self.df = pd.DataFrame(columns=[
      'Producto', 'Cantidad', 'Precio Unitario', 'Total', 'Fecha/Hora', 'SKU'
    ])

  def sincronizar_data(self):
    rows = [v.to_dict() for v in self.ventas]
    self.df = pd.DataFrame(rows, columns=[
      'Producto', 'Cantidad', 'Precio Unitario', 'Total', 'Fecha/Hora', 'SKU'
    ])

  def registrar_venta(self, nombre_producto, cantidad, precio_unitario=None):
    nombre_producto = str(nombre_producto).strip().capitalize()
    
    # Buscar producto en inventario
    producto = self.inventario.buscar_producto_por_nombre(nombre_producto)
    if not producto:
      raise ValueError(f"No se encontró el producto '{nombre_producto}' en el inventario.")
    
    # Validar cantidad
    try:
      cantidad = int(cantidad)
    except:
      raise ValueError("La cantidad debe ser un número entero.")
    if cantidad <= 0:
      raise ValueError("La cantidad debe ser mayor que cero.")
    
    # Validar stock disponible
    if cantidad > producto.cantidad:
      raise ValueError(f"Stock insuficiente. Disponible: {producto.cantidad}, Solicitado: {cantidad}")
    
    # Usar precio del inventario 
    if precio_unitario is None:
      precio_unitario = producto.precio_venta
    else:
      try:
        precio_unitario = float(precio_unitario)
      except:
        raise ValueError("El precio unitario debe ser un número válido.")
    
    if precio_unitario <= 0:
      raise ValueError("El precio unitario debe ser mayor que cero.")
    
    # Calcular total
    total = cantidad * precio_unitario
    
    # Crear registro de venta
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    venta = Venta(
      producto_nombre=nombre_producto,
      cantidad=cantidad,
      precio_unitario=precio_unitario,
      total=total,
      fecha_hora=fecha_hora,
      sku=producto.sku
    )
    
    # Registrar venta
    self.ventas.append(venta)
    self.sincronizar_data()
    
    # Actualizar stock en inventario (salida automática)
    self.inventario.registrar_salida_producto(nombre_producto, cantidad)
    
    logger.info(f"Venta registrada: {nombre_producto} x{cantidad} @ ${int(precio_unitario)} = ${int(total)}")
    
    return venta

  def get_dataframe(self):
    return self.df.copy()

  def calcular_total_ventas(self):
    return sum(v.total for v in self.ventas)

  def obtener_ventas_por_producto(self):
    ventas_por_producto = {}
    for venta in self.ventas:
      if venta.producto_nombre not in ventas_por_producto:
        ventas_por_producto[venta.producto_nombre] = {
          'cantidad_total': 0,
          'total_ventas': 0.0
        }
      ventas_por_producto[venta.producto_nombre]['cantidad_total'] += venta.cantidad
      ventas_por_producto[venta.producto_nombre]['total_ventas'] += venta.total
    return ventas_por_producto
  
  

  



# main ------------------------------------------------------------------------------------------
def main():
  logger.info("=== Iniciando aplicación de Gestión de Inventario ===")
  inventario_obj = inventario()
  logger.info("Inventario inicializado")
  registro_ventas = RegistroVentas(inventario_obj)
  logger.info("Sistema de ventas inicializado")

  root = tk.Tk()
  root.title("Gestión de Inventario")
  root.geometry("1200x600")
  root.configure(bg="#f0f0f0")
  root.resizable(width=False, height=False)
  utl.centrar_ventana(root, 1200, 600)


  columns = ("Nombre", "Precio Venta", "Cantidad", "SKU", "Proveedor")
  tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
  for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=150)
  tree.pack(fill="both", expand=True, padx=10, pady=10)

  # Cargar inventario desde archivo pickle
  try:
    with open("inventario_data.pkl", "rb") as f:
      inventario_obj.productos = pickle.load(f)
    inventario_obj.sincronizar_data()
    logger.info(f"Inventario cargado desde archivo: {len(inventario_obj.productos)} productos")
  except FileNotFoundError:
    logger.info("Archivo de inventario no encontrado. Iniciando con inventario vacío.")
  except Exception as e:
    logger.error(f"Error al cargar inventario: {str(e)}")
    messagebox.showerror("Error", f"Error al cargar inventario: {str(e)}")


  # --- Pagination state --- IA --------------------------------------------------
  page_size = 100
  current_page = 1


  def refresh_tree():
    nonlocal current_page, page_size
    logger.debug(f"Refrescando árbol de productos - Página: {current_page}, Tamaño página: {page_size}")
    # Clear current items
    for row in tree.get_children():
      tree.delete(row)

    # Obtain dataset length and slice for current page
    try:
      df = inventario_obj.get_dataframe()
      total = len(df)
      if total == 0:
        update_pagination_info(0, 0, 0)
        actualizar_valor_total()
        return
      total_pages = max(1, (total + page_size - 1) // page_size)
      # clamp current_page
      if current_page < 1:
        current_page = 1
      if current_page > total_pages:
        current_page = total_pages
      start = (current_page - 1) * page_size
      end = start + page_size
      page_df = df.iloc[start:end]
      for _, r in page_df.iterrows():
        tree.insert(
          "", "end",
          values=(r['Nombre'], f"${int(r['PrecioVenta'])}", int(r['Cantidad']), int(r['SKU']), r['Proveedor'])
        )
      update_pagination_info(start + 1, min(end, total), total)
    except Exception:
      # Fallback to the in-memory list if dataframe is not ready
      prods = inventario_obj.productos
      total = len(prods)
      if total == 0:
        update_pagination_info(0, 0, 0)
        actualizar_valor_total()
        return
      total_pages = max(1, (total + page_size - 1) // page_size)
      if current_page < 1:
        current_page = 1
      if current_page > total_pages:
        current_page = total_pages
      start = (current_page - 1) * page_size
      end = start + page_size
      for p in prods[start:end]:
        tree.insert(
          "", "end",
          values=(p.nombre, f"${int(p.precio_venta)}", p.cantidad, p.sku, p.proveedor)
        )
      update_pagination_info(start + 1, min(end, total), total)
    
    # Actualizar valor total automáticamente
    actualizar_valor_total()

  def update_pagination_info(from_idx, to_idx, total):
    # updates the pagination label(s)
    try:
      pages = max(1, (total + page_size - 1) // page_size)
    except Exception:
      pages = 1
    lbl_page.config(text=f"Página {current_page} / {pages}")
    lbl_count.config(text=f"Mostrando {from_idx}-{to_idx} de {total}")

  # --- Pagination controls UI ---
  def go_first():
    nonlocal current_page
    current_page = 1
    refresh_tree()

  def go_prev():
    nonlocal current_page
    if current_page > 1:
      current_page -= 1
      refresh_tree()

  def go_next():
    nonlocal current_page
    try:
      total = len(inventario_obj.get_dataframe())
    except Exception:
      total = len(inventario_obj.productos)
    pages = max(1, (total + page_size - 1) // page_size)
    if current_page < pages:
      current_page += 1
      refresh_tree()

  def go_last():
    nonlocal current_page
    try:
      total = len(inventario_obj.get_dataframe())
    except Exception:
      total = len(inventario_obj.productos)
    pages = max(1, (total + page_size - 1) // page_size)
    current_page = pages
    refresh_tree()

  def go_to_page():
    nonlocal current_page
    try:
      v = int(e_page.get())
      if v < 1:
        v = 1
      current_page = v
      refresh_tree()
    except Exception:
      messagebox.showwarning("Aviso", "Página inválida")

  def change_page_size(*_):
    nonlocal page_size, current_page
    try:
      v = int(var_page_size.get())
      if v <= 0:
        raise ValueError()
      page_size = v
      current_page = 1
      refresh_tree()
    except Exception:
      messagebox.showwarning("Aviso", "Tamaño de página inválido")

  pagination_frame = tk.Frame(root)
  pagination_frame.pack(fill="x", padx=10, pady=4)

  tk.Button(pagination_frame, text="<<", width=3, command=go_first).pack(side="left", padx=2)
  tk.Button(pagination_frame, text="<", width=3, command=go_prev).pack(side="left", padx=2)
  lbl_page = tk.Label(pagination_frame, text="Página 1 / 1")
  lbl_page.pack(side="left", padx=6)

  tk.Label(pagination_frame, text="Ir a:").pack(side="left", padx=(8,2))
  e_page = tk.Entry(pagination_frame, width=5)
  e_page.pack(side="left")
  tk.Button(pagination_frame, text="Ir", width=4, command=go_to_page).pack(side="left", padx=4)

  tk.Button(pagination_frame, text=">", width=3, command=go_next).pack(side="left", padx=6)
  tk.Button(pagination_frame, text=">>", width=3, command=go_last).pack(side="left", padx=2)

  lbl_count = tk.Label(pagination_frame, text="Mostrando 0-0 de 0")
  lbl_count.pack(side="right")

  # page size selector
  var_page_size = tk.StringVar(value=str(page_size))
  tk.Label(pagination_frame, text="Tamaño página:").pack(side="right", padx=(4,2))
  opt = tk.OptionMenu(pagination_frame, var_page_size, "50", "100", "250", "500", "1000", command=change_page_size)
  opt.config(width=6)
  opt.pack(side="right")
  
  # Frame para mostrar valor total del inventario
  frame_valor_total = tk.Frame(root, bg="#f0f0f0")
  frame_valor_total.pack(fill="x", padx=10, pady=5)
  
  lbl_valor_total = tk.Label(
    frame_valor_total, 
    text="Valor Total del Inventario: $0", 
    font=("Arial", 14, "bold"),
    bg="#f0f0f0",
    fg="#000000"
  )
  lbl_valor_total.pack(side="right", padx=10)

  #---------------------------------------IA PURA---------------------------------------------

  def agregar():
    logger.info("Abriendo formulario para agregar producto")
    form = tk.Toplevel(root)
    form.title("Agregar producto")
    form.geometry("380x280")
    form.resizable(False, False)

    tk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
    e_nombre = tk.Entry(form, width=30)
    e_nombre.grid(row=0, column=1, padx=6, pady=6)

    tk.Label(form, text="Precio compra:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
    e_precio_compra = tk.Entry(form, width=30)
    e_precio_compra.grid(row=1, column=1, padx=6, pady=6)

    tk.Label(form, text="Precio venta:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
    e_precio_venta = tk.Entry(form, width=30)
    e_precio_venta.grid(row=2, column=1, padx=6, pady=6)

    tk.Label(form, text="Cantidad:").grid(row=3, column=0, sticky="e", padx=6, pady=6)
    e_cantidad = tk.Entry(form, width=30)
    e_cantidad.grid(row=3, column=1, padx=6, pady=6)

    tk.Label(form, text="Proveedor:").grid(row=4, column=0, sticky="e", padx=6, pady=6)
    e_proveedor = tk.Entry(form, width=30)
    e_proveedor.grid(row=4, column=1, padx=6, pady=6)

    def clear_fields():
      e_nombre.delete(0, tk.END)
      e_precio_compra.delete(0, tk.END)
      e_precio_venta.delete(0, tk.END)
      e_cantidad.delete(0, tk.END)
      e_proveedor.delete(0, tk.END)
      e_nombre.focus_set()

    def add_and_option(close_after=False):
      try:
        nombre = e_nombre.get()
        precio_compra = e_precio_compra.get()
        precio_venta = e_precio_venta.get()
        cantidad = e_cantidad.get()
        proveedor = e_proveedor.get()
        producto = inventario_obj.agregar_producto_manual(
          nombre, precio_compra, precio_venta, cantidad, proveedor
        )
        logger.info(f"Producto agregado exitosamente desde GUI: {producto.nombre} (SKU: {producto.sku})")
        messagebox.showinfo("Éxito", f"Producto '{producto.nombre}' agregado (SKU: {producto.sku})")
        refresh_tree()
        if close_after:
          form.destroy()
        else:
          clear_fields()
      except Exception as exc:
        logger.error(f"Error al agregar producto: {str(exc)}")
        messagebox.showerror("Error", str(exc))

    btn_frame = tk.Frame(form)
    btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

    btn_add_new = tk.Button(btn_frame, text="Agregar y nuevo", width=14, command=lambda: add_and_option(False))
    btn_add_close = tk.Button(btn_frame, text="Agregar y cerrar", width=14, command=lambda: add_and_option(True))
    btn_cancel = tk.Button(btn_frame, text="Cancelar", width=10, command=form.destroy)

    btn_add_new.pack(side="left", padx=4)
    btn_add_close.pack(side="left", padx=4)
    btn_cancel.pack(side="left", padx=4)

    form.bind("<Return>", lambda e: add_and_option(False))
    form.bind("<Escape>", lambda e: form.destroy())

    e_nombre.focus_set()

  def eliminar():
    logger.info("Abriendo formulario para eliminar producto")
    form = tk.Toplevel(root)
    form.title("Eliminar producto")
    form.geometry("360x120")
    form.resizable(False, False)

    tk.Label(form, text="Nombre del producto:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
    e_nombre = tk.Entry(form, width=30)
    e_nombre.grid(row=0, column=1, padx=6, pady=6)

    def clear_fields():
      e_nombre.delete(0, tk.END)
      e_nombre.focus_set()

    def do_delete(close_after=False):
      nombre = e_nombre.get()
      if not nombre:
        messagebox.showwarning("Aviso", "Ingrese un nombre de producto.")
        return
      try:
        producto = inventario_obj.eliminar_producto(nombre)
        logger.info(f"Producto eliminado exitosamente desde GUI: {producto.nombre} (SKU: {producto.sku})")
        messagebox.showinfo("Eliminar", f"Producto '{producto.nombre}' eliminado.")
        refresh_tree()
        if close_after:
          form.destroy()
        else:
          clear_fields()
      except Exception as e:
        logger.error(f"Error al eliminar producto: {str(e)}")
        messagebox.showerror("Error", str(e))

    btn_frame = tk.Frame(form)
    btn_frame.grid(row=1, column=0, columnspan=2, pady=8)
    tk.Button(btn_frame, text="Eliminar y nuevo", width=15, command=lambda: do_delete(False)).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Eliminar y cerrar", width=15, command=lambda: do_delete(True)).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Cancelar", width=10, command=form.destroy).pack(side="left", padx=4)

    form.bind("<Return>", lambda e: do_delete(False))
    form.bind("<Escape>", lambda e: form.destroy())
    e_nombre.focus_set()

  def actualizar():
    logger.info("Abriendo formulario para actualizar producto")
    form = tk.Toplevel(root)
    form.title("Actualizar producto")
    form.geometry("420x200")
    form.resizable(False, False)

    tk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
    e_nombre = tk.Entry(form, width=30)
    e_nombre.grid(row=0, column=1, padx=6, pady=6)

    tk.Label(form, text="Nuevo precio compra:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
    e_precio_compra = tk.Entry(form, width=30)
    e_precio_compra.grid(row=1, column=1, padx=6, pady=6)

    tk.Label(form, text="Nuevo precio venta:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
    e_precio_venta = tk.Entry(form, width=30)
    e_precio_venta.grid(row=2, column=1, padx=6, pady=6)

    tk.Label(form, text="Nueva cantidad:").grid(row=3, column=0, sticky="e", padx=6, pady=6)
    e_cantidad = tk.Entry(form, width=30)
    e_cantidad.grid(row=3, column=1, padx=6, pady=6)

    def clear_fields():
      e_nombre.delete(0, tk.END)
      e_precio_compra.delete(0, tk.END)
      e_precio_venta.delete(0, tk.END)
      e_cantidad.delete(0, tk.END)
      e_nombre.focus_set()

    def do_update(close_after=False):
      nombre = e_nombre.get()
      if not nombre:
        messagebox.showwarning("Aviso", "Ingrese el nombre del producto.")
        return
      try:
        nuevo_pc = e_precio_compra.get()
        nuevo_pv = e_precio_venta.get()
        nueva_cant = e_cantidad.get()
        producto = inventario_obj.actualizar_producto(nombre, nuevo_pc, nuevo_pv, nueva_cant)
        logger.info(f"Producto actualizado exitosamente desde GUI: {producto.nombre} (SKU: {producto.sku})")
        messagebox.showinfo("Actualizar", f"Producto '{producto.nombre}' actualizado.")
        refresh_tree()
        if close_after:
          form.destroy()
        else:
          clear_fields()
      except Exception as e:
        logger.error(f"Error al actualizar producto: {str(e)}")
        messagebox.showerror("Error", str(e))

    btn_frame = tk.Frame(form)
    btn_frame.grid(row=4, column=0, columnspan=2, pady=8)
    tk.Button(btn_frame, text="Actualizar y nuevo", width=16, command=lambda: do_update(False)).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Actualizar y cerrar", width=16, command=lambda: do_update(True)).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Cancelar", width=10, command=form.destroy).pack(side="left", padx=4)

  def entrada():
    logger.info("Abriendo formulario para registrar entrada")
    form = tk.Toplevel(root)
    form.title("Registrar entrada")
    form.geometry("360x140")
    form.resizable(False, False)

    tk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
    e_nombre = tk.Entry(form, width=30)
    e_nombre.grid(row=0, column=1, padx=6, pady=6)

    tk.Label(form, text="Cantidad entrada:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
    e_cantidad = tk.Entry(form, width=20)
    e_cantidad.grid(row=1, column=1, padx=6, pady=6)

    def clear_fields():
      e_nombre.delete(0, tk.END)
      e_cantidad.delete(0, tk.END)

    def do_entry(close_after=False):
      nombre = e_nombre.get()
      if not nombre:
        messagebox.showwarning("Aviso", "Ingrese el nombre del producto.")
        return
      try:
        cantidad = e_cantidad.get()
        producto = inventario_obj.registrar_entrada_producto(nombre, cantidad)
        logger.info(f"Entrada registrada exitosamente desde GUI: {producto.nombre} - Cantidad: {cantidad}")
        messagebox.showinfo("Entrada", f"Entrada registrada para '{producto.nombre}'. Nueva cantidad: {producto.cantidad}")
        refresh_tree()
        if close_after:
          form.destroy()
        else:
          clear_fields()
      except Exception as e:
        logger.error(f"Error al registrar entrada: {str(e)}")
        messagebox.showerror("Error", str(e))

    btn_frame = tk.Frame(form)
    btn_frame.grid(row=2, column=0, columnspan=2, pady=8)
    tk.Button(btn_frame, text="Registrar y nuevo", width=15, command=lambda: do_entry(False)).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Registrar y cerrar", width=15, command=lambda: do_entry(True)).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Cancelar", width=10, command=form.destroy).pack(side="left", padx=4)

    form.bind("<Return>", lambda e: do_entry(False))
    form.bind("<Escape>", lambda e: form.destroy())
    e_nombre.focus_set()

  def salida():
    logger.info("Abriendo formulario para registrar salida")
    form = tk.Toplevel(root)
    form.title("Registrar salida")
    form.geometry("360x140")
    form.resizable(False, False)

    tk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
    e_nombre = tk.Entry(form, width=30)
    e_nombre.grid(row=0, column=1, padx=6, pady=6)

    tk.Label(form, text="Cantidad salida:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
    e_cantidad = tk.Entry(form, width=20)
    e_cantidad.grid(row=1, column=1, padx=6, pady=6)

    def clear_fields():
      e_nombre.delete(0, tk.END)
      e_cantidad.delete(0, tk.END)
      e_nombre.focus_set()

    def do_exit(close_after=False):
      nombre = e_nombre.get()
      if not nombre:
        messagebox.showwarning("Aviso", "Ingrese el nombre del producto.")
        return
      try:
        cantidad = e_cantidad.get()
        producto = inventario_obj.registrar_salida_producto(nombre, cantidad)
        logger.info(f"Salida registrada exitosamente desde GUI: {producto.nombre} - Cantidad: {cantidad}")
        messagebox.showinfo("Salida", f"Salida registrada para '{producto.nombre}'. Nueva cantidad: {producto.cantidad}")
        refresh_tree()
        if close_after:
          form.destroy()
        else:
          clear_fields()
      except Exception as e:
        logger.error(f"Error al registrar salida: {str(e)}")
        messagebox.showerror("Error", str(e))

    btn_frame = tk.Frame(form)
    btn_frame.grid(row=2, column=0, columnspan=2, pady=8)
    tk.Button(btn_frame, text="Registrar y nuevo", width=15, command=lambda: do_exit(False)).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Registrar y cerrar", width=15, command=lambda: do_exit(True)).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Cancelar", width=10, command=form.destroy).pack(side="left", padx=4)

    form.bind("<Return>", lambda e: do_exit(False))
    form.bind("<Escape>", lambda e: form.destroy())
    e_nombre.focus_set()

  def reporte_stock_bajo():
    logger.info("Generando reporte de stock bajo")
    bajos = inventario_obj.obtener_productos_stock_bajo()
    if not bajos:
      logger.info("No se encontraron productos con stock bajo")
      messagebox.showinfo("Stock bajo", "No hay productos con stock bajo.")
      return
    logger.info(f"Reporte de stock bajo generado: {len(bajos)} producto(s) con stock bajo")
    texto = "\n".join(p.obtener_info() for p in bajos)
    win = tk.Toplevel(root)
    win.title("Reporte: Stock bajo")
    txt = tk.Text(win, width=100, height=20)
    txt.insert("1.0", texto)
    txt.config(state="disabled")
    txt.pack(fill="both", expand=True)

  def actualizar_valor_total():
    """Actualiza el Label con el valor total del inventario"""
    try:
      valor_total = inventario_obj.calcular_valor_total_recursivo()
      lbl_valor_total.config(text=f"Valor Total del Inventario: ${int(valor_total):,}")
    except Exception as e:
      logger.error(f"Error al calcular valor total: {str(e)}")
      lbl_valor_total.config(text="Valor Total del Inventario: $0")

  def buscar_sku():
    logger.info("Abriendo formulario para buscar por SKU")
    form = tk.Toplevel(root)
    form.title("Buscar por SKU")
    form.geometry("360x120")
    form.resizable(False, False)

    tk.Label(form, text="SKU:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
    e_sku = tk.Entry(form, width=25)
    e_sku.grid(row=0, column=1, padx=6, pady=6)

    def clear_fields():
      e_sku.delete(0, tk.END)
      e_sku.focus_set()

    def do_search(close_after=False):
      sku = e_sku.get()
      if not sku:
        messagebox.showwarning("Aviso", "Ingrese un SKU.")
        return
      try:
        p = inventario_obj.buscar_producto_por_sku(sku)
        if p:
          logger.info(f"Búsqueda por SKU exitosa: {sku} - {p.nombre}")
          messagebox.showinfo("Producto encontrado", p.obtener_info())
        else:
          logger.info(f"Búsqueda por SKU sin resultados: {sku}")
          messagebox.showwarning("No encontrado", f"No se encontró producto con SKU {sku}.")
        if close_after:
          form.destroy()
        else:
          clear_fields()
      except Exception as e:
        logger.error(f"Error en búsqueda por SKU: {str(e)}")
        messagebox.showerror("Error", str(e))

    btn_frame = tk.Frame(form)
    btn_frame.grid(row=1, column=0, columnspan=2, pady=8)
    tk.Button(btn_frame, text="Buscar y nuevo", width=12, command=lambda: do_search(False)).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Buscar y cerrar", width=12, command=lambda: do_search(True)).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Cancelar", width=10, command=form.destroy).pack(side="left", padx=4)

    form.bind("<Return>", lambda e: do_search(False))
    form.bind("<Escape>", lambda e: form.destroy())
    e_sku.focus_set()

  def exportar_xls():
    logger.info("Exportando inventario a archivo Excel")
    try:
      df = inventario_obj.get_dataframe()
      if df.empty:
        messagebox.showwarning("Aviso", "El inventario está vacío. No se puede exportar.")
        logger.warning("Intento de exportación a Excel con inventario vacío")
        return
      filename = f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
      df.to_excel(filename, index=False)
      logger.info(f"Inventario exportado exitosamente a '{filename}'")
      messagebox.showinfo("Éxito", f"Inventario exportado a '{filename}'")
    except Exception as e:
      logger.error(f"Error al exportar a Excel: {str(e)}")
      messagebox.showerror("Error", f"No se pudo exportar el inventario: {str(e)}")

  def descargar_log():
    """Descarga el archivo de log del sistema (solo admin)"""
    logger.info("Solicitud de descarga de log por administrador")
    try:
      import os
      import shutil
      
      # Buscar el archivo de log más reciente
      log_files = [f for f in os.listdir('.') if f.startswith('inventario_log_') and f.endswith('.log')]
      
      if not log_files:
        messagebox.showwarning("Aviso", "No se encontró ningún archivo de log.")
        logger.warning("Intento de descargar log pero no hay archivos de log")
        return
      
      # Ordenar por fecha de modificación (más reciente primero)
      log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
      log_file = log_files[0]
      
      # Crear nombre de copia con timestamp
      timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
      copy_filename = f"log_inventario_{timestamp}.log"
      
      # Copiar el archivo
      shutil.copy2(log_file, copy_filename)
      
      logger.info(f"Log descargado exitosamente: '{copy_filename}'")
      messagebox.showinfo("Éxito", f"Log descargado como '{copy_filename}'")
    except Exception as e:
      logger.error(f"Error al descargar log: {str(e)}")
      messagebox.showerror("Error", f"No se pudo descargar el log: {str(e)}")

  def ventas():
    logger.info("Abriendo ventana de registro de ventas")
    ventana_ventas = tk.Toplevel(root)
    ventana_ventas.title("Registro de Ventas")
    ventana_ventas.geometry("1000x650")
    
    # Frame superior para formulario de venta
    frame_form = tk.Frame(ventana_ventas)
    frame_form.pack(fill="x", padx=10, pady=10)
    
    tk.Label(frame_form, text="Producto:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    e_producto = tk.Entry(frame_form, width=30)
    e_producto.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(frame_form, text="Cantidad:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
    e_cantidad = tk.Entry(frame_form, width=15)
    e_cantidad.grid(row=0, column=3, padx=5, pady=5)
    
    tk.Label(frame_form, text="Precio unitario (opcional):").grid(row=0, column=4, sticky="e", padx=5, pady=5)
    e_precio = tk.Entry(frame_form, width=15)
    e_precio.grid(row=0, column=5, padx=5, pady=5)
    
    def calcular_total():
      try:
        cantidad = int(e_cantidad.get()) if e_cantidad.get() else 0
        precio = float(e_precio.get()) if e_precio.get() else 0
        if precio == 0:
          # Intentar obtener precio del producto
          producto_nombre = e_producto.get().strip().capitalize()
          if producto_nombre:
            producto = inventario_obj.buscar_producto_por_nombre(producto_nombre)
            if producto:
              precio = producto.precio_venta
              e_precio.delete(0, tk.END)
              e_precio.insert(0, str(int(precio)))
        total = cantidad * precio
        lbl_total.config(text=f"Total: ${int(total)}")
      except:
        lbl_total.config(text="Total: $0")
    
    e_producto.bind("<KeyRelease>", lambda e: calcular_total())
    e_cantidad.bind("<KeyRelease>", lambda e: calcular_total())
    e_precio.bind("<KeyRelease>", lambda e: calcular_total())
    
    lbl_total = tk.Label(frame_form, text="Total: $0", font=("Arial", 12, "bold"))
    lbl_total.grid(row=0, column=6, padx=10, pady=5)
    
    def registrar_venta():
      producto_nombre = e_producto.get()
      cantidad = e_cantidad.get()
      precio_unit = e_precio.get() if e_precio.get() else None
      
      if not producto_nombre:
        messagebox.showwarning("Aviso", "Ingrese el nombre del producto.")
        return
      if not cantidad:
        messagebox.showwarning("Aviso", "Ingrese la cantidad.")
        return
      
      try:
        venta = registro_ventas.registrar_venta(producto_nombre, cantidad, precio_unit)
        messagebox.showinfo("Venta registrada", 
          f"Venta registrada:\n{venta.producto_nombre} x{venta.cantidad}\n"
          f"Precio unitario: ${int(venta.precio_unitario)}\n"
          f"Total: ${int(venta.total)}\n"
          f"Fecha: {venta.fecha_hora}")
        refresh_tree()
        refresh_tree_ventas()
        e_producto.delete(0, tk.END)
        e_cantidad.delete(0, tk.END)
        e_precio.delete(0, tk.END)
        lbl_total.config(text="Total: $0")
        e_producto.focus_set()
      except Exception as e:
        logger.error(f"Error al registrar venta: {str(e)}")
        messagebox.showerror("Error", str(e))
    
    btn_registrar = tk.Button(frame_form, text="Registrar Venta", command=registrar_venta, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
    btn_registrar.grid(row=0, column=7, padx=10, pady=5)
    
    # Frame para tabla de ventas
    frame_tabla = tk.Frame(ventana_ventas)
    frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)
    
    columns_ventas = ("Producto", "Cantidad", "Precio Unitario", "Total", "Fecha/Hora", "SKU")
    tree_ventas = ttk.Treeview(frame_tabla, columns=columns_ventas, show="headings", height=20)
    for col in columns_ventas:
      tree_ventas.heading(col, text=col)
      tree_ventas.column(col, anchor="center", width=150)
    
    scrollbar_ventas = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree_ventas.yview)
    tree_ventas.configure(yscrollcommand=scrollbar_ventas.set)
    
    tree_ventas.pack(side="left", fill="both", expand=True)
    scrollbar_ventas.pack(side="right", fill="y")
    
    def refresh_tree_ventas():
      for row in tree_ventas.get_children():
        tree_ventas.delete(row)
      df_ventas = registro_ventas.get_dataframe()
      for _, r in df_ventas.iterrows():
        tree_ventas.insert("", "end", values=(
          r['Producto'], 
          int(r['Cantidad']), 
          f"${int(r['Precio Unitario'])}", 
          f"${int(r['Total'])}", 
          r['Fecha/Hora'], 
          int(r['SKU'])
        ))
      # Actualizar totales
      total_ventas = registro_ventas.calcular_total_ventas()
      lbl_total_ventas.config(text=f"Total de ventas: ${int(total_ventas)}")
    
    # Frame inferior para totales
    frame_totales = tk.Frame(ventana_ventas)
    frame_totales.pack(fill="x", padx=10, pady=10)
    
    lbl_total_ventas = tk.Label(frame_totales, text="Total de ventas: $0", font=("Arial", 12, "bold"))
    lbl_total_ventas.pack(side="left", padx=10)
    
    btn_exportar_ventas = tk.Button(frame_totales, text="Exportar Ventas a Excel", command=lambda: exportar_ventas_xls(), bg="#1D6F42", fg="white", font=("Arial", 10, "bold"))
    btn_exportar_ventas.pack(side="right", padx=10)
    
    def exportar_ventas_xls():
      logger.info("Exportando ventas a archivo Excel")
      try:
        df_ventas = registro_ventas.get_dataframe()
        if df_ventas.empty:
          messagebox.showwarning("Aviso", "No hay ventas registradas para exportar.")
          logger.warning("Intento de exportación de ventas con registro vacío")
          return
        filename = f"ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df_ventas.to_excel(filename, index=False)
        logger.info(f"Ventas exportadas exitosamente a '{filename}'")
        messagebox.showinfo("Éxito", f"Ventas exportadas a '{filename}'")
      except Exception as e:
        logger.error(f"Error al exportar ventas a Excel: {str(e)}")
        messagebox.showerror("Error", f"No se pudo exportar las ventas: {str(e)}")
    
    refresh_tree_ventas()
    e_producto.focus_set()

    

  # Botones
  frame = tk.Frame(root)
  frame.pack(fill="x", padx=11, pady=5)
  btn_agregar = tk.Button(frame, text="Agregar", command=agregar, bg="#69F36E", fg="black", font=("Arial", 9, "bold"))
  btn_eliminar = tk.Button(frame, text="Eliminar", command=eliminar, bg="#D80000", fg="white", font=("Arial", 9, "bold"))
  btn_actualizar = tk.Button(frame, text="Actualizar", command=actualizar, bg="#6E03FA", fg="white", font=("Arial", 9, "bold"))
  btn_mostrar = tk.Button(frame, text="Refrescar", command=refresh_tree)
  btn_entrada = tk.Button(frame, text="Registrar Entrada", command=entrada)
  btn_salida = tk.Button(frame, text="Registrar Salida", command=salida)
  btn_reporte = tk.Button(frame, text="Reporte stock bajo", command=reporte_stock_bajo, bg="#FF6600", fg="white", font=("Arial", 9, "bold"))
  btn_buscar = tk.Button(frame, text="Buscar por SKU", command=buscar_sku, bg="#00ACC1", fg="white", font=("Arial", 9, "bold"))
  btn_exportar = tk.Button(frame, text="Exportar a Excel", command=exportar_xls,bg="#1D6F42", fg="white", font=("Arial", 9, "bold"))
  btn_ventas = tk.Button(frame, text="Registrar Ventas", command=ventas, bg="#2196F3", fg="white", font=("Arial", 9, "bold"))
  btn_salir = tk.Button(frame, text="Salir", command=root.destroy)

  # Botón de descarga de log en ubicación discreta (esquina inferior derecha, casi inaccesible)
  btn_descargar_log = tk.Button(
    root, 
    text="📋", 
    command=descargar_log, 
    bg="#9C27B0", 
    fg="white", 
    font=("Arial", 7),
    width=1,
    height=1,
    relief="flat",
    cursor="hand2"
  )
  btn_descargar_log.place(relx=0.995, rely=0.99, anchor="se")

  # Deshabilitar acciones importantes si el usuario no es admin
  try:
    user_role = getattr(current_user, 'role', None)
    if user_role != 'admin':
      btn_eliminar.config(state='disabled')
      btn_actualizar.config(state='disabled')
      btn_descargar_log.config(state='disabled')
  except NameError:
    # current_user no definido -> comportarse como no autenticado (deshabilitar admin)
    btn_eliminar.config(state='disabled')
    btn_actualizar.config(state='disabled')
    btn_descargar_log.config(state='disabled')

  for w in (btn_agregar, btn_eliminar, btn_actualizar, btn_mostrar, btn_entrada, btn_salida, btn_reporte, btn_buscar, btn_exportar, btn_ventas, btn_salir):
    w.pack(side="left", padx=5, pady=5)

  logger.info("Interfaz gráfica inicializada - Iniciando loop principal")
  refresh_tree()  # Esto también actualizará el valor total automáticamente
  root.mainloop()
  logger.info("=== Aplicación cerrada ===")



if __name__ == "__main__":
  main()