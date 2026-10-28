# kvothesson: el Pombero suelto

Plugin para Claude Code. Lo invocás y aparece un Pombero caminando por el borde de
abajo de tu pantalla, que cada tanto te dice algo. Como el clip de Word, pero del monte.

```
/kvothesson:kvothesson
```

## Instalación

```
/plugin marketplace add https://raw.githubusercontent.com/kvothesson/ar-plugins/master/.claude-plugin/marketplace.json
/plugin install kvothesson@ar-plugins
```

Necesita Python 3 con tkinter (viene con Python en Windows y macOS). No instala nada más.

## Uso

| Comando | Qué hace |
|---|---|
| `/kvothesson:kvothesson` | Lo suelta. Si ya anda suelto, le hace decir algo. |
| `/kvothesson:kvothesson chau` | Lo manda de vuelta al monte. |
| `/kvothesson:kvothesson <texto>` | Le hace decir ese texto. |

Sobre el bicho:

- **Clic:** te contesta.
- **Arrastrar y soltar:** se cae hasta el piso.
- **Clic derecho:** abre un menú con "Decí algo", "Quedate quieto" y "Volvé al monte".
- **Hora:** a la hora de la siesta y de madrugada tiene frases propias.

También anda sin Claude: `python bicho/bicho.py`.

## Sumar frases

Las frases están en [`bicho/frases.json`](bicho/frases.json), separadas por momento:

- `saludo`
- `suelta`
- `siesta`
- `noche`
- `toque`
- `caida`
- `chau`

Agregá las tuyas en el grupo que corresponda.

## Cómo funciona

Es una ventana de tkinter sin bordes, siempre arriba y con el fondo transparente:

- **Windows:** se usa `-transparentcolor`.
- **macOS:** se usa `-transparent`.
- **Linux:** queda con fondo oscuro.

El sprite es pixel art de 20x24 dibujado con letras en el código.

Para que haya un solo Pombero a la vez, la ventana escucha en `127.0.0.1:47404`. Las invocaciones que vienen después le mandan las órdenes por ahí.

MIT · Kvothesson
