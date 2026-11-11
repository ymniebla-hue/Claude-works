# Guía: webs construidas por varios agentes con Claude Code

Guía paso a paso para reproducir lo que muestra el reel
[«Claude crea webs en multiagente»](https://www.instagram.com/reel/DfhQWUORA1L/): la web de un
estudio de arquitectura que se va armando sola mientras una docena de «agentes» de colores
escriben los textos, colocan las fotos y maquetan cada sección.

> **Nota sobre las fuentes.** El reel se analizó fotograma a fotograma a partir del video
> descargado; no se pudo leer el texto de la publicación ni transcribir el audio. Lo que se dice
> aquí sobre Claude Code sale de su documentación oficial, consultada en noviembre de 2026.

**Lo que vas a tener al final:**

- Un proyecto web (Astro) que construyen en paralelo seis tipos de subagentes, cada uno dueño de
  sus propios archivos.
- La intro animada del reel, con agentes, contador de capas, registro y botón «Saltar», lista
  para usar en tu web.
- Una demo que puedes abrir ya mismo: [`demos/agentes-construyendo.html`](demos/agentes-construyendo.html).

---

## Qué se ve en el reel (y qué es real)

En el video aparece la web de un estudio de arquitectura con titulares como «Casas que respiran»,
«Del boceto a la llave» y «Empecemos tu casa». Encima hay:

- **12 etiquetas de colores con un cursor** que se mueven por la página (se alcanzan a leer
  nombres como Diseño, Copy, Fotos o SEO).
- **Cajas celestes vacías** que se van llenando con texto, y fotos que aparecen borrosas y se
  enfocan.
- Una barra inferior: **«12 agentes · 136/175 capas · construyendo»**.
- Un panel **«Registro de agentes»** con líneas como «Fotos montó la maqueta 1:50» y un botón
  **«Saltar»**.

Todo eso forma parte de la propia página: el botón «Saltar» y el contador de capas son típicos de
una **animación de entrada**. Los agentes de Claude trabajan en la terminal (o en la app)
escribiendo archivos; no mueven cursores dentro del navegador. El reel junta dos cosas, y esta
guía cubre las dos:

1. **Construir la web con varios agentes de verdad**, en paralelo (pasos 1 a 5).
2. **Una intro animada que dramatiza esa construcción** para quien visita la web (paso 6).

Lo más parecido a «verla construirse» de verdad es tener el servidor local abierto en el
navegador mientras los agentes trabajan: cada vez que uno guarda su archivo, la página se
actualiza sola (paso 5).

---

## Requisitos

| Herramienta | Para qué | Dónde |
|---|---|---|
| Claude Code | Los agentes que construyen la web | [claude.com/claude-code](https://claude.com/claude-code) |
| Node.js 22 (22.23 o superior) | Proyecto Astro | [nodejs.org](https://nodejs.org/) |
| Git | Copiar la plantilla y guardar versiones | [git-scm.com](https://git-scm.com/) |
| Un navegador | Ver la web mientras se construye | — |

Funciona en macOS, Windows y Linux.

---

## Paso 1 — Crear el proyecto

```bash
npm create astro@latest mi-web -- --template minimal
```

Responde que sí a instalar dependencias. Después entra en la carpeta:

```bash
cd mi-web
```

Se usa **Astro** porque genera HTML estático (rápido y bueno para SEO) y porque cada sección vive
en su propio archivo `.astro`, así que varios agentes pueden trabajar a la vez sin pisarse.

## Paso 2 — Copiar la plantilla

La plantilla está en [`plantillas/web-multiagente/`](plantillas/web-multiagente/):

```
web-multiagente/
├── CLAUDE.md                       ← reglas del proyecto y quién toca cada archivo
├── BRIEF.md                        ← lo que tú rellenas: negocio, secciones, tono, fotos
├── .claude/agents/
│   ├── director-de-arte.md         ← colores, tipografías, esqueleto
│   ├── redactor.md                 ← todos los textos
│   ├── maquetador.md               ← una sección (se lanza una copia por sección)
│   ├── motion.md                   ← intro animada y animaciones
│   ├── seo.md                      ← metadatos, Open Graph, datos estructurados
│   └── revisor.md                  ← revisa y reporta, no edita
└── src/components/IntroAgentes.astro  ← la intro del reel, lista para usar
```

Cópiala dentro de tu proyecto (desde la carpeta que contiene `mi-web`):

```bash
git clone https://github.com/ymniebla-hue/Claude-works.git
```

```bash
# macOS / Linux
cp -R Claude-works/guias/plantillas/web-multiagente/. mi-web/
```

```powershell
# Windows (PowerShell)
Copy-Item -Recurse -Force Claude-works\guias\plantillas\web-multiagente\* mi-web\
```

Comprueba que en `mi-web` aparecen `CLAUDE.md`, `BRIEF.md` y la carpeta `.claude/agents/` (en
macOS y Linux es una carpeta oculta: `ls -a`).

## Paso 3 — Rellenar el BRIEF y poner las fotos

Abre `BRIEF.md` y completa lo que sepas: negocio, tono, acción principal, colores de marca y la
lista de secciones en orden. **Lo que dejes vacío no se inventa**: los agentes lo marcan como
`[PENDIENTE]` para que lo completes después.

Pon tus fotos en `src/assets/fotos/` con nombres claros (`hero.jpg`,
`proyecto-casa-salitre-1.jpg`). Si todavía no tienes fotos, los maquetadores dejan marcadores del
tamaño correcto.

Abre también `CLAUDE.md` y cambia `[NOMBRE DEL NEGOCIO]`.

## Paso 4 — Conocer al equipo

Cada agente es un archivo Markdown en `.claude/agents/` con una cabecera (nombre, descripción,
herramientas, modelo y color) y sus instrucciones debajo. Claude Code los detecta solo; si creas
la carpeta con Claude Code abierto, reinícialo una vez.

| Agente | Fase | Edita | Modelo |
|---|---|---|---|
| `director-de-arte` | 1 | `tokens.css`, `global.css`, `Base.astro`, `index.astro`, `DISENO.md` | el de tu sesión |
| `redactor` | 1 | `src/data/textos.ts` | el de tu sesión |
| `maquetador` (×1 por sección) | 2 | su `src/components/secciones/<Nombre>.astro` | el de tu sesión |
| `motion` | 2 | `IntroAgentes.astro`, `src/scripts/animaciones.ts` | el de tu sesión |
| `seo` | 3 | `<head>` de `Base.astro`, `robots.txt` | Sonnet |
| `revisor` | 4 | nada (solo compila y reporta) | Sonnet |

La regla que hace posible el paralelismo está en `CLAUDE.md`: **cada archivo tiene un solo
dueño**. Si un agente necesita un cambio en un archivo ajeno, lo pide en su respuesta y el agente
principal se lo pasa a su dueño. Así no hay dos agentes editando el mismo archivo.

Para ahorrar uso, cambia `model: inherit` por `model: sonnet` en `maquetador.md`. Las opciones
válidas son `sonnet`, `opus`, `haiku`, `fable`, `inherit` o un ID de modelo completo.

## Paso 5 — Lanzar la construcción

1. **Abre el servidor local** en una terminal y deja la página abierta en el navegador
   (http://localhost:4321):

   ```bash
   npm run dev
   ```

2. **Abre Claude Code** en otra terminal, dentro de `mi-web`. Para que no te pida permiso por
   cada archivo, arráncalo aceptando ediciones automáticamente (o pulsa Shift+Tab dentro de
   Claude Code hasta ver el modo de aceptar ediciones):

   ```bash
   claude --permission-mode acceptEdits
   ```

3. **Pega este prompt:**

   > Vamos a construir la web de `BRIEF.md` con los subagentes de `.claude/agents/`. Tú coordinas:
   > no edites archivos de secciones. Espera a que termine cada fase antes de empezar la siguiente.
   >
   > **Fase 1, en paralelo:** `director-de-arte` y `redactor`.
   >
   > **Fase 2, en paralelo:** un `maquetador` por cada sección del BRIEF (pásale a cada uno el
   > nombre de su sección, su archivo en `src/components/secciones/` y lo que dice el BRIEF de
   > ella) y, a la vez, `motion`.
   >
   > **Fase 3:** `seo`.
   >
   > **Fase 4:** `revisor`. Con su tabla, manda cada arreglo al dueño del archivo según
   > `CLAUDE.md` (en paralelo si son archivos distintos) y repite el revisor hasta que diga «Listo
   > para publicar: sí» o solo queden problemas de gravedad baja.
   >
   > Cuando un agente pida un cambio en un archivo ajeno, pásaselo a su dueño. Al final, dame un
   > resumen y la lista de textos `[PENDIENTE]`.

4. **Mira cómo trabaja.** Cada subagente aparece como una fila en el panel de subagentes, debajo
   del cuadro de texto de Claude Code; abre una fila para ver lo que está haciendo. Con `/tasks`
   ves la lista de tareas. En el navegador, las secciones aparecen a medida que cada maquetador
   guarda su archivo.

Con un BRIEF de ocho secciones, en la fase 2 trabajan nueve agentes a la vez (ocho maquetadores y
motion). En total pasan por el proyecto unos trece. Claude Code permite hasta 20 subagentes
simultáneos por defecto.

## Paso 6 — La intro «agentes construyendo»

Es la parte que más llama la atención del reel. Antes de tocar tu proyecto, abre la demo con
doble clic: [`demos/agentes-construyendo.html`](demos/agentes-construyendo.html) (no necesita
instalar nada).

**Cómo funciona:**

- Cada pieza visible de la web lleva `data-capa` (tipo de pieza) y `data-log` (qué escribe el
  registro al terminarla). Los maquetadores ya las ponen:

  ```html
  <h1 data-capa="titular" data-log="compuso el titular">…</h1>
  <div data-capa="imagen" data-log="colocó la foto principal">…</div>
  ```

  Tipos: `titular`, `texto`, `imagen`, `bloque`, `boton`, `nav`.
- Al cargar, esas piezas se ven como cajas vacías. Los 12 agentes van por ellas en el orden de la
  página, cada uno prefiere su especialidad (Copy → textos, Fotos → imágenes…) y, al terminar,
  la pieza aparece con un barrido (textos) o pasando de borrosa a nítida (fotos).
- QA no construye: va detrás repasando lo terminado y cierra el registro.
- La página baja sola siguiendo la obra hasta que la visita hace scroll.

**Lo que ya resuelve el componente `IntroAgentes.astro`:**

- El contenido está en el HTML desde el principio; la intro solo lo oculta visualmente unos
  segundos. Buscadores y lectores de pantalla ven la página completa.
- No aparece si el usuario pidió reducir el movimiento (`prefers-reduced-motion`) ni si no hay
  JavaScript.
- Sale **una vez por sesión** (no en cada página ni en cada recarga).
- Botón «Saltar animación» y redes de seguridad: si el script no arranca, la página se muestra a
  los 6 segundos, y ninguna intro dura más de 45.

**Ajustes rápidos** (o pídeselos al agente `motion`):

```astro
<IntroAgentes
  agentes={[
    { nombre: 'Diseño', color: '#7c5cff' },
    { nombre: 'Copy', color: '#ff4d6d' },
    { nombre: 'QA', color: '#8d949b', revisa: true },
  ]}
  unaVezPorSesion={false}
/>
```

En secciones con fondo oscuro, cambia el color de las cajas vacías:

```astro
<section style="--ia-esqueleto:#23324a; --ia-esqueleto-borde:#3f5f8a">
```

Para quitar la intro, borra `<IntroAgentes />` de `src/pages/index.astro`.

> **Úsala con criterio.** Diez segundos de animación antes de poder leer es mucho para alguien que
> vuelve o que llega desde Google. Una vez por sesión y con «Saltar» visible es lo mínimo; en webs
> de clientes, valora dejarla solo en la portada o como pieza de portafolio.

## Paso 7 — Revisar y publicar

```bash
npm run build
```

```bash
npm run preview
```

Revisa la página en el navegador a 390 px de ancho (modo celular de las herramientas de
desarrollo, F12) y completa los `[PENDIENTE]`. Para publicar, conecta el repositorio a Netlify,
Vercel o Cloudflare Pages (detectan Astro solos), o sube la carpeta `dist/` a
[Netlify Drop](https://app.netlify.com/drop).

---

## Opción avanzada: equipos de agentes

Lo de arriba usa **subagentes**: el agente principal los lanza, cada uno hace su parte y le
devuelve el resultado. Claude Code también tiene **equipos de agentes** (*agent teams*): sesiones
completas que comparten una lista de tareas y se mandan mensajes entre ellas. Visualmente es lo
más parecido al reel si los pones en paneles divididos (cada agente en su propia ventana de
terminal).

Están en fase experimental y vienen desactivados. Para activarlos, añade esto a
`~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Para ver cada agente en su propio panel, abre Claude Code dentro de una sesión de tmux (o en
iTerm2 con su herramienta `it2`) con este modo:

```bash
claude --teammate-mode auto
```

Sin tmux ni iTerm2, los compañeros aparecen en el panel de abajo y los eliges con las flechas.

Luego pide el equipo en lenguaje natural, reutilizando los mismos agentes:

> Crea un equipo de agentes para construir la web de `BRIEF.md`: un compañero con el tipo de agente
> `director-de-arte`, otro `redactor` y, cuando terminen, un `maquetador` por sección. Cada uno
> solo edita sus archivos según `CLAUDE.md`.

**¿Vale la pena?** Para una web, normalmente no: los maquetadores no necesitan hablar entre ellos
y los equipos gastan bastante más uso (cada compañero es una sesión completa). La documentación
recomienda empezar con 3 a 5 compañeros. Úsalos si quieres el efecto visual de muchas terminales
o para tareas donde los agentes deben discutir, como revisar un diseño desde varios ángulos.

---

## Cuánto cuesta y cuándo no conviene

- Cada subagente es una conversación aparte: construir una web con trece agentes consume bastante
  más uso que hacerlo en una sola conversación. Si tu plan tiene límites, empieza con tres o cuatro
  secciones y `model: sonnet` en el maquetador.
- El paralelo ahorra tiempo cuando las partes son **independientes** (secciones distintas). Para
  retocar una misma sección, una sola conversación es mejor.
- Más agentes no es mejor diseño: el resultado depende sobre todo del BRIEF y de `DISENO.md`.
  Revisa la fase 1 antes de dejar que arranque la fase 2.

## Problemas comunes

| Síntoma | Solución |
|---|---|
| Claude no usa los subagentes | Comprueba que existen en `.claude/agents/` dentro de `mi-web`; si creaste la carpeta con Claude Code abierto, reinícialo. Nómbralos en el prompt. |
| Pide permiso por cada archivo | Arranca con `claude --permission-mode acceptEdits` o cambia de modo con Shift+Tab. |
| Dos agentes editaron el mismo archivo | Algún agente se salió de su carril; recuérdale la tabla de `CLAUDE.md` y que pida los cambios en vez de hacerlos. |
| Los maquetadores arrancan antes de que existan los tokens | Pide explícitamente que espere al final de la fase 1 antes de la fase 2. |
| Error de versión al crear el proyecto | Astro 7 pide Node 22.23 o superior: actualiza Node. |
| La intro no aparece | Ya la viste en esta sesión (cierra la pestaña o usa `unaVezPorSesion={false}`), tienes activado «reducir movimiento» en el sistema, o ninguna pieza tiene `data-capa`. |
| La página se queda unos segundos en cajas vacías y luego aparece de golpe | El script de la intro no arrancó; revisa la consola del navegador (F12). El componente muestra la página a los 6 segundos para no dejarla a medias. |
| La página va lenta en celular | Fotos demasiado pesadas: usa `<Image />` de `astro:assets` (las optimiza) y no más de 2000 px de ancho. |

## Fuentes

- Reel original: [instagram.com/reel/DfhQWUORA1L](https://www.instagram.com/reel/DfhQWUORA1L/)
- [Claude Code — Subagentes](https://code.claude.com/docs/en/sub-agents)
- [Claude Code — Equipos de agentes](https://code.claude.com/docs/en/agent-teams)
- [Claude Code — Modos de permisos](https://code.claude.com/docs/en/permission-modes)
- [Astro — Instalación](https://docs.astro.build/en/install-and-setup/)
- [Astro — Imágenes (`astro:assets`)](https://docs.astro.build/en/guides/images/)
- [Astro — Scripts y `define:vars`](https://docs.astro.build/en/reference/directives-reference/)
