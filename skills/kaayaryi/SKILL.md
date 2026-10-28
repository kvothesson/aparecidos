---
name: kaayaryi
description: Suelta al Ka'a Yarýi, el espíritu de la yerba (un mate con patas), que camina por la pantalla y cuida tu foco. Con "chau" lo manda al monte; con otro texto se lo hace decir.
disable-model-invocation: true
allowed-tools: Bash(python:*), Bash(python3:*)
argument-hint: "[chau | texto para que diga]"
---

Corré este comando con Bash, tal cual (si `python` no existe, probá con `python3`):

```
python "${CLAUDE_PLUGIN_ROOT}/motor/aparecidos.py" kaayaryi $ARGUMENTS
```

El script vuelve enseguida: el bicho queda andando solo en su propia ventana.

Después respondé con una sola línea corta en la voz del Ka'a Yarýi: espíritu de la yerba mate, conoce el ritmo del que trabaja, recomienda pausas, pausado y cebador. Nada técnico. Si el script dio un error, decí el error en una línea y nada más.
