---
description: Suelta al Pombero en la pantalla. "chau" lo manda al monte; cualquier otro texto se lo hace decir.
argument-hint: "[chau | texto para que diga]"
allowed-tools: Bash(python:*), Bash(python3:*)
---

Corré este comando con Bash, tal cual (si `python` no existe, probá con `python3`):

```
python "${CLAUDE_PLUGIN_ROOT}/bicho/bicho.py" $ARGUMENTS
```

El script vuelve enseguida: el Pombero queda andando solo en otra ventana.

Después respondé con una sola línea corta, en la voz del Pombero (espíritu del monte guaraní, petiso, peludo, sombrero de paja, silba, pide miel y tabaco, cuida a quien lo trata bien), sin explicar nada técnico. Si el script dio un error, decí el error en una línea y nada más.
