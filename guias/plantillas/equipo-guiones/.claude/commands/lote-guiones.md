---
description: Produce un lote de guiones para Meta Ads con el equipo de agentes (estratega, guionistas en paralelo, revisor, adaptador bilingüe y productor).
argument-hint: <carpeta-del-cliente> [número de guiones] [idiomas: ES | EN | ES+EN]
disable-model-invocation: true
---

Produce un lote de guiones con el equipo de agentes de `.claude/agents/`.

**Encargo**
- Carpeta del cliente: «$0»
- Número de guiones: «$1». Si está vacío, usa el que pida el brief; si el brief no dice, 10.
- Idiomas: «$2». Si está vacío, usa los del brief; si el brief no dice, ES.

Tú coordinas. **No escribas ni corrijas guiones tú mismo**: eso lo hacen los agentes. Pasa a cada
agente las rutas completas que necesita, porque no ve esta conversación.

## Fase 0 · Preparación

1. Comprueba que la carpeta del cliente existe y tiene un brief o documentos del cliente. Si no
   hay nada, detente y pide el brief. No inventes un cliente.
2. Comprueba que la skill **guion-creator** está disponible. Si no, detente y avísame.
3. Crea la carpeta del lote: `<cliente>/Guiones/Lote-<AAAA-MM-DD>/`. Si ya existe, añade `-2`,
   `-3`…

## Fase 1 · Plan

Lanza **estratega-de-lote** con la carpeta del cliente, la del lote, el número de guiones y los
idiomas. Cuando termine, muéstrame la tabla de asignación y los pendientes, y **pregúntame si
sigo**. Si pido cambios, vuelve a lanzar al estratega con ellos.

## Fase 2 · Guiones en paralelo

Lanza **un guionista por grupo** de la sección F del plan, **todos a la vez**. A cada uno pásale
la carpeta del lote, sus guiones (por ejemplo G01 y G02) y su formato.

## Fase 3 · Revisión

Cuando terminen todos, lanza **revisor-de-guiones** sobre el lote completo.

## Fase 4 · Correcciones (máximo 2 rondas)

Si hay guiones con CORREGIR, lanza un **guionista por formato afectado**, en paralelo, con la
ruta de `revision.md` y la lista de sus guiones a corregir. Después lanza de nuevo el revisor solo
sobre los corregidos, y pídele que vuelva a mirar la diversidad del lote. Si tras dos rondas un
guion sigue sin aprobar, déjalo marcado para revisión humana y sigue.

## Fase 5 · Adaptación bilingüe (solo si el lote es ES+EN)

Lanza **adaptador-en** en paralelo, uno por grupo, sobre los guiones aprobados. Luego lanza el
revisor solo sobre las adaptaciones (Scroll-Stop Test, redacción oral en el idioma destino,
duración y compliance).

## Fase 6 · Entrega

Lanza **productor**. Al final respóndeme con:
- la ruta del lote y de `LOTE-FINAL.md` y `plan-de-rodaje.md`;
- la tabla índice;
- los guiones que quedaron para revisión humana;
- los `[PENDIENTE]` y `[DATO A VERIFICAR]` abiertos.
