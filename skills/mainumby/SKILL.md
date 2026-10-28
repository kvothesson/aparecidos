---
name: mainumby
description: Suelta a la Mainumby, un picaflor que vuela a los saltos por la pantalla y trae recados. Con "chau" lo manda al monte; con otro texto se lo hace decir.
disable-model-invocation: true
allowed-tools: Bash(python:*), Bash(python3:*)
argument-hint: "[chau | texto para que diga]"
---

Corré este comando con Bash, tal cual (si `python` no existe, probá con `python3`):

```
python "${CLAUDE_PLUGIN_ROOT}/motor/aparecidos.py" mainumby $ARGUMENTS
```

El script vuelve enseguida: el bicho queda andando solo en su propia ventana.

Después respondé con una sola línea corta en la voz de la Mainumby: picaflor guaraní que lleva mensajes y almas; apurada, trae recados del monte. Nada técnico. Si el script dio un error, decí el error en una línea y nada más.
