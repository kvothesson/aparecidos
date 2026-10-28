---
name: ana
description: Suelta al Añá, un diablito que camina y de golpe desaparece y aparece en otro lado de la pantalla. Con "chau" lo manda al monte; con otro texto se lo hace decir.
disable-model-invocation: true
allowed-tools: Bash(python:*), Bash(python3:*)
argument-hint: "[chau | texto para que diga]"
---

Corré este comando con Bash, tal cual (si `python` no existe, probá con `python3`):

```
python "${CLAUDE_PLUGIN_ROOT}/motor/aparecidos.py" ana $ARGUMENTS
```

El script vuelve enseguida: el bicho queda andando solo en su propia ventana.

Después respondé con una sola línea corta en la voz del Añá: espíritu del mal guaraní, astuto, no destruye por destruir sino que prueba qué tan frágil es todo; burlón. Nada técnico. Si el script dio un error, decí el error en una línea y nada más.
