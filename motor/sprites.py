"""Sprites de los bichos, en pixel art escrito con letras.

Cada bicho define sus cuadros como listas de filas del mismo ancho. "." es
transparente; las demás letras son colores de su paleta. Los que miran hacia un
costado se dibujan mirando a la derecha y el motor los espeja.
"""
import math


def _cambiar(filas, fila, nueva):
    filas = list(filas)
    filas[fila] = nueva
    return filas


def _reemplazar(filas, tabla):
    return ["".join(tabla.get(c, c) for c in f) for f in filas]


# --- Pombero: camina ----------------------------------------------------------
_POMBERO = [
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
_POMBERO_QUIETO = _POMBERO + [
    ".....KHHK..KHHK.....",
    ".....KHHK..KHHK.....",
    "....KFFFK..KFFFK....",
    "....KKKKK..KKKKK....",
]
_POMBERO_PASO = _POMBERO + [
    "....KHHK....KHHK....",
    "...KHHK......KHHK...",
    "..KFFFK......KFFFK..",
    "..KKKKK......KKKKK..",
]
POMBERO = {
    "nombre": "Pombero",
    "modo": "camina",
    "velocidad": 1.0,
    "escala": 4,
    "acento": "#ffc05c",
    "espejar": False,
    "paleta": {
        "K": "#1a1208", "S": "#d9b25a", "s": "#a8833a", "h": "#3d2716",
        "H": "#5a3a22", "E": "#ffd75a", "F": "#b07850", "f": "#8a5a3a",
        "M": "#3a0f0f", "P": "#7a2b2b", "Y": "#e0c070",
    },
    "cuadros": {
        "quieto": _POMBERO_QUIETO,
        "paso": _POMBERO_PASO,
        "parpadeo": _cambiar(_POMBERO_QUIETO, 8, "...KhKKhhhhhhKKhK..."),
        "habla": _cambiar(_POMBERO_QUIETO, 10, "...KHFfFKMMKFfFHK..."),
        "habla_paso": _cambiar(_POMBERO_PASO, 10, "...KHFfFKMMKFfFHK..."),
    },
}

# --- Luz Mala: flota y titila -------------------------------------------------
_LUZ = [
    "....oooooo....",
    "..ooOOOOOOoo..",
    ".oOOYYYYYYOOo.",
    ".oOYYYYYYYYOo.",
    "oOYYWWWWWWYYOo",
    "oOYWWWWWWWWYOo",
    "oOYWKWWWWKWYOo",
    "oOYWWWWWWWWYOo",
    "oOYWWWWWWWWYOo",
    "oOYYWWWWWWYYOo",
    ".oOYYYYYYYYOo.",
    ".oOOYYYYYYOOo.",
    "..ooOOOOOOoo..",
    "....oooooo....",
]
_LUZ_HABLA = _cambiar(_LUZ, 8, "oOYWWWKKWWWYOo")
_TENUE = {"o": ".", "O": "o"}
LUZMALA = {
    "nombre": "Luz Mala",
    "modo": "flota",
    "velocidad": 1.0,
    "escala": 4,
    "acento": "#ffe680",
    "espejar": False,
    "paleta": {"W": "#fffbe8", "Y": "#ffe680", "O": "#ffb347", "o": "#b0602a", "K": "#5a3a10"},
    "cuadros": {
        "quieto": _LUZ,
        "paso": _reemplazar(_LUZ, _TENUE),
        "parpadeo": _cambiar(_LUZ, 6, "oOYWWWWWWWWYOo"),
        "habla": _LUZ_HABLA,
        "habla_paso": _reemplazar(_LUZ_HABLA, _TENUE),
    },
}

# --- Lobizón: anda en cuatro patas --------------------------------------------
_LOBO = [
    "...............K...K....",
    "..............KgK.KgK...",
    "..............KGGKKGGK..",
    "..............KGGGGEGGK.",
    ".K............KGGGGGGGGK",
    "KgK.K.K.K.K..KGGGGGGKKKK",
    "KgK.KKKKKKKKKGGGGGGGGGGK",
    ".KgKGGGGGGGGGGGGGGGGGK..",
    "..KGGGGGGGGGGGGGGGGKKK..",
    "..KGGGGGGGGGGGGGGGGK....",
    "..KGgGGGGGGGGGGGGgGK....",
    "..KLLLLLLLLLLLLLLLLK....",
    "...KKKKKKKKKKKKKKKK.....",
]
_LOBO_QUIETO = _LOBO + [
    "...KgK.KgK....KgK.KgK...",
    "...KgK.KgK....KgK.KgK...",
    "...KKK.KKK....KKK.KKK...",
]
_LOBO_PASO = _LOBO + [
    "..KgK...KgK..KgK...KgK..",
    ".KgK.....KgKKgK.....KgK.",
    ".KKK.....KKKKKK.....KKK.",
]


def _lobo_habla(filas):
    filas = _cambiar(filas, 6, "KgK.KKKKKKKKKGGGGGGMTMTK")
    return _cambiar(filas, 7, ".KgKGGGGGGGGGGGGGGGMMMK.")


LOBIZON = {
    "nombre": "Lobizón",
    "modo": "camina",
    "velocidad": 1.6,
    "escala": 4,
    "acento": "#a9b0ff",
    "espejar": True,
    "paleta": {
        "K": "#141414", "G": "#6b6b73", "g": "#4a4a52", "L": "#9a9aa3",
        "E": "#ff5a3c", "M": "#8a1c1c", "T": "#eeeeee",
    },
    "cuadros": {
        "quieto": _LOBO_QUIETO,
        "paso": _LOBO_PASO,
        "parpadeo": _cambiar(_LOBO_QUIETO, 3, "..............KGGGGGGGK."),
        "habla": _lobo_habla(_LOBO_QUIETO),
        "habla_paso": _lobo_habla(_LOBO_PASO),
    },
}

# --- Mainumby: vuela a los saltos ---------------------------------------------
_PICA_ARRIBA = [
    "....WWW.........",
    "....WWWW........",
    ".....WWWW..KK...",
    "......WWKKVVK...",
    ".......KVVVEKBBB",
    "....KKKVVVVRK...",
    "..KKvVVVVVRRK...",
    ".KvvVVVVVVVK....",
    "KvvKKVVVVKK.....",
    "KK...KKKK.......",
    "................",
]
_PICA_ABAJO = [
    "................",
    "................",
    "...........KK...",
    "........KKVVK...",
    ".......KVVVEKBBB",
    "....KKKVVVVRK...",
    "..KKvVVVVVRRK...",
    ".KvvWWWWVVVK....",
    "KvvKWWWWWKK.....",
    "KK...WWWW.......",
    "......WW........",
]
_PICO_ABIERTO = "....KKKVVVVRKB.."
MAINUMBY = {
    "nombre": "Mainumby",
    "modo": "vuela",
    "velocidad": 1.0,
    "escala": 4,
    "acento": "#2fbf71",
    "espejar": True,
    "paleta": {
        "K": "#0e1a14", "V": "#2fbf71", "v": "#1d7a48", "R": "#ff3d7f",
        "B": "#2a2a2a", "W": "#9ee8c0", "E": "#ffffff",
    },
    "cuadros": {
        "quieto": _PICA_ARRIBA,
        "paso": _PICA_ABAJO,
        "parpadeo": _cambiar(_PICA_ARRIBA, 4, ".......KVVVVKBBB"),
        "habla": _cambiar(_PICA_ARRIBA, 5, _PICO_ABIERTO),
        "habla_paso": _cambiar(_PICA_ABAJO, 5, _PICO_ABIERTO),
    },
}

# --- Mbói: repta --------------------------------------------------------------
_CABEZA = {2: "KKKK....", 3: "NNENK...", 4: "NNNNNK..", 5: "YYYYK...", 6: "KKKK...."}
_LENGUA = {4: "NNNNNKTT"}


def _vibora(fase, ojo="E", lengua=False):
    ancho, alto, largo = 30, 10, 22
    grilla = [["."] * ancho for _ in range(alto)]
    for x in range(largo):
        amp = 2.0 * math.sin(math.pi * x / largo)
        c = 4 + round(amp * math.sin(x * 0.55 - fase))
        grueso = x > 2
        grilla[c - 1][x] = "K"
        grilla[c][x] = "N" if grueso else "n"
        if grueso:
            grilla[c + 1][x] = "Y"
            grilla[c + 2][x] = "K"
        else:
            grilla[c + 1][x] = "K"
    for y, fila in _CABEZA.items():
        if lengua and y in _LENGUA:
            fila = _LENGUA[y]
        for i, ch in enumerate(fila):
            if ch != ".":
                grilla[y][largo + i] = "N" if ch == "E" and ojo != "E" else ch
    return ["".join(f) for f in grilla]


MBOI = {
    "nombre": "Mbói",
    "modo": "repta",
    "velocidad": 0.6,
    "escala": 4,
    "acento": "#ff6b6b",
    "espejar": True,
    "paleta": {"K": "#0f1a0f", "N": "#3f8f3a", "n": "#2a6326", "Y": "#c9d66a", "E": "#ff5050", "T": "#ff3d7f"},
    "cuadros": {
        "quieto": _vibora(0),
        "paso": _vibora(math.pi),
        "parpadeo": _vibora(0, ojo="N"),
        "habla": _vibora(0, lengua=True),
        "habla_paso": _vibora(math.pi, lengua=True),
    },
}

# --- Añá: camina y de golpe aparece en otro lado ------------------------------
_ANA = [
    "..H..........H..",
    "..HK........KH..",
    "...HKKKKKKKKH...",
    "...KDDDDDDDDK...",
    "..KDDDDDDDDDDK..",
    "..KDRRDDDDRRDK..",
    "..KDDRDDDDRDDK..",
    "..KDDDDDDDDDDK..",
    "..KDDKWKKWKDDK..",
    "...KDDKKKKDDK...",
    "....KKDDDDKK....",
    "..KCCKDDDDKCCK..",
    ".KCCKDDDDDDKCCK.",
    ".KCKDDDDDDDDKCK.",
    "KCCKDdDDDDdDKCCK",
    "KCCKDDDDDDDDKCCK",
    ".KKKDDDDDDDDKKK.",
]
_ANA_QUIETO = _ANA + ["....KDK..KDK....", "....KDK..KDK....", "...KKKK..KKKK..."]
_ANA_PASO = _ANA + ["...KDK....KDK...", "..KDK......KDK..", ".KKKK......KKKK."]
_ANA_BOCA = "..KDDKRRRRKDDK.."
ANA = {
    "nombre": "Añá",
    "modo": "aparece",
    "velocidad": 1.1,
    "escala": 4,
    "acento": "#ff2a2a",
    "espejar": False,
    "paleta": {
        "K": "#0a0610", "D": "#3b1f4f", "d": "#261433", "R": "#ff2a2a",
        "H": "#d8d0c0", "W": "#f0f0f0", "C": "#6b0f1a",
    },
    "cuadros": {
        "quieto": _ANA_QUIETO,
        "paso": _ANA_PASO,
        "parpadeo": _cambiar(_cambiar(_ANA_QUIETO, 5, "..KDKKDDDDKKDK.."), 6, "..KDDDDDDDDDDK.."),
        "habla": _cambiar(_ANA_QUIETO, 8, _ANA_BOCA),
        "habla_paso": _cambiar(_ANA_PASO, 8, _ANA_BOCA),
    },
}

# --- Irupé: deriva despacio sobre su pedacito de agua -------------------------
_IRUPE = [
    "...........KPPK...........",
    "..........KPpPpK..........",
    ".........KPpYYpPK.........",
    "........KPPpYYpPPK........",
    ".KK.....KKPPPPPPKK.....KK.",
    "KllK..KKLLLLLLLLLLKK..KllK",
    "KlLLKKLLLLKLLLLKLLLLKKLLlK",
    ".Kl" + "L" * 20 + "lK.",
    "..KK" + "l" * 18 + "KK..",
]
_AGUA = "aAAaAAAAaAAAAAaAAAAaAAAAaA"
_IRUPE_QUIETO = _IRUPE + [_AGUA]
_IRUPE_PASO = _IRUPE + [_AGUA[2:] + _AGUA[:2]]
_IRUPE_BOCA = ".Kl" + "L" * 9 + "KK" + "L" * 9 + "lK."
IRUPE = {
    "nombre": "Irupé",
    "modo": "repta",
    "velocidad": 0.25,
    "escala": 4,
    "acento": "#f08fb8",
    "espejar": False,
    "paleta": {
        "K": "#0c1f14", "L": "#3fa34d", "l": "#b0413e", "P": "#f6f0f5",
        "p": "#f08fb8", "Y": "#ffd34d", "A": "#3a7fbf", "a": "#8fc3ef",
    },
    "cuadros": {
        "quieto": _IRUPE_QUIETO,
        "paso": _IRUPE_PASO,
        "parpadeo": _cambiar(_IRUPE_QUIETO, 6, "KlLLKKLLLLLLLLLLLLLLKKLLlK"),
        "habla": _cambiar(_IRUPE_QUIETO, 7, _IRUPE_BOCA),
        "habla_paso": _cambiar(_IRUPE_PASO, 7, _IRUPE_BOCA),
    },
}

# --- Ka'a Yarýi: un mate con patas, el espíritu de la yerba -------------------
_MATE = [
    "..........B.....",
    ".........B......",
    "...y..y.B..y....",
    "..yYyyYyByYy....",
    "...KVVVVBVVK....",
    "..KVVVVVVVVVK...",
    "..KGGGGGGGGGK...",
    ".KGGGGGGGGGGGK..",
    ".KGGEKGGGEKGGK..",
    "KGGGGGGGGGGGGGK.",
    "KGgGGGGMGGGGgGK.",
    "KGGgGGGGGGGgGGK.",
    "KGGGggggggggGGK.",
    ".KGGGGGGGGGGGK..",
    "..KgGGGGGGGgK...",
    "...KKKKKKKKK....",
]
_MATE_QUIETO = _MATE + ["....KgK.KgK.....", "...KKKK.KKKK...."]
_MATE_PASO = _MATE + ["...KgK...KgK....", "..KKKK....KKKK.."]
_MATE_BOCA = "KGgGGGMMMGGGgGK."
KAAYARYI = {
    "nombre": "Ka'a Yarýi",
    "modo": "camina",
    "velocidad": 0.7,
    "escala": 4,
    "acento": "#8fd14f",
    "espejar": True,
    "paleta": {
        "K": "#1a120a", "G": "#8b5a2b", "g": "#5e3b1a", "Y": "#6fa83a",
        "y": "#4a7a22", "B": "#c8c8d0", "E": "#fff2c0", "M": "#3a1a0a", "V": "#d9b25a",
    },
    "cuadros": {
        "quieto": _MATE_QUIETO,
        "paso": _MATE_PASO,
        "parpadeo": _cambiar(_MATE_QUIETO, 8, ".KGGKKGGGKKGGK.."),
        "habla": _cambiar(_MATE_QUIETO, 10, _MATE_BOCA),
        "habla_paso": _cambiar(_MATE_PASO, 10, _MATE_BOCA),
    },
}

BICHOS = {
    "pombero": POMBERO,
    "luzmala": LUZMALA,
    "lobizon": LOBIZON,
    "mainumby": MAINUMBY,
    "mboi": MBOI,
    "ana": ANA,
    "irupe": IRUPE,
    "kaayaryi": KAAYARYI,
}


def revisar():
    """Comprueba que cada cuadro sea rectangular y use colores de su paleta."""
    for clave, b in BICHOS.items():
        anchos = set()
        for nombre, filas in b["cuadros"].items():
            for f in filas:
                anchos.add(len(f))
                for c in f:
                    assert c == "." or c in b["paleta"], (clave, nombre, c)
            assert len({len(f) for f in filas}) == 1, (clave, nombre)
        assert len(anchos) == 1, (clave, anchos)


if __name__ == "__main__":
    revisar()
    print("ok")
