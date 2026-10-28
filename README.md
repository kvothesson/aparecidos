# aparecidos

Los aparecidos del folklore del Universo Austral se dejan ver en tu pantalla. Caminan,
flotan, vuelan o reptan por el borde de abajo, y cada tanto te dicen algo. Como el
clip de Word, pero del monte.

Son los mismos bichos de [daemons](https://github.com/kvothesson/daemons-plugin),
en versión visible.

## Instalación

```
/plugin marketplace add https://raw.githubusercontent.com/kvothesson/ar-plugins/master/.claude-plugin/marketplace.json
/plugin install aparecidos@ar-plugins
```

Necesita Python 3 con tkinter. Viene con Python en Windows y macOS, y no instala nada más.

## Los aparecidos

| Comando | Quién | Cómo anda |
|---|---|---|
| `/aparecidos:pombero` | Pombero | Camina con su sombrero de paja y te pide miel. |
| `/aparecidos:luzmala` | Luz Mala | Flota y titila. Donde se apaga hay un tesoro. |
| `/aparecidos:lobizon` | Lobizón | Corre en cuatro patas. De noche anda más rápido. |
| `/aparecidos:mainumby` | Mainumby | Picaflor que vuela a los saltos y trae recados. |
| `/aparecidos:mboi` | Mbói | Serpiente que repta y se fija en tus patrones. |
| `/aparecidos:ana` | Añá | Camina y de golpe aparece en otro lado. |
| `/aparecidos:irupe` | Irupé | Flor del agua que deriva despacio y ordena. |
| `/aparecidos:kaayaryi` | Ka'a Yarýi | Un mate con patas que cuida tu foco. |
| `/aparecidos` | Todos | Los suelta a todos. Con `chau`, se vuelven todos. |

Cada comando acepta argumentos:

- **Sin nada:** suelta al aparecido. Si ya andaba suelto, le hace decir algo.
- **`chau`:** lo manda de vuelta al monte.
- **Cualquier otro texto:** se lo hace decir. Por ejemplo: `/aparecidos:pombero guardá todo`.

## Sobre los bichos

- **Clic:** te contesta.
- **Arrastrar y soltar:** los que caminan se caen al piso. Los que flotan o vuelan se quedan donde los dejaste.
- **Clic derecho:** abre un menú con "Decí algo", "Quedate quieto", "Volvé al monte" y "Que vuelvan todos".
- **Hora:** a la hora de la siesta y de madrugada tienen frases propias.
- **De a uno:** si hay varios sueltos, esperan a que termine de hablar el que está hablando.

Sin Claude también andan:

```
python motor/aparecidos.py todos
```

## Sumar frases o bichos

- **Frases:** están en `motor/frases/<bicho>.json`, agrupadas por momento: `saludo`, `suelta`, `siesta`, `noche`, `toque`, `caida` y `chau`.
- **Sprites:** están en `motor/sprites.py`. Son pixel art escrito con letras, una paleta por bicho y cinco cuadros: quieto, paso, parpadeo, habla y habla con paso.
- **Bicho nuevo:** necesita su entrada en `BICHOS`, su archivo de frases y su `skills/<bicho>/SKILL.md`.

## Cómo funciona

Cada aparecido es una ventana de tkinter sin bordes, siempre arriba y con el fondo transparente:

- **Windows:** se usa `-transparentcolor`.
- **macOS:** se usa `-transparent`.
- **Linux:** queda con fondo oscuro.

Todos viven en un mismo proceso, el corral, que escucha en `127.0.0.1:47404`. Cada comando le manda una orden. Si el corral no está abierto, lo abre. Cuando se va el último bicho, el corral se cierra solo.

MIT · Kvothesson
