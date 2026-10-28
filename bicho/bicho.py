"""El Pombero suelto en la pantalla.

Uso:
  python bicho.py            lo suelta (o, si ya anda suelto, le hace decir algo)
  python bicho.py chau       lo manda de vuelta al monte
  python bicho.py decir TXT  le hace decir TXT

Solo usa la biblioteca estándar (tkinter). Una sola instancia: la que anda suelta
escucha en 127.0.0.1:47404 y las invocaciones siguientes le mandan órdenes por ahí.
"""
import json
import os
import platform
import queue
import random
import socket
import subprocess
import sys
import threading
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
PUERTO = 47404
SISTEMA = platform.system()

# --- Sprite -----------------------------------------------------------------
# 20x24, cada letra es un color de la paleta; "." es transparente.
PALETA = {
    "K": "#1a1208",  # contorno
    "S": "#d9b25a",  # sombrero de paja
    "s": "#a8833a",
    "h": "#3d2716",  # sombra bajo el ala
    "H": "#5a3a22",  # pelo y barba
    "E": "#ffd75a",  # ojos que brillan en la sombra
    "F": "#b07850",  # piel
    "f": "#8a5a3a",
    "M": "#3a0f0f",  # boca abierta
    "P": "#7a2b2b",  # poncho
    "Y": "#e0c070",  # guarda
}
CUERPO = [
    "......KKKKKKKK......",
    ".....KSSSSSSSSK.....",
    ".....KSsSSSSsSK.....",
    "....KssssssssssK....",
    ".KKSSSSSSSSSSSSSSKK.",
    "KSSSSSSSSSSSSSSSSSSK",
    ".KKKKKKKKKKKKKKKKKK.",
    "...KhhhhhhhhhhhhK...",
    "...KhEEhhhhhhEEhK...",
    "...KHFFFFFFFFFFHK...",
    "...KHFfFFKKFFfFHK...",
    "...KHHHHHHHHHHHHK...",
    "....KHHHhhhhHHHK....",
    "...KPPPKHHHHKPPPK...",
    "..KHPPPPPKKPPPPPHK..",
    "..KHPYYYYYYYYYYPHK..",
    "..KFPPYPPYYPPYPPFK..",
    "...KPPPPPPPPPPPPK...",
    "...KPPPPPPPPPPPPK...",
    "....KKKKKKKKKKKK....",
]
PIERNAS_QUIETO = [
    ".....KHHK..KHHK.....",
    ".....KHHK..KHHK.....",
    "....KFFFK..KFFFK....",
    "....KKKKK..KKKKK....",
]
PIERNAS_PASO = [
    "....KHHK....KHHK....",
    "...KHHK......KHHK...",
    "..KFFFK......KFFFK..",
    "..KKKKK......KKKKK..",
]
OJOS_CERRADOS = "...KhKKhhhhhhKKhK..."
BOCA_ABIERTA = "...KHFfFKMMKFfFHK..."


def armar(piernas=PIERNAS_QUIETO, parpadeo=False, habla=False):
    filas = list(CUERPO) + list(piernas)
    if parpadeo:
        filas[8] = OJOS_CERRADOS
    if habla:
        filas[10] = BOCA_ABIERTA
    return filas


# --- Frases -----------------------------------------------------------------
with open(os.path.join(AQUI, "frases.json"), encoding="utf-8") as f:
    FRASES = json.load(f)
_ultimas = []


def frase(tipo=None):
    if tipo is None:
        hora = time.localtime().tm_hour
        tipo = "suelta"
        if 13 <= hora < 17 and random.random() < 0.3:
            tipo = "siesta"
        elif hora < 6 and random.random() < 0.3:
            tipo = "noche"
    opciones = [x for x in FRASES[tipo] if x not in _ultimas] or FRASES[tipo]
    elegida = random.choice(opciones)
    _ultimas.append(elegida)
    del _ultimas[:-8]
    return elegida


# --- Órdenes entre procesos -------------------------------------------------
def mandar(orden):
    """Manda una orden a la instancia suelta. Devuelve False si no hay ninguna."""
    try:
        with socket.create_connection(("127.0.0.1", PUERTO), timeout=1) as s:
            s.sendall(orden.encode("utf-8"))
        return True
    except OSError:
        return False


def soltar():
    """Arranca una instancia desacoplada de la consola que la invocó."""
    args = [sys.executable, os.path.abspath(__file__), "--suelto"]
    opciones = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL, "close_fds": True}
    if SISTEMA == "Windows":
        pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        if os.path.exists(pyw):
            args[0] = pyw
        opciones["creationflags"] = 0x00000008 | 0x00000200  # DETACHED_PROCESS | NEW_PROCESS_GROUP
    else:
        opciones["start_new_session"] = True
    subprocess.Popen(args, **opciones)


# --- El bicho ---------------------------------------------------------------
class Pombero:
    TIC = 90  # ms

    def __init__(self, ordenes):
        import tkinter as tk
        self.tk = tk
        self.ordenes = ordenes
        if SISTEMA == "Windows":
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass

        self.root = tk.Tk()
        self.root.title("Pombero")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        dpi = self.root.winfo_fpixels("1i")
        self.esc = max(3, round(4 * dpi / 96))
        self.w, self.h = 20 * self.esc, 24 * self.esc

        llave = "#ff00fe"
        if SISTEMA == "Windows":
            self.root.config(bg=llave)
            self.root.attributes("-transparentcolor", llave)
        elif SISTEMA == "Darwin":
            llave = "systemTransparent"
            self.root.config(bg=llave)
            self.root.attributes("-transparent", True)
        else:
            llave = "#07090d"
            self.root.config(bg=llave)

        self.cuadros = {
            "quieto": self._imagen(armar()),
            "paso": self._imagen(armar(PIERNAS_PASO)),
            "parpadeo": self._imagen(armar(parpadeo=True)),
            "habla": self._imagen(armar(habla=True)),
            "habla_paso": self._imagen(armar(PIERNAS_PASO, habla=True)),
        }
        self.lienzo = tk.Canvas(self.root, width=self.w, height=self.h, bg=llave,
                                highlightthickness=0, bd=0)
        self.lienzo.pack()
        self.sprite = self.lienzo.create_image(0, 0, anchor="nw", image=self.cuadros["quieto"])

        self._globo()
        self._menu()

        self.izq, self.arriba, self.der, self.piso = self._area()
        self.x = random.randint(self.izq, max(self.izq, self.der - self.w))
        self.y = self.arriba - self.h  # entra cayendo desde arriba
        self.vy = 0.0
        self.dir = random.choice((-1, 1))
        self.estado = "cae"
        self.quieto_hasta = 0
        self.tics = 0
        self.parpadeo_en = time.time() + 3
        self.proxima_charla = time.time() + random.uniform(25, 50)
        self.pausado = False
        self.cerrando = False
        self.arrastre = None
        self.texto, self.letra, self.globo_hasta = "", 0, 0

        self.lienzo.bind("<ButtonPress-1>", self._agarrar)
        self.lienzo.bind("<B1-Motion>", self._arrastrar)
        self.lienzo.bind("<ButtonRelease-1>", self._soltar)
        self.lienzo.bind("<Button-3>", lambda e: self.menu.tk_popup(e.x_root, e.y_root))
        self.lienzo.bind("<Button-2>", lambda e: self.menu.tk_popup(e.x_root, e.y_root))

        self._mover()
        self.root.after(700, lambda: self.decir(frase("saludo")))
        self.root.after(self.TIC, self._tic)

    # armado
    def _imagen(self, filas):
        img = self.tk.PhotoImage(width=self.w, height=self.h)
        for y, fila in enumerate(filas):
            for x, c in enumerate(fila):
                if c != ".":
                    x0, y0 = x * self.esc, y * self.esc
                    img.put(PALETA[c], to=(x0, y0, x0 + self.esc, y0 + self.esc))
        return img

    def _globo(self):
        tk = self.tk
        self.globo = tk.Toplevel(self.root)
        self.globo.overrideredirect(True)
        self.globo.attributes("-topmost", True)
        self.globo.config(bg="#66e0ff")
        self.etiqueta = tk.Label(self.globo, text="", bg="#0d1118", fg="#d8dee8",
                                 font=("Segoe UI" if SISTEMA == "Windows" else "Helvetica", 11),
                                 wraplength=240, justify="left", padx=12, pady=8)
        self.etiqueta.pack(padx=1, pady=1)
        self.etiqueta.bind("<Button-1>", lambda e: self._callar())
        self.globo.withdraw()

    def _menu(self):
        self.menu = self.tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Decí algo", command=lambda: self.decir(frase()))
        self.menu.add_command(label="Quedate quieto / Caminá", command=self._pausar)
        self.menu.add_separator()
        self.menu.add_command(label="Volvé al monte", command=self.chau)

    def _area(self):
        """Área útil de la pantalla, sin la barra de tareas cuando se puede saber."""
        if SISTEMA == "Windows":
            try:
                import ctypes
                from ctypes import wintypes
                r = wintypes.RECT()
                ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(r), 0)
                return r.left, r.top, r.right, r.bottom
            except Exception:
                pass
        ancho, alto = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        return 0, 0, ancho, alto - (70 if SISTEMA == "Darwin" else 40)

    # habla
    def decir(self, texto):
        self.texto, self.letra = texto, 0
        self.globo_hasta = 0
        self.etiqueta.config(text="")
        self.globo.deiconify()
        self.globo.lift()

    def _callar(self):
        self.texto = ""
        self.globo.withdraw()

    def _ubicar_globo(self):
        self.globo.update_idletasks()
        gw, gh = self.globo.winfo_reqwidth(), self.globo.winfo_reqheight()
        gx = int(self.x + self.w / 2 - gw / 2)
        gx = max(self.izq + 4, min(gx, self.der - gw - 4))
        gy = int(self.y - gh - 6)
        if gy < self.arriba:
            gy = int(self.y + self.h + 6)
        self.globo.geometry(f"+{gx}+{gy}")

    # comportamiento
    def _pausar(self):
        self.pausado = not self.pausado
        self.decir("Me quedo acá, quietito." if self.pausado else "Bueno, salgo a recorrer.")

    def chau(self):
        if self.cerrando:
            return
        self.cerrando = True
        self.pausado = True
        self.decir(frase("chau"))
        self.root.after(3200, self.root.destroy)

    def _agarrar(self, e):
        self.arrastre = (e.x, e.y, time.time(), self.x, self.y)

    def _arrastrar(self, e):
        if not self.arrastre:
            return
        self.estado = "arrastre"
        self.x = self.root.winfo_pointerx() - self.arrastre[0]
        self.y = self.root.winfo_pointery() - self.arrastre[1]
        self._mover()

    def _soltar(self, e):
        if not self.arrastre:
            return
        _, _, t0, x0, y0 = self.arrastre
        self.arrastre = None
        if self.estado == "arrastre" and abs(self.x - x0) + abs(self.y - y0) > 6:
            self.estado, self.vy = "cae", 0.0
            self.cayo_de_alto = self.piso - self.h - self.y > 120
        else:
            self.estado = "quieto"
            self.quieto_hasta = time.time() + 2.5
            self.decir(frase("toque"))

    def _mover(self):
        self.root.geometry(f"{self.w}x{self.h}+{int(self.x)}+{int(self.y)}")
        if self.globo.state() == "normal":
            self._ubicar_globo()

    def _cuadro(self, nombre):
        self.lienzo.itemconfig(self.sprite, image=self.cuadros[nombre])

    def _tic(self):
        ahora = time.time()
        self.tics += 1

        while not self.ordenes.empty():
            orden = self.ordenes.get()
            if orden == "chau":
                self.chau()
            elif orden.startswith("decir "):
                self.decir(orden[6:].strip()[:280])
            else:
                self.decir(frase())

        hablando = bool(self.texto) and self.letra < len(self.texto)
        if hablando:
            self.letra = min(len(self.texto), self.letra + 2)
            self.etiqueta.config(text=self.texto[:self.letra])
            self._ubicar_globo()
            if self.letra == len(self.texto):
                self.globo_hasta = ahora + 2.5 + 0.06 * len(self.texto)
        elif self.texto and ahora > self.globo_hasta:
            self._callar()

        piso_y = self.piso - self.h
        if self.estado == "cae":
            self.vy = min(self.vy + 2.2, 40)
            self.y += self.vy
            if self.y >= piso_y:
                self.y = piso_y
                self.estado = "quieto"
                self.quieto_hasta = ahora + random.uniform(1, 3)
                if getattr(self, "cayo_de_alto", False):
                    self.cayo_de_alto = False
                    self.decir(frase("caida"))
        elif self.estado == "arrastre":
            pass
        elif self.estado == "quieto":
            if ahora > self.quieto_hasta and not self.pausado and not hablando:
                self.estado = "camina"
                if random.random() < 0.4:
                    self.dir *= -1
                self.camina_hasta = ahora + random.uniform(3, 9)
        elif self.estado == "camina":
            self.x += self.dir * max(2, self.esc - 1)
            if self.x <= self.izq or self.x >= self.der - self.w:
                self.x = max(self.izq, min(self.x, self.der - self.w))
                self.dir *= -1
            if ahora > self.camina_hasta or self.pausado:
                self.estado = "quieto"
                self.quieto_hasta = ahora + random.uniform(2, 7)

        if not hablando and not self.texto and not self.cerrando and ahora > self.proxima_charla:
            self.decir(frase())
            self.proxima_charla = ahora + random.uniform(30, 70)

        paso = self.estado == "camina" and (self.tics // 3) % 2 == 1
        if hablando and (self.tics % 2):
            self._cuadro("habla_paso" if paso else "habla")
        elif paso:
            self._cuadro("paso")
        elif ahora > self.parpadeo_en:
            self._cuadro("parpadeo")
            if ahora > self.parpadeo_en + 0.15:
                self.parpadeo_en = ahora + random.uniform(2.5, 6)
        else:
            self._cuadro("quieto")

        self._mover()
        self.root.after(self.TIC, self._tic)


def escuchar(srv, ordenes):
    while True:
        try:
            con, _ = srv.accept()
            with con:
                datos = con.recv(2048).decode("utf-8", "replace").strip()
            if datos:  # una conexión vacía es solo para ver si está suelto
                ordenes.put(datos)
        except OSError:
            return


def andar_suelto():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        srv.bind(("127.0.0.1", PUERTO))
    except OSError:
        return  # ya hay otro suelto
    srv.listen(4)
    ordenes = queue.Queue()
    threading.Thread(target=escuchar, args=(srv, ordenes), daemon=True).start()
    Pombero(ordenes).root.mainloop()
    srv.close()


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if argv[:1] == ["--suelto"]:
        andar_suelto()
        return
    orden = " ".join(argv).strip()
    if orden.lower() in ("chau", "andate", "basta"):
        print("El Pombero vuelve al monte." if mandar("chau") else "El Pombero no andaba suelto.")
        return
    if orden.lower().startswith(("decir ", "decí ", "deci ")):
        orden = "decir " + orden.split(" ", 1)[1]
    elif orden:
        orden = "decir " + orden
    else:
        orden = "hablar"
    if mandar(orden):
        print("El Pombero ya andaba suelto. Le pasé el mensaje.")
        return
    soltar()
    for _ in range(30):
        time.sleep(0.2)
        if _escuchando():
            break
    if orden.startswith("decir "):
        time.sleep(1.5)
        mandar(orden)
    print("El Pombero anda suelto por la pantalla. Clic derecho sobre él para mandarlo al monte.")


def _escuchando():
    try:
        socket.create_connection(("127.0.0.1", PUERTO), timeout=0.3).close()
        return True
    except OSError:
        return False


if __name__ == "__main__":
    main(sys.argv[1:])
