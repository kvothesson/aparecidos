"""Bichos del folklore sueltos en la pantalla.

Uso:
  python aparecidos.py <bicho>            lo suelta (si ya anda suelto, le hace decir algo)
  python aparecidos.py <bicho> chau       lo manda de vuelta al monte
  python aparecidos.py <bicho> <texto>    le hace decir ese texto
  python aparecidos.py todos              suelta a todos
  python aparecidos.py chau               los manda a todos al monte
  python aparecidos.py                    lista los bichos

Bichos: pombero, luzmala, lobizon, mainumby, mboi, ana, irupe, kaayaryi.

Solo usa la biblioteca estándar (tkinter). Todos los bichos viven en un mismo
proceso, el corral, que escucha órdenes en 127.0.0.1:47404.
"""
import json
import math
import os
import platform
import queue
import random
import socket
import subprocess
import sys
import threading
import time
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from sprites import BICHOS  # noqa: E402

PUERTO = 47404
SISTEMA = platform.system()
CUADROS = ("quieto", "paso", "parpadeo", "habla", "habla_paso")


# --- Frases -------------------------------------------------------------------
class Frases:
    def __init__(self, clave):
        with open(os.path.join(AQUI, "frases", clave + ".json"), encoding="utf-8") as f:
            self.grupos = json.load(f)
        self.ultimas = []

    def una(self, tipo=None):
        if tipo is None:
            hora = time.localtime().tm_hour
            tipo = "suelta"
            if 13 <= hora < 17 and random.random() < 0.3:
                tipo = "siesta"
            elif (hora >= 22 or hora < 6) and random.random() < 0.3:
                tipo = "noche"
        grupo = self.grupos[tipo]
        opciones = [x for x in grupo if x not in self.ultimas] or grupo
        elegida = random.choice(opciones)
        self.ultimas = (self.ultimas + [elegida])[-8:]
        return elegida


# --- Un bicho -----------------------------------------------------------------
class Bicho:
    TIC = 90  # ms

    def __init__(self, corral, clave):
        tk = corral.tk
        self.corral, self.clave = corral, clave
        self.spec = BICHOS[clave]
        self.modo = self.spec["modo"]
        self.frases = Frases(clave)
        self.izq, self.arriba, self.der, self.piso = corral.area

        self.esc = max(3, round(self.spec["escala"] * corral.dpi / 96))
        filas = self.spec["cuadros"]["quieto"]
        self.w, self.h = len(filas[0]) * self.esc, len(filas) * self.esc

        self.win = tk.Toplevel(corral.root)
        self.win.title(self.spec["nombre"])
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.config(bg=corral.llave)
        if SISTEMA == "Windows":
            self.win.attributes("-transparentcolor", corral.llave)
        elif SISTEMA == "Darwin":
            self.win.attributes("-transparent", True)

        self.imgs = {1: {}, -1: {}}
        for n in CUADROS:
            filas = self.spec["cuadros"][n]
            self.imgs[1][n] = self._imagen(filas)
            self.imgs[-1][n] = self._imagen([f[::-1] for f in filas]) if self.spec["espejar"] else self.imgs[1][n]
        self.lienzo = tk.Canvas(self.win, width=self.w, height=self.h, bg=corral.llave,
                                highlightthickness=0, bd=0)
        self.lienzo.pack()
        self.sprite = self.lienzo.create_image(0, 0, anchor="nw", image=self.imgs[1]["quieto"])

        self._globo()
        self._menu()

        self.dir = random.choice((-1, 1))
        self.x = random.randint(self.izq, max(self.izq, self.der - self.w))
        if self.modo in ("camina", "repta", "aparece"):
            self.y = self.arriba - self.h  # entra cayendo desde arriba
            self.estado = "cae"
        else:
            self.y = self._altura_al_azar()
            self.estado = "quieto"
        self.base_y = self.y
        self.nacio = time.time()
        self.destino = None
        self.vy = 0.0
        self.quieto_hasta = time.time() + 1
        self.mueve_hasta = 0
        self.tics = random.randint(0, 50)
        self.parpadeo_en = time.time() + random.uniform(2, 5)
        self.proxima_charla = time.time() + random.uniform(25, 50)
        self.pausado = False
        self.oculto = False
        self.cerrando = False
        self.arrastre = None
        self.cayo_de_alto = False
        self.texto, self.letra, self.globo_hasta = "", 0, 0

        self.lienzo.bind("<ButtonPress-1>", self._agarrar)
        self.lienzo.bind("<B1-Motion>", self._arrastrar)
        self.lienzo.bind("<ButtonRelease-1>", self._soltar)
        for boton in ("<Button-3>", "<Button-2>"):
            self.lienzo.bind(boton, lambda e: self.menu.tk_popup(e.x_root, e.y_root))

        self._mover()
        self.saludo_pendiente = True

    # armado
    def _imagen(self, filas):
        img = self.corral.tk.PhotoImage(width=self.w, height=self.h)
        paleta, e = self.spec["paleta"], self.esc
        for y, fila in enumerate(filas):
            for x, c in enumerate(fila):
                if c != ".":
                    img.put(paleta[c], to=(x * e, y * e, x * e + e, y * e + e))
        return img

    def _globo(self):
        tk = self.corral.tk
        fuente = "Segoe UI" if SISTEMA == "Windows" else "Helvetica"
        self.globo = tk.Toplevel(self.corral.root)
        self.globo.overrideredirect(True)
        self.globo.attributes("-topmost", True)
        self.globo.config(bg=self.spec["acento"])
        caja = tk.Frame(self.globo, bg="#0d1118", padx=12, pady=7)
        caja.pack(padx=1, pady=1)
        tk.Label(caja, text=self.spec["nombre"].upper(), bg="#0d1118", fg=self.spec["acento"],
                 font=(fuente, 8, "bold"), anchor="w").pack(fill="x")
        self.etiqueta = tk.Label(caja, text="", bg="#0d1118", fg="#d8dee8", font=(fuente, 11),
                                 wraplength=240, justify="left", anchor="w")
        self.etiqueta.pack(fill="x")
        for w in (self.globo, caja, self.etiqueta):
            w.bind("<Button-1>", lambda e: self._callar())
        self.globo.withdraw()

    def _menu(self):
        self.menu = self.corral.tk.Menu(self.win, tearoff=0)
        self.menu.add_command(label="Decí algo", command=lambda: self.decir(self.frases.una()))
        self.menu.add_command(label="Quedate quieto / Movete", command=self._pausar)
        self.menu.add_separator()
        self.menu.add_command(label="Volvé al monte", command=self.chau)
        self.menu.add_command(label="Que vuelvan todos", command=self.corral.chau_todos)

    def _altura_al_azar(self):
        alto = self.piso - self.arriba
        return random.uniform(self.arriba + alto * 0.15, self.piso - self.h - 20)

    # habla
    def hablando(self):
        return bool(self.texto)

    def decir(self, texto):
        if self.cerrando and texto not in self.frases.grupos["chau"]:
            return
        self.texto, self.letra, self.globo_hasta = texto, 0, 0
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

    # órdenes
    def _pausar(self):
        self.pausado = not self.pausado
        self.decir("Me quedo acá, quietito." if self.pausado else "Bueno, salgo a recorrer.")

    def chau(self):
        if self.cerrando:
            return
        if self.oculto:
            self.win.deiconify()
            self.oculto = False
        self.decir(self.frases.una("chau"))
        self.cerrando = self.pausado = True
        self.win.after(3200, self.cerrar)

    def cerrar(self):
        self.globo.destroy()
        self.win.destroy()
        self.corral.se_fue(self.clave)

    # arrastre
    def _agarrar(self, e):
        self.arrastre = (e.x, e.y, self.x, self.y)

    def _arrastrar(self, e):
        if not self.arrastre:
            return
        self.estado = "arrastre"
        self.x = self.win.winfo_pointerx() - self.arrastre[0]
        self.y = self.win.winfo_pointery() - self.arrastre[1]
        self._mover()

    def _soltar(self, e):
        if not self.arrastre:
            return
        _, _, x0, y0 = self.arrastre
        self.arrastre = None
        if self.estado == "arrastre" and abs(self.x - x0) + abs(self.y - y0) > 6:
            if self.modo in ("camina", "repta", "aparece"):
                self.estado, self.vy = "cae", 0.0
                self.cayo_de_alto = self.piso - self.h - self.y > 120
            else:
                self.base_y, self.destino = self.y, None
                self.estado = "quieto"
                self.quieto_hasta = time.time() + 3
                self.decir(self.frases.una("caida"))
        else:
            self.estado = "quieto"
            self.quieto_hasta = time.time() + 2.5
            self.decir(self.frases.una("toque"))

    # movimiento
    def _mover(self):
        self.win.geometry(f"{self.w}x{self.h}+{int(self.x)}+{int(self.y)}")
        if self.globo.state() == "normal":
            self._ubicar_globo()

    def _rebotar_en_bordes(self):
        if self.x <= self.izq or self.x >= self.der - self.w:
            self.x = max(self.izq, min(self.x, self.der - self.w))
            self.dir *= -1

    def _por_el_piso(self, ahora, hablando):
        piso_y = self.piso - self.h
        if self.estado == "cae":
            self.vy = min(self.vy + 2.2, 40)
            self.y += self.vy
            if self.y >= piso_y:
                self.y = piso_y
                self.estado = "quieto"
                self.quieto_hasta = ahora + random.uniform(1, 3)
                if self.cayo_de_alto:
                    self.cayo_de_alto = False
                    self.decir(self.frases.una("caida"))
        elif self.estado == "quieto":
            if ahora > self.quieto_hasta and not self.pausado and not hablando:
                if self.modo == "aparece" and random.random() < 0.35:
                    self._esfumarse()
                    return
                self.estado = "mueve"
                if random.random() < 0.4:
                    self.dir *= -1
                self.mueve_hasta = ahora + random.uniform(3, 9)
        elif self.estado == "mueve":
            paso = max(2, self.esc - 1) * self.spec["velocidad"]
            hora = time.localtime().tm_hour
            if self.clave == "lobizon" and (hora >= 20 or hora < 6):
                paso *= 1.5  # de noche anda más suelto
            self.x += self.dir * paso
            self._rebotar_en_bordes()
            if ahora > self.mueve_hasta or self.pausado:
                self.estado = "quieto"
                self.quieto_hasta = ahora + random.uniform(2, 7)

    def _esfumarse(self):
        """Desaparece y vuelve a aparecer en otro punto del piso."""
        self.oculto = True
        self.win.withdraw()

        def volver():
            if self.cerrando:
                return
            self.x = random.randint(self.izq, max(self.izq, self.der - self.w))
            self.dir = random.choice((-1, 1))
            self.quieto_hasta = time.time() + random.uniform(1.5, 4)
            self._mover()
            self.win.deiconify()
            self.win.attributes("-topmost", True)
            self.oculto = False

        self.win.after(random.randint(700, 1600), volver)

    def _flotando(self, ahora, hablando):
        if self.estado == "quieto":
            if ahora > self.quieto_hasta and not self.pausado and not hablando:
                self.estado = "mueve"
                self.mueve_hasta = ahora + random.uniform(4, 10)
                if random.random() < 0.5:
                    self.dir *= -1
                if random.random() < 0.5:
                    self.destino = self._altura_al_azar()
        elif self.estado == "mueve":
            self.x += self.dir * self.esc * 0.35
            self._rebotar_en_bordes()
            if self.destino is not None:
                self.base_y += (self.destino - self.base_y) * 0.02
            if ahora > self.mueve_hasta or self.pausado:
                self.estado = "quieto"
                self.quieto_hasta = ahora + random.uniform(2, 6)
        self.y = self.base_y + math.sin(ahora * 1.6) * self.esc * 1.5

    def _volando(self, ahora, hablando):
        if self.estado == "quieto":
            self.y = self.base_y + math.sin(ahora * 5) * self.esc * 0.6
            if ahora > self.quieto_hasta and not self.pausado and not hablando:
                self.estado = "mueve"
                alto = self.piso - self.arriba
                self.destino = (random.uniform(self.izq, self.der - self.w),
                                random.uniform(self.arriba + alto * 0.1, self.piso - self.h - 10))
        elif self.estado == "mueve":
            tx, ty = self.destino
            dx, dy = (tx - self.x) * 0.16, (ty - self.base_y) * 0.16
            lim = self.esc * 10
            dx, dy = max(-lim, min(lim, dx)), max(-lim, min(lim, dy))
            if abs(dx) > 0.5:
                self.dir = 1 if dx > 0 else -1
            self.x += dx
            self.base_y += dy
            self.y = self.base_y
            if abs(tx - self.x) < 3 and abs(ty - self.base_y) < 3 or self.pausado:
                self.estado = "quieto"
                self.quieto_hasta = ahora + random.uniform(1.5, 5)

    def tic(self, ahora, otro_habla):
        self.tics += 1
        if self.oculto:
            return

        hablando = bool(self.texto) and self.letra < len(self.texto)
        if hablando:
            self.letra = min(len(self.texto), self.letra + 2)
            self.etiqueta.config(text=self.texto[:self.letra])
            if self.letra == len(self.texto):
                self.globo_hasta = ahora + 2.5 + 0.06 * len(self.texto)
        elif self.texto and ahora > self.globo_hasta:
            self._callar()

        if self.estado != "arrastre":
            if self.modo in ("camina", "repta", "aparece"):
                self._por_el_piso(ahora, hablando)
            elif self.modo == "flota":
                self._flotando(ahora, hablando)
            else:
                self._volando(ahora, hablando)

        if self.saludo_pendiente and not self.texto and not otro_habla and ahora - self.nacio > 0.7:
            self.saludo_pendiente = False  # saluda cuando nadie más está hablando
            self.decir(self.frases.una("saludo"))
        elif (not self.texto and not otro_habla and not self.cerrando
                and ahora > self.proxima_charla):
            self.decir(self.frases.una())
            self.proxima_charla = ahora + random.uniform(30, 70)

        if self.modo == "vuela":
            paso = self.tics % 2 == 1  # aletea siempre
        elif self.modo == "flota":
            paso = random.random() < 0.12  # titila
        else:
            ritmo = 3 if self.modo == "camina" else 4
            paso = self.estado == "mueve" and (self.tics // ritmo) % 2 == 1

        imgs = self.imgs[self.dir]
        if hablando and self.tics % 2:
            img = imgs["habla_paso" if paso else "habla"]
        elif paso:
            img = imgs["paso"]
        elif ahora > self.parpadeo_en:
            img = imgs["parpadeo"]
            if ahora > self.parpadeo_en + 0.15:
                self.parpadeo_en = ahora + random.uniform(2.5, 6)
        else:
            img = imgs["quieto"]
        self.lienzo.itemconfig(self.sprite, image=img)
        self._mover()


# --- El corral: todos los bichos en un proceso --------------------------------
class Corral:
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
        self.root.withdraw()
        self.dpi = self.root.winfo_fpixels("1i")
        self.llave = {"Windows": "#ff00fe", "Darwin": "systemTransparent"}.get(SISTEMA, "#07090d")
        self.area = self._area()
        self.bichos = {}
        self.root.after(Bicho.TIC, self._tic)

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

    def soltar(self, clave):
        if clave in self.bichos and not self.bichos[clave].cerrando:
            b = self.bichos[clave]
            b.decir(b.frases.una())
        elif clave not in self.bichos:
            self.bichos[clave] = Bicho(self, clave)

    def chau_todos(self):
        for b in list(self.bichos.values()):
            b.chau()

    def se_fue(self, clave):
        self.bichos.pop(clave, None)
        if not self.bichos:
            self.root.after(200, self.root.destroy)

    def _orden(self, orden):
        partes = orden.split(" ", 2)
        verbo = partes[0]
        clave = partes[1] if len(partes) > 1 else ""
        if verbo == "todos":
            for i, c in enumerate(BICHOS):  # de a uno, para que no se pisen los saludos
                self.root.after(i * 2600, lambda c=c: self.soltar(c))
        elif verbo == "chau" and not clave:
            self.chau_todos()
        elif clave in BICHOS:
            if verbo == "soltar":
                self.soltar(clave)
            elif verbo == "chau" and clave in self.bichos:
                self.bichos[clave].chau()
            elif verbo == "decir" and len(partes) > 2:
                self.soltar(clave)
                b = self.bichos[clave]
                b.saludo_pendiente = False  # el texto pedido va en lugar del saludo
                b.win.after(800, lambda: b.decir(partes[2][:280]))

    def _tic(self):
        while not self.ordenes.empty():
            self._orden(self.ordenes.get())
        ahora = time.time()
        for b in list(self.bichos.values()):
            otro_habla = any(o.hablando() for o in self.bichos.values() if o is not b)
            b.tic(ahora, otro_habla)
        self.root.after(Bicho.TIC, self._tic)


# --- Proceso ------------------------------------------------------------------
def escuchar(srv, ordenes):
    while True:
        try:
            con, _ = srv.accept()
            with con:
                datos = con.recv(2048).decode("utf-8", "replace").strip()
            if datos:  # una conexión vacía es solo para ver si el corral está abierto
                ordenes.put(datos)
        except OSError:
            return


def abrir_corral(primera_orden):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        srv.bind(("127.0.0.1", PUERTO))
    except OSError:
        return  # ya hay un corral abierto
    srv.listen(8)
    ordenes = queue.Queue()
    if primera_orden:
        ordenes.put(primera_orden)
    threading.Thread(target=escuchar, args=(srv, ordenes), daemon=True).start()
    corral = Corral(ordenes)
    corral.root.mainloop()
    srv.close()


def mandar(orden):
    """Manda una orden al corral. Devuelve False si no hay corral abierto."""
    try:
        with socket.create_connection(("127.0.0.1", PUERTO), timeout=1) as s:
            s.sendall(orden.encode("utf-8"))
        return True
    except OSError:
        return False


def lanzar(orden):
    """Abre el corral en un proceso desacoplado de la consola, con su primera orden."""
    args = [sys.executable, os.path.abspath(__file__), "--corral", orden]
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


def lista():
    return "Bichos: " + ", ".join(BICHOS) + ". También: todos, chau."


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if argv[:1] == ["--corral"]:
        abrir_corral(argv[1] if len(argv) > 1 else "")
        return

    if not argv:
        print(lista())
        return
    clave = "".join(c for c in unicodedata.normalize("NFD", argv[0].lower())
                    if c.isalnum() and not unicodedata.combining(c))
    resto = " ".join(argv[1:]).strip()

    if clave in ("chau", "andate", "basta"):
        print("Todos vuelven al monte." if mandar("chau") else "No había ningún bicho suelto.")
        return
    if clave == "todos":
        orden, aviso = "todos", "Andan todos sueltos por la pantalla."
    elif clave in BICHOS:
        nombre = BICHOS[clave]["nombre"]
        if resto.lower() in ("chau", "andate", "basta"):
            ok = mandar("chau " + clave)
            print(f"{nombre} vuelve al monte." if ok else f"{nombre} no andaba suelto.")
            return
        orden = f"decir {clave} {resto}" if resto else f"soltar {clave}"
        aviso = f"{nombre} anda suelto por la pantalla. Clic derecho sobre él para mandarlo al monte."
    else:
        print(f"No conozco a '{argv[0]}'. {lista()}")
        return

    if mandar(orden):
        print(aviso)
        return
    lanzar(orden)
    for _ in range(40):
        time.sleep(0.2)
        try:
            socket.create_connection(("127.0.0.1", PUERTO), timeout=0.3).close()
            break
        except OSError:
            pass
    print(aviso)


if __name__ == "__main__":
    main(sys.argv[1:])
