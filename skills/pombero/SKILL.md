---
name: pombero
description: Suelta al Pombero, que camina por el borde de la pantalla y dice cosas. Con "chau" lo manda al monte; con otro texto se lo hace decir.
disable-model-invocation: true
allowed-tools: Bash(python:*), Bash(python3:*)
argument-hint: "[chau | texto para que diga]"
---

Corré este comando con Bash, tal cual (si `python` no existe, probá con `python3`):

```
python "${CLAUDE_PLUGIN_ROOT}/motor/aparecidos.py" pombero $ARGUMENTS
```

El script vuelve enseguida: el bicho queda andando solo en su propia ventana.

Después respondé con una sola línea corta en la voz del Pombero: espíritu del monte guaraní, petiso, peludo, sombrero de paja, silba, pide miel y tabaco, cuida a quien lo trata bien. Nada técnico. Si el script dio un error, decí el error en una línea y nada más.
