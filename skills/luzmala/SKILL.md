---
name: luzmala
description: Suelta a la Luz Mala, que flota y titila por la pantalla y dice cosas. Con "chau" lo manda al monte; con otro texto se lo hace decir.
disable-model-invocation: true
allowed-tools: Bash(python:*), Bash(python3:*)
argument-hint: "[chau | texto para que diga]"
---

Corré este comando con Bash, tal cual (si `python` no existe, probá con `python3`):

```
python "${CLAUDE_PLUGIN_ROOT}/motor/aparecidos.py" luzmala $ARGUMENTS
```

El script vuelve enseguida: el bicho queda andando solo en su propia ventana.

Después respondé con una sola línea corta en la voz de la Luz Mala: luz misteriosa del campo que asusta a los paisanos y marca donde hay tesoros enterrados; coqueta, un poco tétrica. Nada técnico. Si el script dio un error, decí el error en una línea y nada más.
