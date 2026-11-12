---
name: efectos-sonido-reels
description: Planea los efectos de sonido (SFX) de un reel, short o TikTok ya editado. Mira la edición (cortes, textos que aparecen, revelaciones, pausas de la voz) y entrega un mapa de sonido por timecode — whooshes, risers, pops, tecleo, impactos, flashes, foley y ambiente, en capas — con los términos exactos para buscarlos en Envato y el volumen de cada uno, listo para montarlo en Premiere Pro o DaVinci Resolve. Úsala siempre que alguien quiera ponerle efectos de sonido, SFX, "sonidos", sound design o "más ritmo / impacto / dinamismo" a un reel, short, TikTok o video vertical, o comparta un video editado preguntando qué sonidos usar y dónde, aunque no diga "efectos de sonido" ni "Envato".
---

# Efectos de sonido para reels

El objetivo es que un reel ya editado suene "premium": cada momento importante tiene un sonido que lo empuja, sincronizado al fotograma, sin tapar la voz y sin saturar. Lo que entregas es un **mapa de sonido**: qué efecto va en cada momento, por qué, cómo encontrarlo en Envato y a qué volumen. La persona descarga los sonidos de su cuenta de Envato y los coloca en Premiere Pro o DaVinci Resolve siguiendo el mapa.

## Estilo de referencia

Los reels que este equipo toma como ejemplo usan diseño sonoro **en capas**, no un sonido suelto por corte. En un desglose de DaVinci de 12 segundos había unas 12 pistas de SFX:
- **Foley literal**: un reloj cuando la voz habla del tiempo, páginas que pasan en un montaje de fotos, el flash de una cámara cargando cuando aparece una cámara.
- **Capas de diseño**: risers y whooshes largos que suben hasta un "grand hit" en el momento clave.
- **Ambiente**: tono de sala (room tone) y una cola de reverb que asientan la escena siguiente.

Las librerías que les gustan nombran los efectos por función: *digital text*, *typing*, *data*, *digital*, *suspense riser*, *charge*, *flash*, *whoosh*, *glitch*, *impact*. Apunta a ese nivel: pocas ideas, bien sincronizadas y apiladas donde importa.

## Flujo

### 1. Conseguir la edición
Lo ideal es el video exportado de la edición actual: MP4 con voz y música, aunque sea en baja calidad. Si solo hay guion o una descripción de escenas, salta al paso 3 y usa los tiempos que te den. Si no hay tiempos, ordena el mapa por escena.

### 2. Analizar el video
```bash
python <carpeta-de-esta-skill>/scripts/analizar_reel.py "<video>" [--out "<carpeta>"]
```
Por defecto escribe en `<video>_sfx/`, junto al video. Necesita `ffmpeg` (macOS: `brew install ffmpeg`; Windows: `winget install ffmpeg`) y `pip install numpy pillow`. Genera:
- `hoja_eventos.jpg`: un fotograma por evento detectado, con número, tipo y timecode. **Míralo con Read**: es tu forma de "ver" el reel.
- `hoja_general.jpg`: fotogramas repartidos por todo el reel, para entender la historia completa.
- `analisis.json`: duración, fps, eventos y pausas de audio. Cada evento trae `tc`, `tipo`, `audio_db` y `en_pausa`.

Los eventos son **candidatos**, no órdenes. Confírmalos con los fotogramas:
- `corte`: cambia la toma. Es fiable.
- `salto`: cambia casi toda la imagen con la misma paleta. Puede ser un jump cut de alguien hablando, un zoom o punch-in, o movimiento brusco de cámara. Los jump cuts de una persona hablando casi nunca llevan SFX.
- `cambio`: algo aparece de golpe dentro del plano: texto, emoji, sticker, gráfico, número. Es candidato a pop, click, tecleo o digital text.
- `inicio` / `cierre`: el hook y el CTA. Siempre revísalos.
- `pausas`: tramos donde el audio cae mucho. Con voz y música debajo suele ser "la voz se calla". Ahí un efecto puede sonar más fuerte, y es el lugar natural para un riser o un impacto.
- `nota: dos cambios seguidos`: destello, flash o fundido muy corto. El golpe va en el primero.

El detector no oye lo que dice la voz. Si te dan el guion, úsalo para ubicar palabras clave (un número, un "pero", el remate) y poner ahí foley literal o impactos. Si un texto aparece pegado a un corte, el detector solo marca el corte. Revisa en la hoja general si hay un texto que merezca su propio pop.

### 3. Entender el reel antes de poner sonidos
Antes de elegir efectos, decide:
1. **Tipo de reel**: lista de tips, antes/después, promo con precio, historia, tutorial, unboxing...
2. **Momentos clave**: el hook (primer segundo), la revelación, el dato o precio, el remate y el CTA. Ahí van las capas más fuertes.
3. **Paleta sonora**: 3 o 4 familias que se repiten en todo el reel para que suene coherente. Ejemplos de paletas en `references/catalogo-sfx.md`.

### 4. Asignar efectos
Lee `references/catalogo-sfx.md`: familias, cuándo usar cada una, cómo sincronizar, términos de Envato y "pilas" de capas para momentos clave. Criterios:

- **Jerarquía.** Si todo suena, nada destaca. Pon las pilas de 2 a 4 capas en el hook y en la revelación. Los cortes intermedios llevan un whoosh simple, o nada si la música ya marca el ritmo. Como guía: denso en los primeros 2 segundos, luego un acento cada 1.5 a 3 segundos, y aire antes del momento grande.
- **Sincronía al fotograma.** El sonido tiene que pegar con la imagen o se siente amateur:
  - el pico del whoosh cae en el corte (el clip empieza 3 a 8 fotogramas antes);
  - el pop o click va en el primer fotograma del texto;
  - el riser termina justo en la revelación;
  - el hit va en el fotograma del cambio.
- **La voz manda.** Un efecto que tapa una palabra clave arruina el reel. Bajo la voz, los efectos van suaves. En las pausas y en reels sin voz pueden ir fuertes. No pongas un impacto encima de la palabra importante: ponlo en la pausa justo antes o justo después.
- **Literal y emocional.** Combina foley de lo que se ve o se nombra (reloj, cámara, teclado, páginas, dinero) con capas de diseño para la emoción (risers, hits, sub drops). El foley vuelve el reel táctil. El diseño le da peso.
- **Variedad dentro de la paleta.** Alterna 2 o 3 variantes del mismo tipo (whoosh A, B, C) para que no suene mecánico. Por eso conviene bajar *packs*.
- **Contraste.** Un silencio de 5 a 10 fotogramas antes de un hit grande hace que pegue el doble. Puede ser bajar la música o cortar el riser en seco. Sugiérelo cuando encaje.
- **Respeta lo que ya existe.** Si la música ya tiene un golpe en ese punto, o el video ya trae un sonido, no lo dupliques: refuérzalo con una capa grave o déjalo.

### 5. Entregar el mapa
Escribe `mapa_sonido.md` en la carpeta del análisis con la plantilla de abajo. En el chat, da un resumen corto: la paleta, cuántos efectos, los 2 o 3 momentos clave y la ruta del archivo. Si la persona dijo en qué editor trabaja, adapta la última sección a ese editor (ver `references/editores.md`).

**Términos de Envato**: siempre en inglés, porque el catálogo de Envato está etiquetado en inglés. Da un término principal y una alternativa, de 1 a 3 palabras con un adjetivo de carácter (*short, deep, soft, cinematic, digital, airy, punchy*). Arma el link así: `https://elements.envato.com/sound-effects/<termino-con-guiones>`, por ejemplo `https://elements.envato.com/sound-effects/whoosh-transition`. Si un link no abre la búsqueda, el término sirve igual en el buscador de Envato o en la extensión de Envato para Premiere.

**Si la sesión tiene el conector de Envato** (herramientas con "envato" en el nombre), úsalo para buscar cada fila del kit con su término. Elige 1 o 2 sonidos reales por fila: los de duración corta, que encajen con el carácter pedido y, si hay, de un mismo pack para las variantes. En la columna "Buscar en Envato" pon el título exacto y su enlace, y deja el término como alternativa. Sin conector, prueba `python <carpeta-de-esta-skill>/scripts/buscar_envato.py --kit kit.json --json resultados.json`. Usa el mismo buscador público de Envato, que no pide cuenta, y necesita acceso de red a `mcp.envato.com`. `kit.json` es una lista de `{"id", "termino", "max_seg", "categoria"}`. Si tampoco funciona, no inventes títulos de sonidos: da solo términos. Si el conector permite descargar o licenciar, no lo hagas sin que la persona lo pida, porque cada descarga registra una licencia para un proyecto: pregunta antes y usa el nombre del reel como proyecto.

**Timecodes**: usa `HH:MM:SS:FF`, que es como los muestran Premiere y DaVinci. Indica también los segundos. Los del análisis empiezan en `00:00:00:00`. La línea de tiempo de DaVinci suele empezar en `01:00:00:00`, así que avisa que hay que sumar una hora. En Premiere normalmente empieza en cero.

## Plantilla de `mapa_sonido.md`

```markdown
# Mapa de sonido — <nombre del reel>

**Duración:** 0:20 · **FPS:** 30 · **Editor:** Premiere Pro · **Efectos:** 16 en 9 momentos
**Paleta:** <nombre corto> — <qué familias y por qué encajan con el reel>

> Timecodes del video exportado (empiezan en 00:00:00:00). <Nota de DaVinci si aplica.>

## 1. Kit para descargar en Envato
Bájalo una vez. Varios momentos reutilizan el mismo sonido.

| Sonido | Para qué momentos | Buscar en Envato | Alternativa |
|---|---|---|---|
| Whoosh corto (2–3 variantes) | cortes 2, 4, 7 | [whoosh transition](https://elements.envato.com/sound-effects/whoosh-transition) | fast swoosh |

## 2. Mapa por momento
Varias filas con el mismo número son capas que suenan juntas en ese momento.

| # | Timecode (seg) | Qué pasa en pantalla | Capa / efecto | Buscar en Envato | Sincronía | Volumen |
|---|---|---|---|---|---|---|
| 1 | 00:00:00:00 (0.0) | Hook: "BLACK FRIDAY" entra de golpe | Impacto cinematográfico | cinematic hit | Empieza en el fotograma 0 | Fuerte |
| 1 | 00:00:00:00 (0.0) | | Sub drop debajo del hit | sub drop | Junto al hit | Medio |

## 3. Momentos sin efecto (a propósito)
- 00:00:09:15 — jump cut mientras habla; la frase ya lleva el ritmo y un whoosh la taparía.

## 4. Montaje en <Premiere Pro / DaVinci Resolve>
<4 a 6 pasos concretos: pistas por familia, de dónde bajar los sonidos, volúmenes, ducking de la música y comprobación final.>
```

Escala de volumen, para que todos hablen igual (picos aproximados del efecto en la mezcla, con la voz pico en torno a −6 dB):
- **Fuerte** (−6 a −10 dB): solo sin voz encima, como el hook, una revelación o un reel solo con música.
- **Medio** (−12 a −16 dB): transiciones e impactos con poca voz.
- **Suave** (−18 a −24 dB): pops, clicks, tecleo y foley debajo de la voz.
- **Ambiente** (−26 a −32 dB): room tone y colas.

Las filas y la sección de montaje deben bastar para que alguien que no vio el análisis coloque cada sonido sin adivinar.

## Si falta algo
- **Sin ffmpeg y sin forma de instalarlo**: pide el guion o una descripción con tiempos y trabaja desde ahí. Avisa que la sincronía será aproximada.
- **Video largo (más de 3 minutos)**: funciona, pero prioriza. Mapea a fondo el primer minuto y los momentos clave, y para el resto da patrones ("cada cambio de tip: whoosh B + pop").
- **Piden otro banco de sonidos** (Artlist, Epidemic, la biblioteca de CapCut...): los mismos términos en inglés funcionan casi en todos. Cambia solo los links.
