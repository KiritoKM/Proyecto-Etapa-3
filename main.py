#Proyecto3.py

import random
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import pandas as pd
import calendar
import logging 
from datetime import datetime
import faker as fk
import pickle
import util.generic as utl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


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
  def __init__(self, nombre, precio_compra, precio_venta, cantidad, sku, proveedor, categoria="Sin categoría"):
    self.nombre = nombre.capitalize()
    self.precio_compra = float(precio_compra)
    self.precio_venta = float(precio_venta)
    self.cantidad = int(cantidad)
    self.sku = int(sku)
    self.proveedor = proveedor.capitalize()
    self.categoria = categoria
    logger.info(f"Producto creado: {self.nombre} (SKU: {self.sku}) - Categoría: {self.categoria} - Precio venta: ${int(self.precio_venta)} - Cantidad: {self.cantidad}")

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
      f"Nombre: {self.nombre} || Categoría: {self.categoria} || Precio: ${int(self.precio_venta)} || "
      f"Cantidad: {self.cantidad} || Codigo: {self.sku} || Proveedor: {self.proveedor}"
    )


# Sistema de gestión de categorías
def cargar_categorias():
  """Carga las categorías desde archivo pickle"""
  try:
    with open("categorias.pkl", "rb") as f:
      categorias = pickle.load(f)
    logger.info(f"Categorías cargadas: {len(categorias)} categorías disponibles")
    return categorias
  except FileNotFoundError:
    # Categorías por defecto
    categorias_default = ["Electrónica", "Ropa", "Alimentos", "Hogar", "Deportes", "Libros", "Juguetes", "Sin categoría"]
    guardar_categorias(categorias_default)
    logger.info("Categorías por defecto creadas")
    return categorias_default
  except Exception as e:
    logger.error(f"Error al cargar categorías: {str(e)}")
    return ["Sin categoría"]

def guardar_categorias(categorias):
  """Guarda las categorías en archivo pickle"""
  try:
    with open("categorias.pkl", "wb") as f:
      pickle.dump(categorias, f)
    logger.info(f"Categorías guardadas: {len(categorias)} categorías")
  except Exception as e:
    logger.error(f"Error al guardar categorías: {str(e)}")

class inventario:
  def __init__(self):
    self.productos = []
    self.df = pd.DataFrame(columns=[
      'Nombre', 'Categoría', 'PrecioCompra', 'PrecioVenta', 'Cantidad', 'SKU', 'Proveedor'
    ])

  def sincronizar_data(self):
    rows = [
      {
        'Nombre': p.nombre,
        'Categoría': p.categoria,
        'PrecioCompra': p.precio_compra,
        'PrecioVenta': p.precio_venta,
        'Cantidad': p.cantidad,
        'SKU': p.sku,
        'Proveedor': p.proveedor
      }
      for p in self.productos
    ]
    self.df = pd.DataFrame(rows, columns=[
      'Nombre', 'Categoría', 'PrecioCompra', 'PrecioVenta', 'Cantidad', 'SKU', 'Proveedor'
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
  def agregar_producto_manual(self, nombre, precio_compra, precio_venta, cantidad, proveedor, categoria="Sin categoría", sku=None):
    nombre = str(nombre).strip().capitalize()
    proveedor = str(proveedor).strip().capitalize()
    categoria = str(categoria).strip()
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
    if not categoria:
      categoria = "Sin categoría"
    if sku is None:
      sku = random.randint(100000, 999999)
      while any(producto.sku == sku for producto in self.productos):
        sku = random.randint(100000, 999999)
    else:
      sku = int(sku)
      if any(producto.sku == sku for producto in self.productos):
        raise ValueError(f"Ya existe un producto con el SKU '{sku}'.")
    producto = Producto(nombre, precio_compra, precio_venta, cantidad, sku, proveedor, categoria)
    self.productos.append(producto)
    self.sincronizar_data()
    self.guardar_inventario()
    logger.info(f"Producto agregado al inventario: {producto.nombre} (SKU: {producto.sku}) - Categoría: {categoria} - Total productos: {len(self.productos)}")
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

  def actualizar_producto(self, nombre, nuevo_precio_compra, nuevo_precio_venta, nueva_cantidad, nueva_categoria=None):
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
    if nueva_categoria:
      producto.categoria = nueva_categoria
    self.sincronizar_data()
    self.guardar_inventario()
    logger.info(f"Producto actualizado: {nombre} - Precio compra: ${int(nuevo_precio_compra)}, Precio venta: ${int(nuevo_precio_venta)}, Cantidad: {nueva_cantidad}, Categoría: {producto.categoria}")
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
  def __init__(self, producto_nombre, cantidad, precio_unitario, total, fecha_hora, sku, categoria):
    self.producto_nombre = producto_nombre
    self.cantidad = int(cantidad)
    self.precio_unitario = float(precio_unitario)
    self.total = float(total)
    self.fecha_hora = fecha_hora
    self.sku = int(sku)
    self.categoria = categoria

  def to_dict(self):
    return {
      'Producto': self.producto_nombre,
      'Categoría': self.categoria,
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
      'Producto', 'Categoría', 'Cantidad', 'Precio Unitario', 'Total', 'Fecha/Hora', 'SKU'
    ])

  def sincronizar_data(self):
    rows = [v.to_dict() for v in self.ventas]
    self.df = pd.DataFrame(rows, columns=[
      'Producto', 'Categoría', 'Cantidad', 'Precio Unitario', 'Total', 'Fecha/Hora', 'SKU'
    ])

  def guardar_ventas(self):
    """Guarda las ventas en un archivo pickle"""
    try:
      with open("ventas_data.pkl", "wb") as f:
        pickle.dump(self.ventas, f)
      logger.debug("Ventas guardadas en archivo pickle")
    except Exception as e:
      logger.error(f"Error al guardar ventas: {str(e)}")

  def cargar_ventas(self):
    """Carga las ventas desde un archivo pickle"""
    try:
      with open("ventas_data.pkl", "rb") as f:
        self.ventas = pickle.load(f)
      self.sincronizar_data()
      logger.info(f"Ventas cargadas desde archivo: {len(self.ventas)} ventas registradas")
    except FileNotFoundError:
      logger.info("Archivo de ventas no encontrado. Iniciando con registro de ventas vacío.")
    except Exception as e:
      logger.error(f"Error al cargar ventas: {str(e)}")

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
    categoria = getattr(producto, 'categoria', 'Sin categoría')
    venta = Venta(
      producto_nombre=nombre_producto,
      cantidad=cantidad,
      precio_unitario=precio_unitario,
      total=total,
      fecha_hora=fecha_hora,
      sku=producto.sku,
      categoria=categoria
    )
    
    # Registrar venta
    self.ventas.append(venta)
    self.sincronizar_data()
    
    # Guardar ventas en archivo pickle
    self.guardar_ventas()
    
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
  
  

  



# Funciones de importación y limpieza de datos --------------------------------------------
def importar_inventario_desde_excel(inventario_obj, ruta_archivo):
  """Importa productos desde un archivo Excel"""
  logger.info(f"Importando inventario desde Excel: {ruta_archivo}")
  productos_importados = 0
  productos_duplicados = 0
  productos_con_errores = 0
  
  try:
    df = pd.read_excel(ruta_archivo)
    
    # Mapear columnas posibles
    columnas_esperadas = {
      'Nombre': ['Nombre', 'nombre', 'NOMBRE', 'Producto', 'producto', 'PRODUCTO'],
      'PrecioCompra': ['PrecioCompra', 'precio_compra', 'Precio Compra', 'Precio de Compra', 'precio compra'],
      'PrecioVenta': ['PrecioVenta', 'precio_venta', 'Precio Venta', 'Precio de Venta', 'precio venta'],
      'Cantidad': ['Cantidad', 'cantidad', 'CANTIDAD', 'Stock', 'stock', 'STOCK'],
      'SKU': ['SKU', 'sku', 'Codigo', 'código', 'Código', 'CODIGO'],
      'Proveedor': ['Proveedor', 'proveedor', 'PROVEEDOR', 'Supplier', 'supplier'],
      'Categoría': ['Categoría', 'categoria', 'Categoría', 'CATEGORIA', 'Category', 'category', 'Tipo', 'tipo']
    }
    
    # Buscar columnas en el DataFrame
    columnas_encontradas = {}
    for col_esperada, posibles_nombres in columnas_esperadas.items():
      for nombre_posible in posibles_nombres:
        if nombre_posible in df.columns:
          columnas_encontradas[col_esperada] = nombre_posible
          break
    
    if 'Nombre' not in columnas_encontradas:
      raise ValueError("No se encontró la columna 'Nombre' en el archivo Excel")
    
    for index, row in df.iterrows():
      try:
        nombre = str(row[columnas_encontradas.get('Nombre', 'Nombre')]).strip()
        if pd.isna(nombre) or nombre == "" or nombre == "nan":
          productos_con_errores += 1
          continue
        
        precio_compra = float(row[columnas_encontradas.get('PrecioCompra', 'PrecioCompra')]) if 'PrecioCompra' in columnas_encontradas else 0
        precio_venta = float(row[columnas_encontradas.get('PrecioVenta', 'PrecioVenta')]) if 'PrecioVenta' in columnas_encontradas else precio_compra * 1.5
        cantidad = int(row[columnas_encontradas.get('Cantidad', 'Cantidad')]) if 'Cantidad' in columnas_encontradas else 0
        sku = int(row[columnas_encontradas.get('SKU', 'SKU')]) if 'SKU' in columnas_encontradas else None
        proveedor = str(row[columnas_encontradas.get('Proveedor', 'Proveedor')]).strip() if 'Proveedor' in columnas_encontradas else "Proveedor Desconocido"
        categoria = str(row[columnas_encontradas.get('Categoría', 'Categoría')]).strip() if 'Categoría' in columnas_encontradas else "Sin categoría"
        
        if pd.isna(proveedor) or proveedor == "" or proveedor == "nan":
          proveedor = "Proveedor Desconocido"
        if pd.isna(categoria) or categoria == "" or categoria == "nan":
          categoria = "Sin categoría"
        
        # Verificar si el producto ya existe
        if any(p.nombre == nombre.capitalize() for p in inventario_obj.productos):
          productos_duplicados += 1
          continue
        
        inventario_obj.agregar_producto_manual(
          nombre=nombre,
          precio_compra=precio_compra,
          precio_venta=precio_venta,
          cantidad=cantidad,
          proveedor=proveedor,
          categoria=categoria,
          sku=sku
        )
        productos_importados += 1
      except Exception as e:
        logger.warning(f"Error al importar producto en fila {index + 2}: {str(e)}")
        productos_con_errores += 1
        continue
    
    logger.info(f"Importación completada: {productos_importados} productos importados, {productos_duplicados} duplicados, {productos_con_errores} con errores")
    return {
      'importados': productos_importados,
      'duplicados': productos_duplicados,
      'errores': productos_con_errores
    }
  except Exception as e:
    logger.error(f"Error al importar inventario desde Excel: {str(e)}")
    raise


def importar_ventas_desde_excel(registro_ventas, ruta_archivo):
  """Importa ventas desde un archivo Excel"""
  logger.info(f"Importando ventas desde Excel: {ruta_archivo}")
  ventas_importadas = 0
  ventas_con_errores = 0
  
  try:
    df = pd.read_excel(ruta_archivo)
    
    # Mapear columnas posibles
    columnas_esperadas = {
      'Producto': ['Producto', 'producto', 'PRODUCTO', 'Nombre', 'nombre'],
      'Cantidad': ['Cantidad', 'cantidad', 'CANTIDAD'],
      'Precio Unitario': ['Precio Unitario', 'precio_unitario', 'Precio', 'precio', 'Precio Unit'],
      'Total': ['Total', 'total', 'TOTAL'],
      'Fecha/Hora': ['Fecha/Hora', 'Fecha', 'fecha', 'Fecha y Hora', 'Fecha_Hora', 'fecha_hora'],
      'SKU': ['SKU', 'sku', 'Codigo', 'código'],
      'Categoría': ['Categoría', 'categoria', 'Categoría', 'Category', 'category']
    }
    
    # Buscar columnas en el DataFrame
    columnas_encontradas = {}
    for col_esperada, posibles_nombres in columnas_esperadas.items():
      for nombre_posible in posibles_nombres:
        if nombre_posible in df.columns:
          columnas_encontradas[col_esperada] = nombre_posible
          break
    
    if 'Producto' not in columnas_encontradas:
      raise ValueError("No se encontró la columna 'Producto' en el archivo Excel")
    
    for index, row in df.iterrows():
      try:
        producto_nombre = str(row[columnas_encontradas.get('Producto', 'Producto')]).strip()
        if pd.isna(producto_nombre) or producto_nombre == "" or producto_nombre == "nan":
          ventas_con_errores += 1
          continue
        
        cantidad = int(row[columnas_encontradas.get('Cantidad', 'Cantidad')]) if 'Cantidad' in columnas_encontradas else 1
        precio_unitario = float(row[columnas_encontradas.get('Precio Unitario', 'Precio Unitario')]) if 'Precio Unitario' in columnas_encontradas else 0
        total = float(row[columnas_encontradas.get('Total', 'Total')]) if 'Total' in columnas_encontradas else cantidad * precio_unitario
        fecha_hora = str(row[columnas_encontradas.get('Fecha/Hora', 'Fecha/Hora')]) if 'Fecha/Hora' in columnas_encontradas else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sku = int(row[columnas_encontradas.get('SKU', 'SKU')]) if 'SKU' in columnas_encontradas else 0
        categoria = str(row[columnas_encontradas.get('Categoría', 'Categoría')]).strip() if 'Categoría' in columnas_encontradas else "Sin categoría"
        
        if pd.isna(categoria) or categoria == "" or categoria == "nan":
          categoria = "Sin categoría"
        
        # Validar datos
        if cantidad <= 0 or precio_unitario <= 0 or total <= 0:
          ventas_con_errores += 1
          continue
        
        # Crear venta
        venta = Venta(
          producto_nombre=producto_nombre,
          cantidad=cantidad,
          precio_unitario=precio_unitario,
          total=total,
          fecha_hora=fecha_hora,
          sku=sku,
          categoria=categoria
        )
        
        registro_ventas.ventas.append(venta)
        ventas_importadas += 1
      except Exception as e:
        logger.warning(f"Error al importar venta en fila {index + 2}: {str(e)}")
        ventas_con_errores += 1
        continue
    
    registro_ventas.sincronizar_data()
    registro_ventas.guardar_ventas()
    logger.info(f"Importación de ventas completada: {ventas_importadas} ventas importadas, {ventas_con_errores} con errores")
    return {
      'importadas': ventas_importadas,
      'errores': ventas_con_errores
    }
  except Exception as e:
    logger.error(f"Error al importar ventas desde Excel: {str(e)}")
    raise


def limpiar_datos_nulos(inventario_obj, registro_ventas):
  """Limpia datos nulos, valores negativos y otros errores en productos y ventas"""
  logger.info("Iniciando limpieza de datos nulos y errores")
  
  productos_limpiados = 0
  ventas_limpiadas = 0
  ventas_eliminadas = 0
  
  # Limpiar productos
  for producto in inventario_obj.productos:
    cambios = False
    
    if not producto.nombre or producto.nombre.strip() == "":
      producto.nombre = f"Producto_SKU_{producto.sku}"
      cambios = True
    
    if producto.precio_compra < 0:
      producto.precio_compra = abs(producto.precio_compra)
      cambios = True
    if producto.precio_venta < 0 or producto.precio_venta < producto.precio_compra:
      producto.precio_venta = max(producto.precio_compra * 1.2, 1000)
      cambios = True
    
    if producto.cantidad < 0:
      producto.cantidad = 0
      cambios = True
    
    if not producto.categoria or producto.categoria.strip() == "":
      producto.categoria = "Sin categoría"
      cambios = True
    
    if not producto.proveedor or producto.proveedor.strip() == "":
      producto.proveedor = "Proveedor Desconocido"
      cambios = True
    
    if producto.sku <= 0:
      # Generar SKU único en rango 1 a 600,000
      skus_existentes = {p.sku for p in inventario_obj.productos if p.sku > 0}
      if skus_existentes:
        producto.sku = min(max(skus_existentes) + 1, 600000)
      else:
        producto.sku = random.randint(1, 600000)
      cambios = True
    
    if cambios:
      productos_limpiados += 1
  
  # Limpiar ventas
  ventas_validas = []
  for venta in registro_ventas.ventas:
    es_valida = True
    
    if not venta.producto_nombre or venta.producto_nombre.strip() == "":
      es_valida = False
    
    if venta.cantidad <= 0:
      es_valida = False
    
    if venta.precio_unitario <= 0:
      es_valida = False
    
    if venta.total <= 0 or abs(venta.total - (venta.cantidad * venta.precio_unitario)) > 0.01:
      venta.total = venta.cantidad * venta.precio_unitario
      ventas_limpiadas += 1
    
    try:
      datetime.strptime(venta.fecha_hora, '%Y-%m-%d %H:%M:%S')
    except:
      es_valida = False
    
    if not venta.categoria or venta.categoria.strip() == "":
      venta.categoria = "Sin categoría"
      ventas_limpiadas += 1
    
    if venta.sku <= 0:
      es_valida = False
    
    if es_valida:
      ventas_validas.append(venta)
    else:
      ventas_eliminadas += 1
  
  registro_ventas.ventas = ventas_validas
  registro_ventas.sincronizar_data()
  inventario_obj.sincronizar_data()
  
  inventario_obj.guardar_inventario()
  registro_ventas.guardar_ventas()
  
  logger.info(f"Limpieza completada: {productos_limpiados} productos corregidos, {ventas_limpiadas} ventas corregidas, {ventas_eliminadas} ventas eliminadas")
  
  return {
    'productos_limpiados': productos_limpiados,
    'ventas_limpiadas': ventas_limpiadas,
    'ventas_eliminadas': ventas_eliminadas
  }


def generar_datos_aleatorios_excel(cantidad_productos=50, cantidad_ventas=200):
  """Genera productos y ventas aleatorios con errores y datos nulos, guardándolos en archivos Excel"""
  logger.info(f"Generando {cantidad_productos} productos y {cantidad_ventas} ventas aleatorias en archivos Excel")
  
  # Validar que no se exceda el límite de SKU
  if cantidad_productos > 600000:
    raise ValueError(f"La cantidad máxima de productos es 600,000. Se solicitó: {cantidad_productos}")
  
  categorias = cargar_categorias()
  productos_data = []
  ventas_data = []
  
  # Usar conjuntos para rastrear SKUs y nombres únicos y evitar duplicados
  skus_usados = set()
  nombres_usados = set()
  
  # Generar productos aleatorios
  for i in range(cantidad_productos):
    try:
      # Generar datos con posibilidad de valores nulos/erróneos
      if random.random() > 0.1:  # 90% de probabilidad de nombre válido
        # Generar nombres únicos usando faker
        intentos_nombre = 0
        while intentos_nombre < 100:
          nombre = faker.word().capitalize() + "_" + faker.word().capitalize() + "_" + str(i + 1)
          if nombre not in nombres_usados:
            break
          intentos_nombre += 1
        if intentos_nombre >= 100:
          nombre = f"Producto_{i + 1}"
      else:
        nombre = None if random.random() > 0.5 else ""  # 10% de probabilidad de nulo o vacío
      
      if nombre is None or nombre == "":
        nombre = f"Producto_{i + 1}"
      
      # Asegurar que el nombre sea único
      if nombre in nombres_usados:
        nombre = f"{nombre}_{i + 1}"
      
      nombres_usados.add(nombre)
      
      # Categoría con posibilidad de nulo
      if random.random() > 0.15:
        categoria = random.choice(categorias)
      else:
        categoria = None if random.random() > 0.5 else ""
      
      if not categoria:
        categoria = "Sin categoría"
      
      # Proveedor con posibilidad de nulo
      if random.random() > 0.1:
        proveedor = faker.company()
      else:
        proveedor = None if random.random() > 0.5 else ""
      
      if not proveedor:
        proveedor = "Proveedor Desconocido"
      
      # Precios con posibilidad de valores negativos o nulos
      if random.random() > 0.1:
        precio_compra = round(random.uniform(1000, 50000), 2)
      else:
        precio_compra = round(random.uniform(-100, 0), 2) if random.random() > 0.5 else 0
      
      if random.random() > 0.1:
        precio_venta = round(precio_compra * random.uniform(1.2, 2.5), 2)
      else:
        precio_venta = round(random.uniform(-50, 0), 2) if random.random() > 0.5 else None
      
      if precio_venta is None or precio_venta <= 0:
        precio_venta = round(precio_compra * 1.5, 2)
      
      # Cantidad con posibilidad de valores negativos
      if random.random() > 0.1:
        cantidad = random.randint(0, 500)
      else:
        cantidad = random.randint(-50, -1)
      
      if cantidad < 0:
        cantidad = 0
      
      # SKU único - usar secuencial desde 1 hasta cantidad_productos (máximo 600,000)
      if random.random() > 0.1:  # 90% de probabilidad de SKU válido
        # Usar SKU secuencial para garantizar unicidad (1, 2, 3, ..., cantidad_productos)
        sku = i + 1
      else:
        # 10% de probabilidad de SKU inválido (para pruebas de limpieza)
        sku = random.randint(-1000, 0) if random.random() > 0.5 else 0
      
      # Registrar SKU usado (solo si es válido)
      if sku > 0:
        skus_usados.add(sku)
      
      productos_data.append({
        'Nombre': nombre,
        'Categoría': categoria,
        'PrecioCompra': precio_compra,
        'PrecioVenta': precio_venta,
        'Cantidad': cantidad,
        'SKU': sku,
        'Proveedor': proveedor
      })
    except Exception as e:
      logger.warning(f"Error al generar producto {i}: {str(e)}")
      continue
  
  # Generar ventas aleatorias
  fecha_inicio = datetime.now() - pd.Timedelta(days=730)  # Hace dos años
  
  for i in range(cantidad_ventas):
    try:
      # Seleccionar producto aleatorio de los generados
      if productos_data:
        producto_ref = random.choice(productos_data)
        producto_nombre = producto_ref['Nombre']
        sku = producto_ref['SKU']
        categoria = producto_ref['Categoría']
      else:
        producto_nombre = faker.word().capitalize()
        # Generar SKU aleatorio dentro del rango válido
        sku = random.randint(1, min(600000, cantidad_productos)) if cantidad_productos > 0 else random.randint(1, 600000)
        categoria = random.choice(categorias)
      
      # Fecha aleatoria en los últimos dos años
      dias_aleatorios = random.randint(0, 730)
      fecha_venta = fecha_inicio + pd.Timedelta(days=dias_aleatorios)
      fecha_venta_str = fecha_venta.strftime('%Y-%m-%d %H:%M:%S')
      
      # Cantidad con posibilidad de valores erróneos
      if random.random() > 0.15:
        cantidad = random.randint(1, 20)
      else:
        cantidad = random.randint(-5, -1) if random.random() > 0.5 else random.randint(1000, 5000)
      
      if cantidad <= 0:
        cantidad = 1
      
      # Precio con posibilidad de valores erróneos
      if productos_data and random.random() > 0.1:
        precio_unitario = round(producto_ref['PrecioVenta'] * random.uniform(0.8, 1.2), 2)
      else:
        precio_unitario = round(random.uniform(-100, 0), 2) if random.random() > 0.5 else round(random.uniform(1000, 50000), 2)
      
      if precio_unitario <= 0:
        precio_unitario = round(random.uniform(1000, 50000), 2)
      
      # Total con posibilidad de cálculo incorrecto
      if random.random() > 0.1:
        total = round(cantidad * precio_unitario, 2)
      else:
        total = round(cantidad * precio_unitario * random.uniform(0.5, 1.5), 2)  # Total incorrecto
      
      # Categoría con posibilidad de nulo
      if random.random() > 0.1:
        categoria_venta = categoria
      else:
        categoria_venta = None if random.random() > 0.5 else ""
      
      if not categoria_venta:
        categoria_venta = "Sin categoría"
      
      # Nombre de producto con posibilidad de nulo
      if random.random() > 0.1:
        nombre_venta = producto_nombre
      else:
        nombre_venta = None if random.random() > 0.5 else ""
      
      if not nombre_venta:
        nombre_venta = f"Producto_{random.randint(1000, 9999)}"
      
      ventas_data.append({
        'Producto': nombre_venta,
        'Categoría': categoria_venta,
        'Cantidad': cantidad,
        'Precio Unitario': precio_unitario,
        'Total': total,
        'Fecha/Hora': fecha_venta_str,
        'SKU': sku
      })
    except Exception as e:
      logger.warning(f"Error al generar venta {i}: {str(e)}")
      continue
  
  # Crear DataFrames y guardar en Excel
  try:
    df_productos = pd.DataFrame(productos_data)
    df_ventas = pd.DataFrame(ventas_data)
    
    # Generar nombres de archivo con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_productos = f"productos_aleatorios_{timestamp}.xlsx"
    archivo_ventas = f"ventas_aleatorias_{timestamp}.xlsx"
    
    # Guardar archivos Excel
    df_productos.to_excel(archivo_productos, index=False)
    df_ventas.to_excel(archivo_ventas, index=False)
    
    logger.info(f"Datos aleatorios generados: {len(productos_data)} productos en '{archivo_productos}', {len(ventas_data)} ventas en '{archivo_ventas}'")
    
    return {
      'archivo_productos': archivo_productos,
      'archivo_ventas': archivo_ventas,
      'productos_generados': len(productos_data),
      'ventas_generadas': len(ventas_data)
    }
  except Exception as e:
    logger.error(f"Error al guardar archivos Excel: {str(e)}")
    raise


# main ------------------------------------------------------------------------------------------
def main():
  logger.info("=== Iniciando aplicación de Gestión de Inventario ===")
  inventario_obj = inventario()
  logger.info("Inventario inicializado")
  registro_ventas = RegistroVentas(inventario_obj)
  logger.info("Sistema de ventas inicializado")
  # Cargar ventas desde archivo pickle
  registro_ventas.cargar_ventas()

  root = tk.Tk()
  root.title("Gestión de Inventario")
  root.geometry("2000x600")
  root.configure(bg="#f0f0f0")
  root.resizable(width=True, height=True)
  utl.centrar_ventana(root, 1600, 600)


  columns = ("Nombre", "Categoría", "Precio Venta", "Cantidad", "SKU", "Proveedor")
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
  categoria_filtro = "Todas"


  def refresh_tree():
    nonlocal current_page, page_size, categoria_filtro
    logger.debug(f"Refrescando árbol de productos - Página: {current_page}, Tamaño página: {page_size}, Categoría: {categoria_filtro}")
    # Clear current items
    for row in tree.get_children():
      tree.delete(row)

    # Obtain dataset length and slice for current page
    try:
      df = inventario_obj.get_dataframe()
      
      # Filtrar por categoría si no es "Todas"
      if categoria_filtro != "Todas":
        df = df[df['Categoría'] == categoria_filtro]
      
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
          values=(r['Nombre'], r.get('Categoría', 'Sin categoría'), f"${int(r['PrecioVenta'])}", int(r['Cantidad']), int(r['SKU']), r['Proveedor'])
        )
      update_pagination_info(start + 1, min(end, total), total)
    except Exception:
      # Fallback to the in-memory list if dataframe is not ready
      prods = inventario_obj.productos
      
      # Filtrar por categoría si no es "Todas"
      if categoria_filtro != "Todas":
        prods = [p for p in prods if getattr(p, 'categoria', 'Sin categoría') == categoria_filtro]
      
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
          values=(p.nombre, getattr(p, 'categoria', 'Sin categoría'), f"${int(p.precio_venta)}", p.cantidad, p.sku, p.proveedor)
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
    nonlocal current_page, categoria_filtro
    try:
      df = inventario_obj.get_dataframe()
      if categoria_filtro != "Todas":
        df = df[df['Categoría'] == categoria_filtro]
      total = len(df)
    except Exception:
      prods = inventario_obj.productos
      if categoria_filtro != "Todas":
        prods = [p for p in prods if getattr(p, 'categoria', 'Sin categoría') == categoria_filtro]
      total = len(prods)
    pages = max(1, (total + page_size - 1) // page_size)
    if current_page < pages:
      current_page += 1
      refresh_tree()

  def go_last():
    nonlocal current_page, categoria_filtro
    try:
      df = inventario_obj.get_dataframe()
      if categoria_filtro != "Todas":
        df = df[df['Categoría'] == categoria_filtro]
      total = len(df)
    except Exception:
      prods = inventario_obj.productos
      if categoria_filtro != "Todas":
        prods = [p for p in prods if getattr(p, 'categoria', 'Sin categoría') == categoria_filtro]
      total = len(prods)
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

  def cambiar_filtro_categoria(*_):
    nonlocal categoria_filtro, current_page
    categoria_filtro = var_categoria_filtro.get()
    current_page = 1  # Resetear a la primera página al cambiar el filtro
    logger.info(f"Filtro de categoría cambiado a: {categoria_filtro}")
    refresh_tree()

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

  # Filtro por categoría
  categorias_para_filtro = ["Todas"] + cargar_categorias()
  var_categoria_filtro = tk.StringVar(value="Todas")
  tk.Label(pagination_frame, text="Filtrar por categoría:").pack(side="right", padx=(4,2))
  combo_filtro_categoria = ttk.Combobox(pagination_frame, textvariable=var_categoria_filtro, values=categorias_para_filtro, state="readonly", width=15)
  combo_filtro_categoria.pack(side="right", padx=(2,8))
  combo_filtro_categoria.bind("<<ComboboxSelected>>", cambiar_filtro_categoria)

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
    form.geometry("380x320")
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

    tk.Label(form, text="Categoría:").grid(row=5, column=0, sticky="e", padx=6, pady=6)
    categorias_disponibles = cargar_categorias()
    combo_categoria = ttk.Combobox(form, values=categorias_disponibles, state="readonly", width=27)
    combo_categoria.grid(row=5, column=1, padx=6, pady=6)
    if categorias_disponibles:
      combo_categoria.current(0)

    def clear_fields():
      e_nombre.delete(0, tk.END)
      e_precio_compra.delete(0, tk.END)
      e_precio_venta.delete(0, tk.END)
      e_cantidad.delete(0, tk.END)
      e_proveedor.delete(0, tk.END)
      if categorias_disponibles:
        combo_categoria.current(0)
      e_nombre.focus_set()

    def add_and_option(close_after=False):
      try:
        nombre = e_nombre.get()
        precio_compra = e_precio_compra.get()
        precio_venta = e_precio_venta.get()
        cantidad = e_cantidad.get()
        proveedor = e_proveedor.get()
        categoria = combo_categoria.get() if combo_categoria.get() else "Sin categoría"
        producto = inventario_obj.agregar_producto_manual(
          nombre, precio_compra, precio_venta, cantidad, proveedor, categoria
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
    btn_frame.grid(row=6, column=0, columnspan=2, pady=10)

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

    tk.Label(form, text="Nueva categoría:").grid(row=4, column=0, sticky="e", padx=6, pady=6)
    categorias_disponibles_upd = cargar_categorias()
    combo_categoria_upd = ttk.Combobox(form, values=categorias_disponibles_upd, state="readonly", width=27)
    combo_categoria_upd.grid(row=4, column=1, padx=6, pady=6)
    if categorias_disponibles_upd:
      combo_categoria_upd.current(0)

    def clear_fields():
      e_nombre.delete(0, tk.END)
      e_precio_compra.delete(0, tk.END)
      e_precio_venta.delete(0, tk.END)
      e_cantidad.delete(0, tk.END)
      if categorias_disponibles_upd:
        combo_categoria_upd.current(0)
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
        nueva_cat = combo_categoria_upd.get() if combo_categoria_upd.get() else None
        producto = inventario_obj.actualizar_producto(nombre, nuevo_pc, nuevo_pv, nueva_cant, nueva_cat)
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
    btn_frame.grid(row=5, column=0, columnspan=2, pady=8)
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

  def gestionar_categorias():
    """Permite al administrador gestionar las categorías (solo admin)"""
    logger.info("Abriendo ventana de gestión de categorías")
    win_cat = tk.Toplevel(root)
    win_cat.title("Gestión de Categorías (Solo Administrador)")
    win_cat.geometry("500x400")
    win_cat.resizable(False, False)
    
    # Frame para lista de categorías
    frame_lista = tk.Frame(win_cat)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)
    
    tk.Label(frame_lista, text="Categorías disponibles:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    
    frame_listbox = tk.Frame(frame_lista)
    frame_listbox.pack(fill="both", expand=True)
    
    listbox_cat = tk.Listbox(frame_listbox, height=12, font=("Arial", 9))
    listbox_cat.pack(side="left", fill="both", expand=True)
    
    scrollbar_cat = tk.Scrollbar(frame_listbox, orient="vertical", command=listbox_cat.yview)
    scrollbar_cat.pack(side="right", fill="y")
    listbox_cat.config(yscrollcommand=scrollbar_cat.set)
    
    def actualizar_lista():
      categorias = cargar_categorias()
      listbox_cat.delete(0, tk.END)
      for cat in categorias:
        listbox_cat.insert(tk.END, cat)
    
    actualizar_lista()
    
    # Frame para agregar nueva categoría
    frame_agregar = tk.Frame(win_cat)
    frame_agregar.pack(fill="x", padx=10, pady=5)
    
    tk.Label(frame_agregar, text="Nueva categoría:").pack(side="left", padx=5)
    e_nueva_cat = tk.Entry(frame_agregar, width=25)
    e_nueva_cat.pack(side="left", padx=5)
    
    def agregar_categoria():
      nueva_cat = e_nueva_cat.get().strip()
      if not nueva_cat:
        messagebox.showwarning("Aviso", "Ingrese un nombre para la categoría.")
        return
      categorias = cargar_categorias()
      if nueva_cat in categorias:
        messagebox.showwarning("Aviso", f"La categoría '{nueva_cat}' ya existe.")
        return
      categorias.append(nueva_cat)
      guardar_categorias(categorias)
      actualizar_lista()
      e_nueva_cat.delete(0, tk.END)
      logger.info(f"Categoría agregada por admin: {nueva_cat}")
      # Actualizar el combobox del filtro
      categorias_para_filtro = ["Todas"] + cargar_categorias()
      combo_filtro_categoria['values'] = categorias_para_filtro
      messagebox.showinfo("Éxito", f"Categoría '{nueva_cat}' agregada.")
    
    btn_agregar_cat = tk.Button(frame_agregar, text="Agregar", command=agregar_categoria, bg="#4CAF50", fg="white")
    btn_agregar_cat.pack(side="left", padx=5)
    
    # Frame para eliminar categoría
    frame_eliminar = tk.Frame(win_cat)
    frame_eliminar.pack(fill="x", padx=10, pady=5)
    
    def eliminar_categoria():
      seleccion = listbox_cat.curselection()
      if not seleccion:
        messagebox.showwarning("Aviso", "Seleccione una categoría para eliminar.")
        return
      categoria_sel = listbox_cat.get(seleccion[0])
      if categoria_sel == "Sin categoría":
        messagebox.showwarning("Aviso", "No se puede eliminar la categoría 'Sin categoría'.")
        return
      respuesta = messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la categoría '{categoria_sel}'?")
      if respuesta:
        categorias = cargar_categorias()
        if categoria_sel in categorias:
          categorias.remove(categoria_sel)
          guardar_categorias(categorias)
          actualizar_lista()
          logger.info(f"Categoría eliminada por admin: {categoria_sel}")
          # Actualizar el combobox del filtro
          categorias_para_filtro = ["Todas"] + cargar_categorias()
          combo_filtro_categoria['values'] = categorias_para_filtro
          # Si la categoría eliminada era la seleccionada en el filtro, cambiar a "Todas"
          if var_categoria_filtro.get() == categoria_sel:
            var_categoria_filtro.set("Todas")
            cambiar_filtro_categoria()
          messagebox.showinfo("Éxito", f"Categoría '{categoria_sel}' eliminada.")
    
    btn_eliminar_cat = tk.Button(frame_eliminar, text="Eliminar categoría seleccionada", command=eliminar_categoria, bg="#D80000", fg="white")
    btn_eliminar_cat.pack(side="left", padx=5)
    
    btn_cerrar_cat = tk.Button(frame_eliminar, text="Cerrar", command=win_cat.destroy)
    btn_cerrar_cat.pack(side="right", padx=5)

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
        # Actualizar años disponibles en el filtro
        df_temp = registro_ventas.get_dataframe()
        anos_disponibles = ["Todos"]
        if not df_temp.empty:
          try:
            df_temp['Fecha'] = pd.to_datetime(df_temp['Fecha/Hora'])
            anos_unicos = sorted(df_temp['Fecha'].dt.year.unique(), reverse=True)
            anos_disponibles.extend([str(a) for a in anos_unicos])
            combo_ano['values'] = anos_disponibles
          except:
            pass
        refresh_tree_ventas()
        e_producto.delete(0, tk.END)
        e_cantidad.delete(0, tk.END)
        e_precio.delete(0, tk.END)
        lbl_total.config(text="Total: $0")
        e_producto.focus_set()
      except Exception as e:
        logger.error(f"Error al registrar venta: {str(e)}")
        messagebox.showerror("Error", str(e))
        e_producto.delete(0, tk.END)
        e_cantidad.delete(0, tk.END)
        e_precio.delete(0, tk.END)
        lbl_total.config(text="Total: $0")
        e_producto.focus_set()
        return
    
    btn_registrar = tk.Button(frame_form, text="Registrar Venta", command=registrar_venta, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
    btn_registrar.grid(row=0, column=7, padx=10, pady=5)
    
    # Frame para filtros de fecha
    frame_filtros = tk.Frame(ventana_ventas, bg="#e0e0e0", relief="raised", bd=2)
    frame_filtros.pack(fill="x", padx=10, pady=5)
    
    tk.Label(frame_filtros, text="Filtrar ventas por fecha:", font=("Arial", 10, "bold"), bg="#e0e0e0").pack(side="left", padx=5, pady=5)
    
    # Filtro por año
    tk.Label(frame_filtros, text="Año:", bg="#e0e0e0").pack(side="left", padx=5)
    var_ano = tk.StringVar(value="Todos")
    # Obtener años únicos de las ventas
    df_temp = registro_ventas.get_dataframe()
    anos_disponibles = ["Todos"]
    if not df_temp.empty:
      try:
        df_temp['Fecha'] = pd.to_datetime(df_temp['Fecha/Hora'])
        anos_unicos = sorted(df_temp['Fecha'].dt.year.unique(), reverse=True)
        anos_disponibles.extend([str(a) for a in anos_unicos])
      except:
        pass
    combo_ano = ttk.Combobox(frame_filtros, textvariable=var_ano, values=anos_disponibles, state="readonly", width=10)
    combo_ano.pack(side="left", padx=5)
    
    # Filtro por mes
    tk.Label(frame_filtros, text="Mes:", bg="#e0e0e0").pack(side="left", padx=5)
    var_mes = tk.StringVar(value="Todos")
    meses_disponibles = ["Todos", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    combo_mes = ttk.Combobox(frame_filtros, textvariable=var_mes, values=meses_disponibles, state="readonly", width=10)
    combo_mes.pack(side="left", padx=5)
    
    # Filtro por día
    tk.Label(frame_filtros, text="Día:", bg="#e0e0e0").pack(side="left", padx=5)
    var_dia = tk.StringVar(value="Todos")
    dias_disponibles = ["Todos"] + [f"{i:02d}" for i in range(1, 32)]
    combo_dia = ttk.Combobox(frame_filtros, textvariable=var_dia, values=dias_disponibles, state="readonly", width=10)
    combo_dia.pack(side="left", padx=5)
    
    # Botón para limpiar filtros
    btn_limpiar_filtros = tk.Button(frame_filtros, text="Limpiar Filtros", command=lambda: limpiar_filtros(), bg="#FF9800", fg="white", font=("Arial", 9))
    btn_limpiar_filtros.pack(side="left", padx=10, pady=5)
    
    def limpiar_filtros():
      var_ano.set("Todos")
      var_mes.set("Todos")
      var_dia.set("Todos")
      refresh_tree_ventas()
    
    # Frame para tabla de ventas
    frame_tabla = tk.Frame(ventana_ventas)
    frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)
    
    columns_ventas = ("Producto", "Categoría", "Cantidad", "Precio Unitario", "Total", "Fecha/Hora", "SKU")
    tree_ventas = ttk.Treeview(frame_tabla, columns=columns_ventas, show="headings", height=20)
    # Configurar anchos de columnas
    tree_ventas.heading("Producto", text="Producto")
    tree_ventas.column("Producto", anchor="center", width=150)
    tree_ventas.heading("Categoría", text="Categoría")
    tree_ventas.column("Categoría", anchor="center", width=120)
    tree_ventas.heading("Cantidad", text="Cantidad")
    tree_ventas.column("Cantidad", anchor="center", width=80)
    tree_ventas.heading("Precio Unitario", text="Precio Unitario")
    tree_ventas.column("Precio Unitario", anchor="center", width=120)
    tree_ventas.heading("Total", text="Total")
    tree_ventas.column("Total", anchor="center", width=100)
    tree_ventas.heading("Fecha/Hora", text="Fecha/Hora")
    tree_ventas.column("Fecha/Hora", anchor="center", width=150)
    tree_ventas.heading("SKU", text="SKU")
    tree_ventas.column("SKU", anchor="center", width=80)
    
    scrollbar_ventas = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree_ventas.yview)
    tree_ventas.configure(yscrollcommand=scrollbar_ventas.set)
    
    tree_ventas.pack(side="left", fill="both", expand=True)
    scrollbar_ventas.pack(side="right", fill="y")
    
    def refresh_tree_ventas():
      for row in tree_ventas.get_children():
        tree_ventas.delete(row)
      df_ventas = registro_ventas.get_dataframe().copy()
      
      # Aplicar filtros de fecha
      if not df_ventas.empty:
        try:
          df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha/Hora'])
          
          # Filtro por año
          ano_filtro = var_ano.get()
          if ano_filtro != "Todos":
            df_ventas = df_ventas[df_ventas['Fecha'].dt.year == int(ano_filtro)]
          
          # Filtro por mes
          mes_filtro = var_mes.get()
          if mes_filtro != "Todos":
            df_ventas = df_ventas[df_ventas['Fecha'].dt.month == int(mes_filtro)]
          
          # Filtro por día
          dia_filtro = var_dia.get()
          if dia_filtro != "Todos":
            df_ventas = df_ventas[df_ventas['Fecha'].dt.day == int(dia_filtro)]
        except Exception as e:
          logger.error(f"Error al aplicar filtros de fecha: {str(e)}")
      
      # Mostrar ventas filtradas
      for _, r in df_ventas.iterrows():
        tree_ventas.insert("", "end", values=(
          r['Producto'], 
          r.get('Categoría', 'Sin categoría'),
          int(r['Cantidad']), 
          f"${int(r['Precio Unitario'])}", 
          f"${int(r['Total'])}", 
          r['Fecha/Hora'], 
          int(r['SKU'])
        ))
      
      # Actualizar totales (solo de las ventas filtradas)
      total_ventas_filtradas = df_ventas['Total'].sum() if not df_ventas.empty else 0
      total_registros = len(df_ventas)
      lbl_total_ventas.config(text=f"Total de ventas (filtradas): ${int(total_ventas_filtradas)} | Registros: {total_registros}")
    
    # Vincular eventos de cambio en los filtros
    combo_ano.bind("<<ComboboxSelected>>", lambda e: refresh_tree_ventas())
    combo_mes.bind("<<ComboboxSelected>>", lambda e: refresh_tree_ventas())
    combo_dia.bind("<<ComboboxSelected>>", lambda e: refresh_tree_ventas())
    
    # Frame inferior para totales
    frame_totales = tk.Frame(ventana_ventas)
    frame_totales.pack(fill="x", padx=10, pady=10)
    
    lbl_total_ventas = tk.Label(frame_totales, text="Total de ventas: $0", font=("Arial", 12, "bold"))
    lbl_total_ventas.pack(side="left", padx=10)
    
    def importar_ventas_excel():
      """Importa ventas desde un archivo Excel"""
      ruta_archivo = filedialog.askopenfilename(
        title="Seleccionar archivo Excel de ventas",
        filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
      )
      if not ruta_archivo:
        return
      
      try:
        resultado = importar_ventas_desde_excel(registro_ventas, ruta_archivo)
        refresh_tree_ventas()
        messagebox.showinfo("Importación Completada",
          f"Importación de ventas completada:\n\n"
          f"- Ventas importadas: {resultado['importadas']}\n"
          f"- Ventas con errores: {resultado['errores']}")
        logger.info(f"Importación de ventas completada: {resultado}")
      except Exception as e:
        logger.error(f"Error al importar ventas: {str(e)}")
        messagebox.showerror("Error", f"Error al importar ventas: {str(e)}")
    
    btn_importar_ventas = tk.Button(frame_totales, text="Importar Ventas desde Excel", command=importar_ventas_excel, bg="#673AB7", fg="white", font=("Arial", 10, "bold"))
    btn_importar_ventas.pack(side="right", padx=10)
    
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

  def mostrar_graficas():
    """Muestra una ventana con opciones para generar diferentes gráficas de inventario y ventas"""
    logger.info("Abriendo ventana de gráficas")
    ventana_graficas = tk.Toplevel(root)
    ventana_graficas.title("Gráficas de Inventario y Ventas")
    ventana_graficas.geometry("800x600")
    ventana_graficas.configure(bg="#f0f0f0")
    
    # Frame para selección de gráficas
    frame_seleccion = tk.Frame(ventana_graficas, bg="#f0f0f0")
    frame_seleccion.pack(fill="x", padx=10, pady=10)
    
    tk.Label(frame_seleccion, text="Seleccione el tipo de gráfica:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)
    
    # Frame para botones de gráficas de inventario
    frame_inventario = tk.LabelFrame(frame_seleccion, text="Gráficas de Inventario", font=("Arial", 10, "bold"), bg="#f0f0f0")
    frame_inventario.pack(fill="x", padx=10, pady=5)
    
    def grafica_productos_por_categoria():
      """Gráfica de distribución de productos por categoría"""
      try:
        df = inventario_obj.get_dataframe()
        if df.empty:
          messagebox.showwarning("Aviso", "No hay productos en el inventario para graficar.")
          return
        
        categoria_counts = df['Categoría'].value_counts()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(categoria_counts.values, labels=categoria_counts.index, autopct='%1.1f%%', startangle=90)
        ax.set_title('Distribución de Productos por Categoría', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        ventana_graf = tk.Toplevel(ventana_graficas)
        ventana_graf.title("Productos por Categoría")
        canvas = FigureCanvasTkAgg(fig, ventana_graf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        logger.info("Gráfica de productos por categoría generada")
      except Exception as e:
        logger.error(f"Error al generar gráfica de productos por categoría: {str(e)}")
        messagebox.showerror("Error", f"Error al generar gráfica: {str(e)}")
    
    def grafica_stock_por_categoria():
      """Gráfica de stock total por categoría"""
      try:
        df = inventario_obj.get_dataframe()
        if df.empty:
          messagebox.showwarning("Aviso", "No hay productos en el inventario para graficar.")
          return
        
        stock_por_categoria = df.groupby('Categoría')['Cantidad'].sum().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(stock_por_categoria.index, stock_por_categoria.values, color='steelblue')
        ax.set_title('Stock Total por Categoría', fontsize=14, fontweight='bold')
        ax.set_xlabel('Categoría', fontsize=12)
        ax.set_ylabel('Cantidad Total', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        
        ventana_graf = tk.Toplevel(ventana_graficas)
        ventana_graf.title("Stock por Categoría")
        canvas = FigureCanvasTkAgg(fig, ventana_graf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        logger.info("Gráfica de stock por categoría generada")
      except Exception as e:
        logger.error(f"Error al generar gráfica de stock por categoría: {str(e)}")
        messagebox.showerror("Error", f"Error al generar gráfica: {str(e)}")
    
    def grafica_valor_por_categoria():
      """Gráfica de valor del inventario por categoría"""
      try:
        df = inventario_obj.get_dataframe()
        if df.empty:
          messagebox.showwarning("Aviso", "No hay productos en el inventario para graficar.")
          return
        
        df['ValorTotal'] = df['PrecioVenta'] * df['Cantidad']
        valor_por_categoria = df.groupby('Categoría')['ValorTotal'].sum().sort_values(ascending=False)
        
        # Convertir valores a millones de pesos
        valor_por_categoria_millones = valor_por_categoria / 1000000
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(valor_por_categoria_millones.index, valor_por_categoria_millones.values, color='green')
        ax.set_title('Valor del Inventario por Categoría', fontsize=14, fontweight='bold')
        ax.set_xlabel('Categoría', fontsize=12)
        ax.set_ylabel('Valor Total (Millones de $)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        # Formatear el eje Y 
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.2f}'))
        plt.tight_layout()
        
        ventana_graf = tk.Toplevel(ventana_graficas)
        ventana_graf.title("Valor por Categoría")
        canvas = FigureCanvasTkAgg(fig, ventana_graf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        logger.info("Gráfica de valor por categoría generada")
      except Exception as e:
        logger.error(f"Error al generar gráfica de valor por categoría: {str(e)}")
        messagebox.showerror("Error", f"Error al generar gráfica: {str(e)}")
    
    def grafica_top_productos_stock():
      """Gráfica de top 10 productos con mayor stock"""
      try:
        df = inventario_obj.get_dataframe()
        if df.empty:
          messagebox.showwarning("Aviso", "No hay productos en el inventario para graficar.")
          return
        
        top_productos = df.nlargest(10, 'Cantidad')[['Nombre', 'Cantidad']]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.barh(top_productos['Nombre'], top_productos['Cantidad'], color='orange')
        ax.set_title('Top 10 Productos con Mayor Stock', fontsize=14, fontweight='bold')
        ax.set_xlabel('Cantidad', fontsize=12)
        ax.set_ylabel('Producto', fontsize=12)
        plt.tight_layout()
        
        ventana_graf = tk.Toplevel(ventana_graficas)
        ventana_graf.title("Top Productos por Stock")
        canvas = FigureCanvasTkAgg(fig, ventana_graf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        logger.info("Gráfica de top productos por stock generada")
      except Exception as e:
        logger.error(f"Error al generar gráfica de top productos: {str(e)}")
        messagebox.showerror("Error", f"Error al generar gráfica: {str(e)}")
    
    tk.Button(frame_inventario, text="Productos por Categoría (Pastel)", command=grafica_productos_por_categoria, 
              bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=30).pack(pady=3, padx=5)
    tk.Button(frame_inventario, text="Stock por Categoría", command=grafica_stock_por_categoria, 
              bg="#2196F3", fg="white", font=("Arial", 9, "bold"), width=30).pack(pady=3, padx=5)
    tk.Button(frame_inventario, text="Valor del Inventario por Categoría", command=grafica_valor_por_categoria, 
              bg="#FF9800", fg="white", font=("Arial", 9, "bold"), width=30).pack(pady=3, padx=5)
    tk.Button(frame_inventario, text="Top 10 Productos con Mayor Stock", command=grafica_top_productos_stock, 
              bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), width=30).pack(pady=3, padx=5)
    
    # Frame para botones de gráficas de ventas
    frame_ventas = tk.LabelFrame(frame_seleccion, text="Gráficas de Ventas", font=("Arial", 10, "bold"), bg="#f0f0f0")
    frame_ventas.pack(fill="x", padx=10, pady=5)
    
    def grafica_ventas_por_producto():
      """Gráfica de ventas totales por producto"""
      try:
        df_ventas = registro_ventas.get_dataframe()
        if df_ventas.empty:
          messagebox.showwarning("Aviso", "No hay ventas registradas para graficar.")
          return
        
        ventas_por_producto = df_ventas.groupby('Producto')['Total'].sum().sort_values(ascending=False).head(10)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(ventas_por_producto.index, ventas_por_producto.values, color='coral')
        ax.set_title('Top 10 Productos por Ventas Totales', fontsize=14, fontweight='bold')
        ax.set_xlabel('Producto', fontsize=12)
        ax.set_ylabel('Total de Ventas ($)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        
        ventana_graf = tk.Toplevel(ventana_graficas)
        ventana_graf.title("Ventas por Producto")
        canvas = FigureCanvasTkAgg(fig, ventana_graf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        logger.info("Gráfica de ventas por producto generada")
      except Exception as e:
        logger.error(f"Error al generar gráfica de ventas por producto: {str(e)}")
        messagebox.showerror("Error", f"Error al generar gráfica: {str(e)}")
    
    def grafica_ventas_por_categoria():
      """Gráfica de ventas totales por categoría"""
      try:
        df_ventas = registro_ventas.get_dataframe()
        if df_ventas.empty:
          messagebox.showwarning("Aviso", "No hay ventas registradas para graficar.")
          return
        
        ventas_por_categoria = df_ventas.groupby('Categoría')['Total'].sum().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(ventas_por_categoria.index, ventas_por_categoria.values, color='teal')
        ax.set_title('Ventas Totales por Categoría', fontsize=14, fontweight='bold')
        ax.set_xlabel('Categoría', fontsize=12)
        ax.set_ylabel('Total de Ventas ($)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        
        ventana_graf = tk.Toplevel(ventana_graficas)
        ventana_graf.title("Ventas por Categoría")
        canvas = FigureCanvasTkAgg(fig, ventana_graf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        logger.info("Gráfica de ventas por categoría generada")
      except Exception as e:
        logger.error(f"Error al generar gráfica de ventas por categoría: {str(e)}")
        messagebox.showerror("Error", f"Error al generar gráfica: {str(e)}")
    
    def grafica_ventas_en_tiempo():
      """Gráfica de ventas en el tiempo"""
      try:
        df_ventas = registro_ventas.get_dataframe()
        if df_ventas.empty:
          messagebox.showwarning("Aviso", "No hay ventas registradas para graficar.")
          return
        
        df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha/Hora'])
        df_ventas['Fecha_Formato'] = df_ventas['Fecha'].dt.date
        ventas_por_fecha = df_ventas.groupby('Fecha_Formato')['Total'].sum().sort_index()
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(ventas_por_fecha.index, ventas_por_fecha.values, marker='o', linewidth=2, markersize=4, color='purple')
        ax.set_title('Evolución de Ventas en el Tiempo', fontsize=14, fontweight='bold')
        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel('Total de Ventas ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        
        ventana_graf = tk.Toplevel(ventana_graficas)
        ventana_graf.title("Ventas en el Tiempo")
        canvas = FigureCanvasTkAgg(fig, ventana_graf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        logger.info("Gráfica de ventas en el tiempo generada")
      except Exception as e:
        logger.error(f"Error al generar gráfica de ventas en el tiempo: {str(e)}")
        messagebox.showerror("Error", f"Error al generar gráfica: {str(e)}")
    
    def grafica_cantidad_vendida_por_producto():
      """Gráfica de cantidad total vendida por producto"""
      try:
        df_ventas = registro_ventas.get_dataframe()
        if df_ventas.empty:
          messagebox.showwarning("Aviso", "No hay ventas registradas para graficar.")
          return
        
        cantidad_por_producto = df_ventas.groupby('Producto')['Cantidad'].sum().sort_values(ascending=False).head(10)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.barh(cantidad_por_producto.index, cantidad_por_producto.values, color='indigo')
        ax.set_title('Top 10 Productos por Cantidad Vendida', fontsize=14, fontweight='bold')
        ax.set_xlabel('Cantidad Total Vendida', fontsize=12)
        ax.set_ylabel('Producto', fontsize=12)
        plt.tight_layout()
        
        ventana_graf = tk.Toplevel(ventana_graficas)
        ventana_graf.title("Cantidad Vendida por Producto")
        canvas = FigureCanvasTkAgg(fig, ventana_graf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        logger.info("Gráfica de cantidad vendida por producto generada")
      except Exception as e:
        logger.error(f"Error al generar gráfica de cantidad vendida: {str(e)}")
        messagebox.showerror("Error", f"Error al generar gráfica: {str(e)}")
    
    tk.Button(frame_ventas, text="Top 10 Productos por Ventas Totales", command=grafica_ventas_por_producto, 
              bg="#E91E63", fg="white", font=("Arial", 9, "bold"), width=30).pack(pady=3, padx=5)
    tk.Button(frame_ventas, text="Ventas por Categoría", command=grafica_ventas_por_categoria, 
              bg="#00BCD4", fg="white", font=("Arial", 9, "bold"), width=30).pack(pady=3, padx=5)
    tk.Button(frame_ventas, text="Evolución de Ventas en el Tiempo", command=grafica_ventas_en_tiempo, 
              bg="#673AB7", fg="white", font=("Arial", 9, "bold"), width=30).pack(pady=3, padx=5)
    tk.Button(frame_ventas, text="Top 10 Productos por Cantidad Vendida", command=grafica_cantidad_vendida_por_producto, 
              bg="#F44336", fg="white", font=("Arial", 9, "bold"), width=30).pack(pady=3, padx=5)
    
    # Botón para cerrar
    btn_cerrar = tk.Button(frame_seleccion, text="Cerrar", command=ventana_graficas.destroy, 
                          bg="#757575", fg="white", font=("Arial", 10, "bold"), width=20)
    btn_cerrar.pack(pady=15)

  def analisis_predictivo_ventas():
    """Análisis predictivo de ventas: productos más/menos vendidos y patrones temporales"""
    logger.info("Abriendo ventana de análisis predictivo de ventas")
    
    df_ventas = registro_ventas.get_dataframe()
    if df_ventas.empty:
      messagebox.showwarning("Aviso", "No hay ventas registradas para realizar el análisis.")
      return
    
    try:
      df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha/Hora'])
    except Exception as e:
      logger.error(f"Error al procesar fechas: {str(e)}")
      messagebox.showerror("Error", f"Error al procesar las fechas de las ventas: {str(e)}")
      return
    
    ventana_analisis = tk.Toplevel(root)
    ventana_analisis.title("Análisis Predictivo de Ventas")
    ventana_analisis.geometry("1200x700")
    ventana_analisis.configure(bg="#f0f0f0")
    
    # Frame principal con scroll
    canvas_frame = tk.Canvas(ventana_analisis, bg="#f0f0f0")
    scrollbar = tk.Scrollbar(ventana_analisis, orient="vertical", command=canvas_frame.yview)
    scrollable_frame = tk.Frame(canvas_frame, bg="#f0f0f0")
    
    scrollable_frame.bind(
      "<Configure>",
      lambda e: canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))
    )
    
    canvas_frame.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas_frame.configure(yscrollcommand=scrollbar.set)
    
    # Título
    tk.Label(scrollable_frame, text="Análisis Predictivo de Ventas", 
             font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=15)
    
    # ========== ANÁLISIS 1: PRODUCTOS MÁS VENDIDOS ==========
    frame_top = tk.LabelFrame(scrollable_frame, text="Productos Más Vendidos", 
                              font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
    frame_top.pack(fill="x", padx=15, pady=10)
    
    # Por cantidad
    ventas_por_producto_cantidad = df_ventas.groupby('Producto')['Cantidad'].sum().sort_values(ascending=False).head(10)
    # Por valor total
    ventas_por_producto_valor = df_ventas.groupby('Producto')['Total'].sum().sort_values(ascending=False).head(10)
    
    tk.Label(frame_top, text="Top 10 Productos por Cantidad Vendida:", 
             font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=5)
    texto_top_cantidad = "\n".join([f"{i+1}. {prod}: {int(cant)} unidades" 
                                     for i, (prod, cant) in enumerate(ventas_por_producto_cantidad.items())])
    tk.Label(frame_top, text=texto_top_cantidad, font=("Arial", 9), bg="#f0f0f0", 
             justify="left").pack(anchor="w", padx=20, pady=5)
    
    tk.Label(frame_top, text="Top 10 Productos por Valor de Ventas:", 
             font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(10, 5))
    texto_top_valor = "\n".join([f"{i+1}. {prod}: ${int(valor):,}" 
                                  for i, (prod, valor) in enumerate(ventas_por_producto_valor.items())])
    tk.Label(frame_top, text=texto_top_valor, font=("Arial", 9), bg="#f0f0f0", 
             justify="left").pack(anchor="w", padx=20, pady=5)
    
    # ========== ANÁLISIS 2: PRODUCTOS MENOS VENDIDOS ==========
    frame_bottom = tk.LabelFrame(scrollable_frame, text="Productos Menos Vendidos", 
                                 font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
    frame_bottom.pack(fill="x", padx=15, pady=10)
    
    ventas_por_producto_cantidad_min = df_ventas.groupby('Producto')['Cantidad'].sum().sort_values(ascending=True).head(10)
    ventas_por_producto_valor_min = df_ventas.groupby('Producto')['Total'].sum().sort_values(ascending=True).head(10)
    
    tk.Label(frame_bottom, text="10 Productos con Menor Cantidad Vendida:", 
             font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=5)
    texto_bottom_cantidad = "\n".join([f"{i+1}. {prod}: {int(cant)} unidades" 
                                        for i, (prod, cant) in enumerate(ventas_por_producto_cantidad_min.items())])
    tk.Label(frame_bottom, text=texto_bottom_cantidad, font=("Arial", 9), bg="#f0f0f0", 
             justify="left").pack(anchor="w", padx=20, pady=5)
    
    tk.Label(frame_bottom, text="10 Productos con Menor Valor de Ventas:", 
             font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(10, 5))
    texto_bottom_valor = "\n".join([f"{i+1}. {prod}: ${int(valor):,}" 
                                     for i, (prod, valor) in enumerate(ventas_por_producto_valor_min.items())])
    tk.Label(frame_bottom, text=texto_bottom_valor, font=("Arial", 9), bg="#f0f0f0", 
             justify="left").pack(anchor="w", padx=20, pady=5)
    
    # ========== ANÁLISIS 3: PATRONES TEMPORALES ==========
    frame_temporal = tk.LabelFrame(scrollable_frame, text="Análisis Temporal de Ventas", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
    frame_temporal.pack(fill="x", padx=15, pady=10)
    
    # Por mes
    df_ventas['Mes'] = df_ventas['Fecha'].dt.month
    df_ventas['Año'] = df_ventas['Fecha'].dt.year
    df_ventas['Dia_Semana'] = df_ventas['Fecha'].dt.day_name()
    
    meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                   'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    ventas_por_mes_ordenado = df_ventas.groupby('Mes')['Total'].sum()
    # Reindexar con nombres de meses en español
    nuevo_indice = [meses_orden[m-1] for m in ventas_por_mes_ordenado.index]
    ventas_por_mes_ordenado.index = nuevo_indice
    
    tk.Label(frame_temporal, text="Ventas por Mes (orden cronológico):", 
             font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=5)
    texto_meses = "\n".join([f"{mes}: ${int(valor):,}" 
                              for mes, valor in ventas_por_mes_ordenado.items()])
    tk.Label(frame_temporal, text=texto_meses, font=("Arial", 9), bg="#f0f0f0", 
             justify="left").pack(anchor="w", padx=20, pady=5)
    
    # Mejores y peores meses
    mejor_mes = ventas_por_mes_ordenado.idxmax()
    peor_mes = ventas_por_mes_ordenado.idxmin()
    tk.Label(frame_temporal, 
             text=f"Mejor mes: {mejor_mes} (${int(ventas_por_mes_ordenado[mejor_mes]):,}) | "
                  f"Peor mes: {peor_mes} (${int(ventas_por_mes_ordenado[peor_mes]):,})", 
             font=("Arial", 9, "bold"), bg="#f0f0f0", fg="#2E7D32").pack(anchor="w", padx=20, pady=5)
    
    # Por día de la semana
    orden_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    nombres_dias = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 
                    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
    ventas_por_dia = df_ventas.groupby('Dia_Semana')['Total'].sum()
    ventas_por_dia_ordenado = ventas_por_dia.reindex([d for d in orden_dias if d in ventas_por_dia.index])
    
    tk.Label(frame_temporal, text="Ventas por Día de la Semana:", 
             font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(10, 5))
    texto_dias = "\n".join([f"{nombres_dias.get(dia, dia)}: ${int(valor):,}" 
                             for dia, valor in ventas_por_dia_ordenado.items()])
    tk.Label(frame_temporal, text=texto_dias, font=("Arial", 9), bg="#f0f0f0", 
             justify="left").pack(anchor="w", padx=20, pady=5)
    
    # ========== ANÁLISIS 4: PRODUCTOS POR PERÍODO ==========
    frame_periodo = tk.LabelFrame(scrollable_frame, text="Productos por Período del Año", 
                                  font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
    frame_periodo.pack(fill="x", padx=15, pady=10)
    
    # Definir estaciones
    def obtener_estacion(mes):
      if mes in [12, 1, 2]:
        return "Invierno"
      elif mes in [3, 4, 5]:
        return "Primavera"
      elif mes in [6, 7, 8]:
        return "Verano"
      else:
        return "Otoño"
    
    df_ventas['Estacion'] = df_ventas['Mes'].apply(obtener_estacion)
    
    # Productos más vendidos por estación
    estaciones = ['Primavera', 'Verano', 'Otoño', 'Invierno']
    texto_estaciones = ""
    for estacion in estaciones:
      df_estacion = df_ventas[df_ventas['Estacion'] == estacion]
      if not df_estacion.empty:
        top_productos_estacion = df_estacion.groupby('Producto')['Cantidad'].sum().sort_values(ascending=False).head(5)
        texto_estaciones += f"\n{estacion}:\n"
        texto_estaciones += "\n".join([f"  • {prod}: {int(cant)} unidades" 
                                        for prod, cant in top_productos_estacion.items()])
        texto_estaciones += "\n"
    
    tk.Label(frame_periodo, text="Top 5 Productos por Estación:", 
             font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=5)
    tk.Label(frame_periodo, text=texto_estaciones, font=("Arial", 9), bg="#f0f0f0", 
             justify="left").pack(anchor="w", padx=20, pady=5)
    
    # ========== ANÁLISIS 5: PREDICCIONES ==========
    frame_prediccion = tk.LabelFrame(scrollable_frame, text="🔮 Predicciones y Tendencias", 
                                     font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
    frame_prediccion.pack(fill="x", padx=15, pady=10)
    
    # Predicción simple basada en tendencia mensual
    if len(ventas_por_mes_ordenado) >= 2:
      # Calcular tendencia
      valores = ventas_por_mes_ordenado.values
      if len(valores) > 1:
        tendencia = (valores[-1] - valores[0]) / len(valores) if len(valores) > 1 else 0
        ultimo_valor = valores[-1]
        prediccion_proximo_mes = ultimo_valor + tendencia
        
        tk.Label(frame_prediccion, text="Predicción para el Próximo Mes:", 
                 font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=5)
        tk.Label(frame_prediccion, 
                 text=f"Basado en la tendencia histórica, se esperan ventas de aproximadamente: ${int(prediccion_proximo_mes):,}", 
                 font=("Arial", 9), bg="#f0f0f0", fg="#1976D2").pack(anchor="w", padx=20, pady=5)
    
    # Productos con tendencia creciente
    productos_tendencia = {}
    for producto in df_ventas['Producto'].unique():
      df_producto = df_ventas[df_ventas['Producto'] == producto].sort_values('Fecha')
      if len(df_producto) >= 3:
        # Dividir en dos períodos
        mitad = len(df_producto) // 2
        ventas_primera_mitad = df_producto.iloc[:mitad]['Cantidad'].sum()
        ventas_segunda_mitad = df_producto.iloc[mitad:]['Cantidad'].sum()
        if ventas_segunda_mitad > ventas_primera_mitad * 1.1:  # 10% de crecimiento
          productos_tendencia[producto] = ((ventas_segunda_mitad - ventas_primera_mitad) / ventas_primera_mitad) * 100
    
    if productos_tendencia:
      productos_crecientes = sorted(productos_tendencia.items(), key=lambda x: x[1], reverse=True)[:5]
      tk.Label(frame_prediccion, text="Productos con Tendencia Creciente:", 
               font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(10, 5))
      texto_crecientes = "\n".join([f"  • {prod}: +{crecimiento:.1f}% de crecimiento" 
                                     for prod, crecimiento in productos_crecientes])
      tk.Label(frame_prediccion, text=texto_crecientes, font=("Arial", 9), bg="#f0f0f0", 
               justify="left", fg="#2E7D32").pack(anchor="w", padx=20, pady=5)
    
    # Botones para gráficas
    frame_botones_graf = tk.Frame(scrollable_frame, bg="#f0f0f0")
    frame_botones_graf.pack(fill="x", padx=15, pady=15)
    
    def mostrar_grafica_temporal():
      """Gráfica de ventas por mes"""
      fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
      
      # Gráfica de ventas por mes
      ax1.bar(ventas_por_mes_ordenado.index, ventas_por_mes_ordenado.values, color='steelblue')
      ax1.set_title('Ventas Totales por Mes', fontsize=14, fontweight='bold')
      ax1.set_xlabel('Mes', fontsize=12)
      ax1.set_ylabel('Ventas Totales ($)', fontsize=12)
      ax1.tick_params(axis='x', rotation=45)
      ax1.grid(True, alpha=0.3, axis='y')
      
      # Gráfica de ventas por día de la semana
      nombres_dias_esp = [nombres_dias.get(dia, dia) for dia in ventas_por_dia_ordenado.index]
      ax2.bar(nombres_dias_esp, ventas_por_dia_ordenado.values, color='coral')
      ax2.set_title('Ventas Totales por Día de la Semana', fontsize=14, fontweight='bold')
      ax2.set_xlabel('Día de la Semana', fontsize=12)
      ax2.set_ylabel('Ventas Totales ($)', fontsize=12)
      ax2.tick_params(axis='x', rotation=45)
      ax2.grid(True, alpha=0.3, axis='y')
      
      plt.tight_layout()
      
      ventana_graf = tk.Toplevel(ventana_analisis)
      ventana_graf.title("Análisis Temporal de Ventas")
      canvas = FigureCanvasTkAgg(fig, ventana_graf)
      canvas.draw()
      canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def mostrar_grafica_productos_periodo():
      """Gráfica de productos por período"""
      fig, ax = plt.subplots(figsize=(14, 8))
      
      # Productos más vendidos por estación
      estaciones = ['Primavera', 'Verano', 'Otoño', 'Invierno']
      productos_por_estacion = {}
      
      for estacion in estaciones:
        df_estacion = df_ventas[df_ventas['Estacion'] == estacion]
        if not df_estacion.empty:
          top_producto = df_estacion.groupby('Producto')['Cantidad'].sum().sort_values(ascending=False).head(1)
          if not top_producto.empty:
            productos_por_estacion[estacion] = top_producto.index[0]
      
      if productos_por_estacion:
        estaciones_list = list(productos_por_estacion.keys())
        productos_list = list(productos_por_estacion.values())
        colores = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3']
        
        ax.barh(estaciones_list, [1]*len(estaciones_list), color=colores[:len(estaciones_list)])
        for i, (estacion, producto) in enumerate(productos_por_estacion.items()):
          ax.text(0.5, i, f"{producto}", ha='center', va='center', fontweight='bold', fontsize=10)
        
        ax.set_title('Productos Más Vendidos por Estación', fontsize=14, fontweight='bold')
        ax.set_xlabel('Estación', fontsize=12)
        ax.set_ylabel('Producto', fontsize=12)
        ax.set_xticks([])
      
      plt.tight_layout()
      
      ventana_graf = tk.Toplevel(ventana_analisis)
      ventana_graf.title("Productos por Período")
      canvas = FigureCanvasTkAgg(fig, ventana_graf)
      canvas.draw()
      canvas.get_tk_widget().pack(fill="both", expand=True)
    
    tk.Button(frame_botones_graf, text="Ver Gráfica Temporal", command=mostrar_grafica_temporal, 
              bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=25).pack(side="left", padx=5)
    tk.Button(frame_botones_graf, text="Ver Gráfica por Período", command=mostrar_grafica_productos_periodo, 
              bg="#FF9800", fg="white", font=("Arial", 10, "bold"), width=25).pack(side="left", padx=5)
    tk.Button(frame_botones_graf, text="Cerrar", command=ventana_analisis.destroy, 
              bg="#757575", fg="white", font=("Arial", 10, "bold"), width=15).pack(side="right", padx=5)
    
    # Configurar scroll
    canvas_frame.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    logger.info("Análisis predictivo de ventas completado")

  def generar_informe_automatico():
    """Genera un informe automático completo de inventario y ventas"""
    logger.info("Generando informe automático")
    
    informe_texto = []
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Encabezado del informe
    informe_texto.append("=" * 80)
    informe_texto.append("INFORME AUTOMÁTICO DE GESTIÓN DE INVENTARIO Y VENTAS")
    informe_texto.append("=" * 80)
    informe_texto.append(f"Fecha de generación: {fecha_actual}")
    informe_texto.append("")
    
    # ========== SECCIÓN 1: RESUMEN DE INVENTARIO ==========
    informe_texto.append("=" * 80)
    informe_texto.append("1. RESUMEN DE INVENTARIO")
    informe_texto.append("=" * 80)
    informe_texto.append("")
    
    df_inventario = inventario_obj.get_dataframe()
    total_productos = len(inventario_obj.productos)
    valor_total_inventario = inventario_obj.calcular_valor_total_recursivo()
    productos_stock_bajo = inventario_obj.obtener_productos_stock_bajo()
    
    informe_texto.append(f"Total de productos en inventario: {total_productos}")
    informe_texto.append(f"Valor total del inventario: ${int(valor_total_inventario):,}")
    informe_texto.append(f"Productos con stock bajo (< 10 unidades): {len(productos_stock_bajo)}")
    informe_texto.append("")
    
    # Productos por categoría
    if not df_inventario.empty:
      productos_por_categoria = df_inventario.groupby('Categoría').size()
      informe_texto.append("Distribución de productos por categoría:")
      for categoria, cantidad in productos_por_categoria.items():
        porcentaje = (cantidad / total_productos * 100) if total_productos > 0 else 0
        informe_texto.append(f"  • {categoria}: {cantidad} productos ({porcentaje:.1f}%)")
      informe_texto.append("")
      
      # Stock total por categoría
      stock_por_categoria = df_inventario.groupby('Categoría')['Cantidad'].sum()
      informe_texto.append("Stock total por categoría:")
      for categoria, stock in stock_por_categoria.items():
        informe_texto.append(f"  • {categoria}: {int(stock)} unidades")
      informe_texto.append("")
      
      # Valor por categoría
      df_inventario['ValorTotal'] = df_inventario['PrecioVenta'] * df_inventario['Cantidad']
      valor_por_categoria = df_inventario.groupby('Categoría')['ValorTotal'].sum()
      informe_texto.append("Valor del inventario por categoría:")
      for categoria, valor in valor_por_categoria.items():
        informe_texto.append(f"  • {categoria}: ${int(valor):,}")
      informe_texto.append("")
    
    # Productos con stock bajo
    if productos_stock_bajo:
      informe_texto.append("PRODUCTOS CON STOCK BAJO (< 10 unidades):")
      for producto in productos_stock_bajo[:20]:  # Limitar a 20 para no hacer el informe muy largo
        informe_texto.append(f"  • {producto.nombre} (SKU: {producto.sku}): {producto.cantidad} unidades")
      if len(productos_stock_bajo) > 20:
        informe_texto.append(f"  ... y {len(productos_stock_bajo) - 20} productos más")
      informe_texto.append("")
    
    # Top 10 productos con mayor stock
    if not df_inventario.empty:
      top_stock = df_inventario.nlargest(10, 'Cantidad')[['Nombre', 'Cantidad', 'Categoría']]
      informe_texto.append("Top 10 productos con mayor stock:")
      for idx, (_, row) in enumerate(top_stock.iterrows(), 1):
        informe_texto.append(f"  {idx}. {row['Nombre']} ({row['Categoría']}): {int(row['Cantidad'])} unidades")
      informe_texto.append("")
    
    # ========== SECCIÓN 2: RESUMEN DE VENTAS ==========
    informe_texto.append("=" * 80)
    informe_texto.append("2. RESUMEN DE VENTAS")
    informe_texto.append("=" * 80)
    informe_texto.append("")
    
    df_ventas = registro_ventas.get_dataframe()
    if df_ventas.empty:
      informe_texto.append("No hay ventas registradas.")
      informe_texto.append("")
    else:
      total_ventas = len(df_ventas)
      total_ingresos = df_ventas['Total'].sum()
      cantidad_total_vendida = df_ventas['Cantidad'].sum()
      ticket_promedio = total_ingresos / total_ventas if total_ventas > 0 else 0
      
      informe_texto.append(f"Total de ventas registradas: {total_ventas}")
      informe_texto.append(f"Ingresos totales: ${int(total_ingresos):,}")
      informe_texto.append(f"Cantidad total de productos vendidos: {int(cantidad_total_vendida)} unidades")
      informe_texto.append(f"Ticket promedio: ${int(ticket_promedio):,}")
      informe_texto.append("")
      
      # Ventas por categoría
      ventas_por_categoria = df_ventas.groupby('Categoría')['Total'].sum()
      informe_texto.append("Ventas por categoría:")
      for categoria, total in ventas_por_categoria.items():
        porcentaje = (total / total_ingresos * 100) if total_ingresos > 0 else 0
        informe_texto.append(f"  • {categoria}: ${int(total):,} ({porcentaje:.1f}%)")
      informe_texto.append("")
      
      # Top 10 productos más vendidos (por cantidad)
      top_productos_cantidad = df_ventas.groupby('Producto')['Cantidad'].sum().sort_values(ascending=False).head(10)
      informe_texto.append("Top 10 productos más vendidos (por cantidad):")
      for idx, (producto, cantidad) in enumerate(top_productos_cantidad.items(), 1):
        informe_texto.append(f"  {idx}. {producto}: {int(cantidad)} unidades")
      informe_texto.append("")
      
      # Top 10 productos más vendidos (por valor)
      top_productos_valor = df_ventas.groupby('Producto')['Total'].sum().sort_values(ascending=False).head(10)
      informe_texto.append("Top 10 productos más vendidos (por valor):")
      for idx, (producto, valor) in enumerate(top_productos_valor.items(), 1):
        informe_texto.append(f"  {idx}. {producto}: ${int(valor):,}")
      informe_texto.append("")
      
      # Análisis temporal
      try:
        df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha/Hora'])
        df_ventas['Mes'] = df_ventas['Fecha'].dt.month
        meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        ventas_por_mes = df_ventas.groupby('Mes')['Total'].sum()
        
        informe_texto.append("Ventas por mes:")
        for mes_num, total_mes in ventas_por_mes.items():
          mes_nombre = meses_orden[mes_num - 1]
          porcentaje = (total_mes / total_ingresos * 100) if total_ingresos > 0 else 0
          informe_texto.append(f"  • {mes_nombre}: ${int(total_mes):,} ({porcentaje:.1f}%)")
        informe_texto.append("")
        
        # Mejor y peor mes
        if len(ventas_por_mes) > 0:
          mejor_mes_num = ventas_por_mes.idxmax()
          peor_mes_num = ventas_por_mes.idxmin()
          informe_texto.append(f"Mejor mes: {meses_orden[mejor_mes_num - 1]} (${int(ventas_por_mes[mejor_mes_num]):,})")
          informe_texto.append(f"Peor mes: {meses_orden[peor_mes_num - 1]} (${int(ventas_por_mes[peor_mes_num]):,})")
          informe_texto.append("")
      except Exception as e:
        logger.error(f"Error al procesar análisis temporal: {str(e)}")
    
    # ========== SECCIÓN 3: ANÁLISIS Y RECOMENDACIONES ==========
    informe_texto.append("=" * 80)
    informe_texto.append("3. ANÁLISIS Y RECOMENDACIONES")
    informe_texto.append("=" * 80)
    informe_texto.append("")
    
    # Recomendaciones de stock
    if productos_stock_bajo:
      informe_texto.append("RECOMENDACIONES DE INVENTARIO:")
      informe_texto.append(f"  • Se recomienda reponer stock de {len(productos_stock_bajo)} productos con stock bajo.")
      informe_texto.append("  • Revise los productos listados en la sección de stock bajo.")
      informe_texto.append("")
    
    # Análisis de rotación (si hay ventas)
    if not df_ventas.empty and not df_inventario.empty:
      informe_texto.append("ANÁLISIS DE ROTACIÓN:")
      # Productos que se venden pero tienen mucho stock
      productos_vendidos = df_ventas['Producto'].unique()
      for producto_nombre in productos_vendidos[:5]:  # Analizar top 5
        producto_inv = inventario_obj.buscar_producto_por_nombre(producto_nombre)
        if producto_inv:
          ventas_producto = df_ventas[df_ventas['Producto'] == producto_nombre]['Cantidad'].sum()
          if producto_inv.cantidad > ventas_producto * 3:
            informe_texto.append(f"  • {producto_nombre}: Stock alto ({producto_inv.cantidad}) vs ventas ({int(ventas_producto)}). Considerar reducir inventario.")
      informe_texto.append("")
    
    # ========== SECCIÓN 4: MÉTRICAS CLAVE ==========
    informe_texto.append("=" * 80)
    informe_texto.append("4. MÉTRICAS CLAVE")
    informe_texto.append("=" * 80)
    informe_texto.append("")
    
    if not df_ventas.empty:
      informe_texto.append(f"Ingresos totales: ${int(total_ingresos):,}")
      informe_texto.append(f"Valor del inventario: ${int(valor_total_inventario):,}")
      if valor_total_inventario > 0:
        ratio_ventas_inventario = (total_ingresos / valor_total_inventario) * 100
        informe_texto.append(f"Ratio ventas/inventario: {ratio_ventas_inventario:.1f}%")
      informe_texto.append(f"Ticket promedio: ${int(ticket_promedio):,}")
      informe_texto.append(f"Total de productos únicos vendidos: {df_ventas['Producto'].nunique()}")
      informe_texto.append("")
    
    # Pie de página
    informe_texto.append("=" * 80)
    informe_texto.append("Fin del informe")
    informe_texto.append("=" * 80)
    
    # Convertir lista a texto
    informe_completo = "\n".join(informe_texto)
    
    # Mostrar informe en ventana
    ventana_informe = tk.Toplevel(root)
    ventana_informe.title("Informe Automático de Gestión")
    ventana_informe.geometry("900x700")
    
    # Frame con scroll
    frame_scroll = tk.Frame(ventana_informe)
    frame_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
    scrollbar = tk.Scrollbar(frame_scroll)
    scrollbar.pack(side="right", fill="y")
    
    texto_informe = tk.Text(frame_scroll, wrap="none", yscrollcommand=scrollbar.set, 
                           font=("Courier", 10), bg="#ffffff")
    texto_informe.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=texto_informe.yview)
    
    texto_informe.insert("1.0", informe_completo)
    texto_informe.config(state="disabled")
    
    # Frame para botones
    frame_botones_informe = tk.Frame(ventana_informe)
    frame_botones_informe.pack(fill="x", padx=10, pady=10)
    
    def guardar_informe():
      """Guarda el informe en un archivo de texto"""
      try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"informe_automatico_{timestamp}.txt"
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
          f.write(informe_completo)
        messagebox.showinfo("Éxito", f"Informe guardado exitosamente como:\n{nombre_archivo}")
        logger.info(f"Informe guardado: {nombre_archivo}")
      except Exception as e:
        logger.error(f"Error al guardar informe: {str(e)}")
        messagebox.showerror("Error", f"Error al guardar el informe: {str(e)}")
    
    def copiar_informe():
      """Copia el informe al portapapeles"""
      try:
        ventana_informe.clipboard_clear()
        ventana_informe.clipboard_append(informe_completo)
        messagebox.showinfo("Éxito", "Informe copiado al portapapeles")
        logger.info("Informe copiado al portapapeles")
      except Exception as e:
        logger.error(f"Error al copiar informe: {str(e)}")
        messagebox.showerror("Error", f"Error al copiar el informe: {str(e)}")
    
    tk.Button(frame_botones_informe, text="Guardar Informe", command=guardar_informe, 
              bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=20).pack(side="left", padx=5)
    tk.Button(frame_botones_informe, text="Copiar al Portapapeles", command=copiar_informe, 
              bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=25).pack(side="left", padx=5)
    tk.Button(frame_botones_informe, text="Cerrar", command=ventana_informe.destroy, 
              bg="#757575", fg="white", font=("Arial", 10, "bold"), width=15).pack(side="right", padx=5)
    
    logger.info("Informe automático generado exitosamente")

    

  # Botones - Organizados en 2 filas compactas
  frame_botones = tk.Frame(root, bg="#f0f0f0")
  frame_botones.pack(fill="x", padx=11, pady=5)
  
  # Fila 1: Botones principales de gestión
  frame_fila1 = tk.Frame(frame_botones, bg="#f0f0f0")
  frame_fila1.pack(fill="x", pady=3)
  btn_agregar = tk.Button(frame_fila1, text="Agregar", command=agregar, bg="#69F36E", fg="white", font=("Arial", 9, "bold"))
  btn_eliminar = tk.Button(frame_fila1, text="Eliminar", command=eliminar, bg="#D80000", fg="white", font=("Arial", 9, "bold"))
  btn_actualizar = tk.Button(frame_fila1, text="Actualizar", command=actualizar, bg="#6E03FA", fg="white", font=("Arial", 9, "bold"))
  btn_mostrar = tk.Button(frame_fila1, text="Refrescar", command=refresh_tree, bg="#9E9E9E", fg="white", font=("Arial", 9, "bold"))
  btn_entrada = tk.Button(frame_fila1, text="Registrar Entrada", command=entrada, bg="#4CAF50", fg="white", font=("Arial", 9, "bold"))
  btn_salida = tk.Button(frame_fila1, text="Registrar Salida", command=salida, bg="#F44336", fg="white", font=("Arial", 9, "bold"))
  btn_buscar = tk.Button(frame_fila1, text="Buscar por SKU", command=buscar_sku, bg="#00ACC1", fg="white", font=("Arial", 9, "bold"))
  btn_reporte = tk.Button(frame_fila1, text="Reporte stock bajo", command=reporte_stock_bajo, bg="#FF6600", fg="white", font=("Arial", 9, "bold"))
  btn_ventas = tk.Button(frame_fila1, text="Registrar Ventas", command=ventas, bg="#2196F3", fg="white", font=("Arial", 9, "bold"))
  btn_graficas = tk.Button(frame_fila1, text="Ver Gráficas", command=mostrar_graficas, bg="#FF6B35", fg="white", font=("Arial", 9, "bold"))
  btn_analisis_predictivo = tk.Button(frame_fila1, text="Análisis Predictivo", command=analisis_predictivo_ventas, bg="#9C27B0", fg="white", font=("Arial", 9, "bold"))
  
  btn_agregar.pack(side="left", padx=2, pady=3)
  btn_eliminar.pack(side="left", padx=2, pady=3)
  btn_actualizar.pack(side="left", padx=2, pady=3)
  btn_mostrar.pack(side="left", padx=2, pady=3)
  btn_entrada.pack(side="left", padx=2, pady=3)
  btn_salida.pack(side="left", padx=2, pady=3)
  btn_buscar.pack(side="left", padx=2, pady=3)
  btn_reporte.pack(side="left", padx=2, pady=3)
  btn_ventas.pack(side="left", padx=2, pady=3)
  btn_graficas.pack(side="left", padx=2, pady=3)
  btn_analisis_predictivo.pack(side="left", padx=2, pady=3)
  
  # Fila 2: Botones de utilidades y configuración
  frame_fila2 = tk.Frame(frame_botones, bg="#f0f0f0")
  frame_fila2.pack(fill="x", pady=3)
  btn_exportar = tk.Button(frame_fila2, text="Exportar a Excel", command=exportar_xls, bg="#1D6F42", fg="white", font=("Arial", 9, "bold"))
  btn_exportar.pack(side="left", padx=2, pady=3)
  
  def importar_inventario():
    """Importa inventario desde un archivo Excel"""
    ruta_archivo = filedialog.askopenfilename(
      title="Seleccionar archivo Excel de inventario",
      filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
    )
    if not ruta_archivo:
      return
    
    try:
      resultado = importar_inventario_desde_excel(inventario_obj, ruta_archivo)
      refresh_tree()
      messagebox.showinfo("Importación Completada",
        f"Importación de inventario completada:\n\n"
        f"- Productos importados: {resultado['importados']}\n"
        f"- Productos duplicados (omitidos): {resultado['duplicados']}\n"
        f"- Productos con errores: {resultado['errores']}")
      logger.info(f"Importación de inventario completada: {resultado}")
    except Exception as e:
      logger.error(f"Error al importar inventario: {str(e)}")
      messagebox.showerror("Error", f"Error al importar inventario: {str(e)}")
  
  def limpiar_datos():
    """Limpia datos nulos y errores"""
    respuesta = messagebox.askyesno("Limpiar Datos",
      "¿Deseas limpiar datos nulos y errores?\n\n"
      "Esto corregirá:\n"
      "- Nombres, categorías y proveedores vacíos\n"
      "- Precios y cantidades negativas\n"
      "- SKUs inválidos\n"
      "- Ventas con datos incorrectos\n\n"
      "¿Continuar?")
    if not respuesta:
      return
    
    try:
      resultado = limpiar_datos_nulos(inventario_obj, registro_ventas)
      refresh_tree()
      messagebox.showinfo("Limpieza Completada",
        f"Limpieza de datos completada:\n\n"
        f"- Productos corregidos: {resultado['productos_limpiados']}\n"
        f"- Ventas corregidas: {resultado['ventas_limpiadas']}\n"
        f"- Ventas eliminadas: {resultado['ventas_eliminadas']}")
      logger.info(f"Limpieza de datos completada: {resultado}")
    except Exception as e:
      logger.error(f"Error al limpiar datos: {str(e)}")
      messagebox.showerror("Error", f"Error al limpiar datos: {str(e)}")
  
  # Agregar botones restantes a la fila 2
  btn_importar_inventario = tk.Button(frame_fila2, text="Importar Inventario", command=importar_inventario, bg="#9C27B0", fg="white", font=("Arial", 9, "bold"))
  btn_importar_inventario.pack(side="left", padx=2, pady=3)
  btn_gestionar_cat = tk.Button(frame_fila2, text="Gestionar Categorías", command=gestionar_categorias, bg="#E91E63", fg="white", font=("Arial", 9, "bold"))
  btn_gestionar_cat.pack(side="left", padx=2, pady=3)
  
  def generar_datos_aleatorios():
    """Genera datos aleatorios en archivos Excel con errores y datos nulos"""
    # Crear ventana de diálogo para ingresar cantidades
    dialog = tk.Toplevel(root)
    dialog.title("Generar Datos Aleatorios")
    dialog.geometry("450x250")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()
    
    # Centrar ventana
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    
    tk.Label(dialog, text="Generar Datos Aleatorios en Excel", font=("Arial", 12, "bold")).pack(pady=10)
    tk.Label(dialog, text="Los datos generados incluirán errores y valores nulos para pruebas.", wraplength=400).pack(pady=5)
    tk.Label(dialog, text="Máximo: 600,000 productos (SKU máximo: 600,000)", font=("Arial", 9), fg="gray").pack(pady=2)
    
    frame_cantidades = tk.Frame(dialog)
    frame_cantidades.pack(pady=15)
    
    tk.Label(frame_cantidades, text="Cantidad de productos:", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=8, sticky="e")
    e_productos = tk.Entry(frame_cantidades, width=20, font=("Arial", 10))
    e_productos.insert(0, "50")
    e_productos.grid(row=0, column=1, padx=10, pady=8)
    
    tk.Label(frame_cantidades, text="Cantidad de ventas:", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=8, sticky="e")
    e_ventas = tk.Entry(frame_cantidades, width=20, font=("Arial", 10))
    e_ventas.insert(0, "200")
    e_ventas.grid(row=1, column=1, padx=10, pady=8)
    
    def generar():
      try:
        cantidad_productos = int(e_productos.get())
        cantidad_ventas = int(e_ventas.get())
        
        if cantidad_productos <= 0 or cantidad_ventas <= 0:
          messagebox.showerror("Error", "Las cantidades deben ser mayores que cero.")
          return
        
        if cantidad_productos > 600000:
          messagebox.showerror("Error", f"La cantidad máxima de productos es 600,000.\nSe solicitó: {cantidad_productos:,}")
          return
        
        dialog.destroy()
        
        # Mostrar mensaje de progreso
        messagebox.showinfo("Generando", 
          f"Generando {cantidad_productos:,} productos y {cantidad_ventas:,} ventas...\n\n"
          f"Esto puede tomar varios minutos para grandes cantidades.\n"
          f"Por favor, espere...")
        
        resultado = generar_datos_aleatorios_excel(cantidad_productos, cantidad_ventas)
        
        messagebox.showinfo("Generación Completada",
          f"Archivos Excel generados exitosamente:\n\n"
          f"{resultado['archivo_productos']}\n"
          f"   - {resultado['productos_generados']:,} productos generados\n\n"
          f"{resultado['archivo_ventas']}\n"
          f"   - {resultado['ventas_generadas']:,} ventas generadas\n\n"
          f"Nota: Los archivos contienen errores y datos nulos intencionales\n"
          f"para poder probar la función de limpieza de datos.")
        logger.info(f"Datos aleatorios generados exitosamente: {resultado}")
      except ValueError as e:
        if "máximo" in str(e).lower():
          messagebox.showerror("Error", str(e))
        else:
          messagebox.showerror("Error", "Por favor ingrese números válidos.")
      except Exception as e:
        logger.error(f"Error al generar datos aleatorios: {str(e)}")
        messagebox.showerror("Error", f"Error al generar datos: {str(e)}")
    
    frame_botones = tk.Frame(dialog)
    frame_botones.pack(pady=20)
    
    tk.Button(frame_botones, text="Generar", command=generar, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)
    tk.Button(frame_botones, text="Cancelar", command=dialog.destroy, bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)
    
    e_productos.focus_set()
    e_productos.select_range(0, tk.END)
    dialog.bind("<Return>", lambda e: generar())
    dialog.bind("<Escape>", lambda e: dialog.destroy())
  
  btn_generar_informe = tk.Button(frame_fila2, text="Generar Informe", command=generar_informe_automatico, bg="#607D8B", fg="white", font=("Arial", 9, "bold"))
  btn_generar_informe.pack(side="left", padx=2, pady=3)
  btn_generar_datos = tk.Button(frame_fila2, text="Generar Datos Aleatorios", command=generar_datos_aleatorios, bg="#FF9800", fg="white", font=("Arial", 9, "bold"))
  btn_generar_datos.pack(side="left", padx=2, pady=3)
  btn_limpiar_datos = tk.Button(frame_fila2, text="Limpiar Datos", command=limpiar_datos, bg="#FF5722", fg="white", font=("Arial", 9, "bold"))
  btn_limpiar_datos.pack(side="left", padx=2, pady=3)
  
  def cerrar_sesion():
    """Cierra la sesión actual y vuelve al login"""
    try:
      username = current_user.username if hasattr(current_user, 'username') else 'Usuario'
      logger.info(f"Usuario {username} cerró sesión")
    except:
      logger.info("Sesión cerrada")
    
    # Confirmar cierre de sesión
    respuesta = messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que deseas cerrar sesión?")
    if not respuesta:
      return
    
    # Cerrar todas las ventanas secundarias abiertas
    for widget in root.winfo_children():
      if isinstance(widget, tk.Toplevel):
        try:
          widget.destroy()
        except:
          pass
    
    # Cerrar ventana principal
    root.quit()
    root.destroy()
    
    # Reiniciar aplicación con nuevo login
    try:
      import sys
      import os
      python = sys.executable
      os.execl(python, python, *sys.argv)
    except Exception as e:
      logger.error(f"Error al reiniciar aplicación: {str(e)}")
      messagebox.showinfo("Sesión cerrada", "Has cerrado sesión exitosamente. Por favor, reinicia la aplicación manualmente.")
  
  btn_logout = tk.Button(frame_fila2, text="Cerrar Sesión", command=cerrar_sesion, bg="#F44336", fg="white", font=("Arial", 9, "bold"))
  btn_logout.pack(side="left", padx=2, pady=3)

  # Botón de descarga de log en ubicación discreta (esquina inferior derecha, casi inaccesible)
  btn_descargar_log = tk.Button(
    root, 
    text="Descargar Log", 
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
      btn_gestionar_cat.config(state='disabled')
  except NameError:
    # current_user no definido -> comportarse como no autenticado (deshabilitar admin)
    btn_eliminar.config(state='disabled')
    btn_actualizar.config(state='disabled')
    btn_descargar_log.config(state='disabled')
    btn_gestionar_cat.config(state='disabled')

  logger.info("Interfaz gráfica inicializada - Iniciando loop principal")
  refresh_tree()  # Esto también actualizará el valor total automáticamente
  root.mainloop()
  logger.info("=== Aplicación cerrada ===")



if __name__ == "__main__":
  main()