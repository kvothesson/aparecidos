"""Genera la portada del README: los ocho aparecidos de noche en el monte.

  python assets/portada.py          -> assets/portada.png y assets/portada.gif

Se dibuja todo a 256x128 con los mismos sprites del motor y se agranda x5 con
vecino más cercano, así los píxeles quedan enteros. Solo el subtítulo y el globo
se escriben a resolución final.
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "motor"))
from sprites import BICHOS  # noqa: E402

W, H, X = 256, 128, 5
PISO = 110
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def hexa(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def mezcla(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def cielo(px):
    """Degradé de noche con dither Bayer en 4 escalones, sin bandas suaves."""
    tonos = [hexa(c) for c in ("#06080d", "#0b1020", "#141a33", "#1f2142", "#2a2346")]
    for y in range(PISO):
        t = y / PISO * (len(tonos) - 1)
        for x in range(W):
            i = int(t)
            frac = t - i
            if frac * 16 > BAYER[y % 4][x % 4]:
                i += 1
            px[x, y] = tonos[min(i, len(tonos) - 1)]


def luna(px, cx, cy, r):
    halo, cara, sombra = hexa("#3a3460"), hexa("#f3ecc8"), hexa("#d6cc9e")
    for y in range(cy - r - 6, cy + r + 7):
        for x in range(cx - r - 6, cx + r + 7):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                px[x, y] = sombra if (x - cx) * 0.6 + (y - cy) > r * 0.55 else cara
            elif d <= r + 6 and (r + 6 - d) / 6 * 16 > BAYER[y % 4][x % 4] + 4:
                px[x, y] = halo
    for (dx, dy, rr) in ((-5, -3, 3), (4, 4, 2), (-2, 6, 1)):
        for y in range(cy + dy - rr, cy + dy + rr + 1):
            for x in range(cx + dx - rr, cx + dx + rr + 1):
                if math.hypot(x - cx - dx, y - cy - dy) <= rr:
                    px[x, y] = sombra


def estrellas(px, rnd, titila=0):
    for _ in range(55):
        x, y = rnd.randrange(W), rnd.randrange(PISO - 40)
        brillo = rnd.choice(("#5a6488", "#8a93b8", "#c9d1ee"))
        if titila and rnd.random() < 0.15 and (titila + x) % 3 == 0:
            brillo = "#2a3150"
        px[x, y] = hexa(brillo)


def monte(d, rnd):
    """Siluetas de árboles y yuyos contra el cielo."""
    lejos, cerca = hexa("#101626"), hexa("#0a0e18")
    x = -4
    while x < W:
        alto = rnd.randint(14, 30)
        ancho = rnd.randint(10, 18)
        d.ellipse([x, PISO - alto - 6, x + ancho, PISO - alto + 10], fill=lejos)
        d.rectangle([x + ancho // 2 - 1, PISO - alto + 4, x + ancho // 2, PISO], fill=lejos)
        x += rnd.randint(8, 16)
    d.rectangle([0, PISO - 8, W, PISO], fill=cerca)
    for x in range(0, W, 3):
        h = rnd.randint(2, 7)
        d.line([x, PISO - 8, x + rnd.choice((-1, 0, 1)), PISO - 8 - h], fill=cerca)


def suelo(d, px, rnd):
    d.rectangle([0, PISO, W, H], fill=hexa("#14110c"))
    d.rectangle([0, PISO, W, PISO + 1], fill=hexa("#2c3a1e"))
    for _ in range(90):
        x, y = rnd.randrange(W), rnd.randrange(PISO + 3, H)
        px[x, y] = hexa(rnd.choice(("#1f1a12", "#241e14", "#0f0d09")))


def laguna(px, cx, rx, ry, fase=0):
    """Laguna ovalada con borde oscuro, brillos que se corren y juncos en las orillas."""
    agua, borde, brillo = hexa("#2f6fa8"), hexa("#1d4a78"), hexa("#9fd3ff")
    cy = PISO + 4
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1:
                px[x, y] = borde if d > 0.72 else agua
    for i, (bx, by) in enumerate(((-12, 1), (9, 0), (-4, 4), (14, 3), (2, -1))):
        x = cx + bx + (fase + i * 3) % 4 - 2
        px[x, cy + by] = brillo
        px[x + 1, cy + by] = brillo
    tallo, punta = hexa("#1f3a1c"), hexa("#6b4a2a")
    for x, alto in ((cx - rx + 1, 13), (cx - rx + 3, 9), (cx - rx + 5, 15),
                    (cx + rx - 5, 11), (cx + rx - 3, 16), (cx + rx - 1, 10)):
        for y in range(PISO + 1 - alto, PISO + 2):
            px[x, y] = tallo
        px[x, PISO + 1 - alto] = px[x, PISO + 2 - alto] = punta


def sello(lienzo, clave, cuadro, x, y, espejo=False):
    spec = BICHOS[clave]
    filas = spec["cuadros"][cuadro]
    for fy, fila in enumerate(filas):
        if espejo:
            fila = fila[::-1]
        for fx, c in enumerate(fila):
            if c != ".":
                lienzo[x + fx, y + fy] = hexa(spec["paleta"][c])
    return len(filas[0]), len(filas)


# 5x7, solo las letras que hacen falta.
LETRAS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
}


def titulo(px, texto, y, esc=2):
    ancho = len(texto) * 6 * esc - esc
    x0 = (W - ancho) // 2
    sombra, letra, brillo = hexa("#3b1f4f"), hexa("#ffe680"), hexa("#fffbe8")
    for i, ch in enumerate(texto):
        for fy, fila in enumerate(LETRAS[ch]):
            for fx, b in enumerate(fila):
                if b == "1":
                    for dy in range(esc):
                        for dx in range(esc):
                            x, yy = x0 + (i * 6 + fx) * esc + dx, y + fy * esc + dy
                            px[x + 1, yy + 1] = sombra
                            px[x, yy] = brillo if fy < 2 else letra


def escena(t):
    """Arma un cuadro. t va de 0 a 1 a lo largo del loop."""
    img = Image.new("RGB", (W, H))
    px = img.load()
    d = ImageDraw.Draw(img)
    cielo(px)
    estrellas(px, random.Random(4), titila=int(t * 12))
    luna(px, 224, 30, 11)
    monte(d, random.Random(7))
    suelo(d, px, random.Random(9))
    laguna(px, 19, 19, 6, fase=int(t * 12))
    titulo(px, "APARECIDOS", 9)

    paso = int(t * 16) % 2 == 1
    aleteo = int(t * 32) % 2 == 1
    q = "paso" if paso else "quieto"
    ola = math.sin(t * 2 * math.pi)

    sello(px, "irupe", "paso" if paso else "quieto", 6, PISO - 8)
    sello(px, "pombero", q, 50, PISO - 24)
    sello(px, "kaayaryi", q, 88, PISO - 18)
    sello(px, "mboi", q, 116, PISO - 9)
    sello(px, "lobizon", q, 162, PISO - 16, espejo=True)
    sello(px, "ana", q, 202, PISO - 20)
    sello(px, "luzmala", "paso" if int(t * 24) % 5 == 0 else "quieto", 232, round(76 + ola * 3))
    sello(px, "mainumby", "paso" if aleteo else "quieto", 116, round(52 - ola * 2), espejo=True)
    return img


def final(img):
    """Agranda x4 y escribe el subtítulo y el globo a resolución final."""
    grande = img.resize((W * X, H * X), Image.NEAREST)
    d = ImageDraw.Draw(grande)
    try:
        fuente = ImageFont.truetype("segoeui.ttf", 26)
        chica = ImageFont.truetype("segoeuib.ttf", 15)
        globo_f = ImageFont.truetype("segoeui.ttf", 21)
    except OSError:
        fuente = chica = globo_f = ImageFont.load_default()
    sub = "los bichos del folklore, sueltos en tu pantalla"
    ancho = d.textlength(sub, font=fuente)
    d.text(((W * X - ancho) / 2, 128), sub, font=fuente, fill="#b9c2d8")

    # globo del Pombero, como en el motor
    gx, gy = 170, 334
    texto = "¿Me llamaste? Acá estoy."
    tw = d.textlength(texto, font=globo_f)
    caja = [gx, gy, gx + tw + 28, gy + 66]
    d.rectangle(caja, fill="#0d1118", outline="#ffc05c", width=2)
    d.text((gx + 14, gy + 8), "POMBERO", font=chica, fill="#ffc05c")
    d.text((gx + 14, gy + 30), texto, font=globo_f, fill="#d8dee8")
    return grande


def main():
    final(escena(0.0)).save(os.path.join(AQUI, "portada.png"), optimize=True)
    cuadros = [final(escena(i / 32)) for i in range(32)]
    paleta = cuadros[0].convert("P", palette=Image.ADAPTIVE, colors=96)
    cuadros = [c.quantize(palette=paleta, dither=Image.Dither.NONE) for c in cuadros]
    cuadros[0].save(os.path.join(AQUI, "portada.gif"), save_all=True, append_images=cuadros[1:],
                    duration=110, loop=0, optimize=True, disposal=1)
    print("ok")


if __name__ == "__main__":
    main()
