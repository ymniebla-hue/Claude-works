# Guía: equipo de agentes para lotes de guiones

Un equipo de agentes de Claude Code que produce un lote completo de guiones para Meta Ads (10–12
guiones, en español, inglés o ambos) a partir de la carpeta de un cliente. Los guionistas trabajan
**en paralelo, uno por formato**, y un revisor crítico comprueba cada guion antes de la entrega.

El equipo **no trae la metodología**: la toma de la skill **guion-creator** de la agencia
(formatos, Scroll-Stop Test, redacción oral, reglas de Meta Andromeda y checklist). Si la skill
cambia, el equipo cambia con ella. Este repositorio es público, por eso la skill no está copiada
aquí.

---

## El equipo

| Agente | Fase | Qué hace | Qué archivos escribe |
|---|---|---|---|
| `estratega-de-lote` | 1 | Lee la carpeta del cliente y los lotes anteriores. Asigna a cada guion formato, persona, mensaje y ángulo para que no haya dos iguales. Lista los datos que se pueden usar y los que faltan. | `00-plan.md` |
| `guionista` (×1 por formato) | 2 | Escribe sus guiones con la anatomía de la skill y se autoevalúa. También corrige con las observaciones del revisor. | `G01.md`, `G02.md`… (solo los suyos) |
| `revisor-de-guiones` | 3 | Revisa todo con ojo crítico: Scroll-Stop Test, hilo conductor, oraciones largas (las cuenta), datos sin fuente, compliance, duración y diversidad entre guiones. | `revision.md` |
| `adaptador-en` (×1 por grupo) | 5 | Adapta al inglés (o al español) los guiones aprobados. Reescribe hooks y CTAs, no traduce palabra por palabra. | `en/G01.md`… |
| `productor` | 6 | Arma el documento final para el cliente y un plan de rodaje agrupado por locación y talento. | `LOTE-FINAL.md`, `plan-de-rodaje.md` |

El comando **`/lote-guiones`** coordina todo: lanza las fases en orden, los guionistas a la vez y
hasta dos rondas de correcciones. **Se detiene después del plan para que lo apruebes** antes de
escribir los guiones.

### Por qué funciona en paralelo sin repetirse

Los guionistas no se ven entre sí. Lo que evita que dos escriban lo mismo es el plan: el
estratega asigna de antemano un mensaje central y una ejecución distintos a cada guion, y el
revisor vuelve a comparar todos los guiones por pares al final.

### Reglas que el equipo no se salta

- **Ningún dato inventado.** Solo se usan las cifras de la sección «Datos verificados» del plan,
  cada una con su fuente. Si un hook pide un dato que no hay, queda marcado
  `[DATO A VERIFICAR]` para que lo resuelvan ustedes.
- **Ficción declarada** en storytelling y testimoniales.
- **Compliance** según la categoría del cliente (salud, finanzas, bienes raíces, belleza).
- Cada agente edita solo sus archivos.

---

## Requisitos

- **Claude Code** iniciado con su cuenta de claude.ai, versión 2.1.273 o posterior.
- **La skill guion-creator disponible en Claude Code.** Las skills de claude.ai se sincronizan
  solas con Claude Code cuando inician sesión con su cuenta de claude.ai (no con una clave de API).
  Para comprobarlo, pregunta en Claude Code: «¿tienes disponible la skill guion-creator?». Si no
  aparece, guarda una copia de la skill en `~/.claude/skills/guion-creator/SKILL.md` en tu
  computadora; nunca en un repositorio público.

## Paso 1 — Instalar el equipo

Copia en la carpeta donde guardan a los clientes el contenido de
[`plantillas/equipo-guiones/`](plantillas/equipo-guiones/):

```
equipo-guiones/
├── .claude/
│   ├── agents/            ← los cinco agentes
│   └── commands/
│       └── lote-guiones.md   ← el comando /lote-guiones
└── clientes/
    └── _plantilla/
        └── brief.md       ← brief para cada cliente
```

```bash
# macOS / Linux, desde la carpeta que contiene Claude-works y la carpeta de trabajo
cp -R Claude-works/guias/plantillas/equipo-guiones/. "mi-carpeta-de-clientes/"
```

```powershell
# Windows (PowerShell)
Copy-Item -Recurse -Force Claude-works\guias\plantillas\equipo-guiones\* "mi-carpeta-de-clientes\"
```

Si su carpeta de clientes ya tiene otra estructura, no pasa nada: el comando recibe la ruta de la
carpeta del cliente, esté donde esté. Lo único que debe quedar en la raíz es la carpeta `.claude/`.

## Paso 2 — Preparar al cliente

1. Copia `clientes/_plantilla/` con el nombre del cliente y rellena `brief.md`. Lo más importante:
   - **precios y oferta vigente**;
   - **datos que se pueden decir, con su fuente**;
   - **lo que no se puede decir**.
2. Pon en esa carpeta todo lo útil del cliente: presentación, lista de precios, notas de la
   reunión.
3. Si hubo lotes anteriores, ponlos en `Guiones/` dentro de la carpeta del cliente. El estratega
   los lee para mantener el tono y no repetir mensajes.

## Paso 3 — Lanzar el lote

Abre Claude Code en la carpeta de trabajo y escribe:

```text
/lote-guiones clientes/dental-brisa 12 ES+EN
```

- Primer valor: carpeta del cliente (entre comillas si tiene espacios:
  `"clientes/Dental Brisa"`).
- Segundo: número de guiones (si no lo pones, usa el del brief o 10).
- Tercero: idiomas, `ES`, `EN` o `ES+EN` (si no lo pones, usa los del brief).

Para no aprobar cada archivo uno por uno, arranca Claude Code aceptando ediciones:

```bash
claude --permission-mode acceptEdits
```

### Qué va a pasar

1. **Plan.** El estratega escribe `00-plan.md` y Claude te muestra la tabla de asignación.
   **Revísala**: es el momento de cambiar un ángulo, una persona o un formato. Responde «sigue» o
   pide cambios.
2. **Guiones.** Un guionista por formato escribe a la vez (siete en un lote de 12). En el panel de
   subagentes, debajo del cuadro de texto, se ve a cada uno trabajando.
3. **Revisión y correcciones.** El revisor aprueba o pide cambios guion por guion; los guionistas
   corrigen (hasta dos rondas).
4. **Inglés**, si el lote es bilingüe.
5. **Entrega.** Todo queda en `clientes/<cliente>/Guiones/Lote-<fecha>/`:

```
Lote-2026-11-10/
├── 00-plan.md
├── G01.md … G12.md
├── revision.md
├── en/G01.md … en/G12.md
├── LOTE-FINAL.md         ← para el cliente
└── plan-de-rodaje.md     ← para producción
```

`LOTE-FINAL.md` se puede pasar a Google Docs o Word pidiéndoselo a Claude, o con cualquier
conversor de Markdown.

---

## Cuánto cuesta y cuánto tarda

- Un lote de 12 en ES+EN pone a trabajar más de 20 agentes en total. Consume bastante más uso que
  escribir el lote en una sola conversación. A cambio, cada guion lo escribe un agente concentrado
  en un solo formato y lo revisa otro que no lo escribió.
- **Dato real de la prueba** (cliente ficticio, 12 guiones): solo la primera ronda (plan, 12
  guiones y revisión, 9 agentes) consumió alrededor de 1,5 millones de tokens. Con correcciones e
  inglés, cuenten con bastante más.
- En esa misma prueba, el revisor pidió correcciones en 8 de los 12 guiones en la primera ronda:
  le pasó la misma historia a dos guiones distintos, un hook que no frenaba el scroll, una promesa
  sin confirmar… Por eso existen las rondas de corrección, y por eso no conviene saltarse al
  revisor.
- Si su plan tiene límites de uso, prueben primero con `/lote-guiones <cliente> 5 ES`.
- Para ahorrar, cambia `model: inherit` por `model: sonnet` en `adaptador-en.md` (el productor ya
  usa Sonnet). Para los guionistas y el revisor conviene el mejor modelo disponible.

## Lo que sigue siendo trabajo de ustedes

- Aprobar el plan antes de que se escriban los guiones.
- Resolver los `[PENDIENTE]` y `[DATO A VERIFICAR]` con el cliente.
- Leer los guiones en voz alta con el talento y elegir el hook y el CTA de cada toma.
- La revisión legal en sectores regulados (salud, finanzas, inmobiliario): el revisor aplica las
  reglas de la skill, pero no sustituye a un abogado.

## Problemas comunes

| Síntoma | Solución |
|---|---|
| Un agente responde «FALTA LA SKILL guion-creator» | La skill no está en Claude Code: revisa que inicias sesión con tu cuenta de claude.ai o copia la skill en `~/.claude/skills/guion-creator/`. |
| `/lote-guiones` no aparece | La carpeta `.claude/` no está en la carpeta donde abriste Claude Code, o la creaste con Claude Code abierto: reinícialo. |
| Claude escribe los guiones él mismo en vez de usar a los agentes | Recuérdale: «Usa los subagentes guionista, uno por grupo, en paralelo». |
| Dos guiones dicen lo mismo | Vuelve al plan (`00-plan.md`, sección E) y pide al estratega un mensaje distinto para uno de ellos. |
| Muchos `[DATO A VERIFICAR]` | El brief tiene pocos datos con fuente. Añade cifras comprobables en «Datos que se pueden decir» y relanza. |
