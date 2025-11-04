"""Utilities ligeras para GUI — lectura de imágenes y helpers.

Provee `leer_imagen(path_or_url, size=None)` que carga una imagen desde una ruta local
o una URL pública y devuelve un objeto compatible con Tkinter (ImageTk.PhotoImage o tk.PhotoImage).
Si Pillow no está instalado hace un fallback usando tk.PhotoImage cuando es posible.
"""
from urllib.parse import urlparse
import urllib.request
import io
import os
import tempfile
import tkinter as tk

try:
    from PIL import Image, ImageTk
    _HAS_PIL = True
except Exception:
    Image = None
    ImageTk = None
    _HAS_PIL = False


def leer_imagen(path_or_url, size=None, timeout=10):
    """Carga una imagen desde una ruta local o URL.

    Args:
        path_or_url (str): ruta local o URL (http/https).
        size (tuple[int,int] | None): (ancho, alto) para redimensionar.
        timeout (int): timeout para descargas HTTP.

    Returns:
        ImageTk.PhotoImage | tk.PhotoImage | None
    """
    if not path_or_url:
        return None

    parsed = urlparse(path_or_url)
    is_url = parsed.scheme in ("http", "https")

    if _HAS_PIL:
        try:
            if is_url:
                with urllib.request.urlopen(path_or_url, timeout=timeout) as resp:
                    data = resp.read()
                img = Image.open(io.BytesIO(data))
            else:
                img = Image.open(path_or_url)

            if size:
                try:
                    resample = Image.LANCZOS
                except Exception:
                    resample = Image.ANTIALIAS
                img = img.resize((int(size[0]), int(size[1])), resample)

            return ImageTk.PhotoImage(img)
        except Exception:
            # continue to fallback
            pass

    # Fallback using tk.PhotoImage (works for some formats, and requires a file)
    try:
        if is_url:
            with urllib.request.urlopen(path_or_url, timeout=timeout) as resp:
                data = resp.read()
            suffix = os.path.splitext(parsed.path)[1] or ".png"
            fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            os.close(fd)
            with open(tmp_path, "wb") as f:
                f.write(data)
            try:
                img = tk.PhotoImage(file=tmp_path)
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            return img
        else:
            return tk.PhotoImage(file=path_or_url)
    except Exception:
        return None


def centrar_ventana(ventana, ancho, alto):
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    return ventana.geometry(f'{ancho}x{alto}+{x}+{y}')
