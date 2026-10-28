---
name: aparecidos
description: Suelta a todos los aparecidos del folklore en la pantalla, o los manda a todos al monte con "chau". Sin argumentos los suelta a todos.
disable-model-invocation: true
allowed-tools: Bash(python:*), Bash(python3:*)
argument-hint: "[todos | chau]"
---

Si `$ARGUMENTS` está vacío, usá `todos`. Corré con Bash (si `python` no existe, probá con `python3`):

```
python "${CLAUDE_PLUGIN_ROOT}/motor/aparecidos.py" <todos o chau>
```

El script vuelve enseguida: los bichos quedan andando solos.

Después respondé con una sola línea corta: si los soltaste, que se note que llegan el Pombero, la Luz Mala, el Lobizón, la Mainumby, el Mbói, el Añá, el Irupé y el Ka'a Yarýi; si los mandaste al monte, una despedida. Nada técnico.
