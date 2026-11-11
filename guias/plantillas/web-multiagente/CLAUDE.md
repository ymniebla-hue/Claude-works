# Web de [NOMBRE DEL NEGOCIO]

Web estática con **Astro**, construida por varios subagentes que trabajan en paralelo.
Antes de nada, lee `BRIEF.md`.

## Quién toca qué

Cada archivo tiene un solo dueño. **No edites archivos de otro dueño**: si necesitas un cambio,
pídelo en tu respuesta final y el agente principal se lo pasará a quien corresponda.

| Archivo | Dueño |
|---|---|
| `BRIEF.md`, `src/assets/fotos/` | la persona (humano) |
| `src/styles/tokens.css`, `src/styles/global.css`, `DISENO.md` | director-de-arte |
| `src/pages/index.astro` | director-de-arte |
| `src/layouts/Base.astro` | director-de-arte (lo crea) · seo (solo el `<head>`, en la fase 3) |
| `src/data/textos.ts` | redactor |
| `src/components/secciones/<Nombre>.astro` | el maquetador al que se le asignó esa sección |
| `src/components/IntroAgentes.astro`, `src/scripts/animaciones.ts` | motion |
| `public/robots.txt`, `astro.config.mjs` (`site`) | seo |
| todo | revisor: solo lee, nunca edita |

## Convenciones

- Idioma de la web: español. Textos siempre desde `src/data/textos.ts`.
- Estilos: solo variables de `src/styles/tokens.css`. Sin colores ni tamaños sueltos.
- Fotos en `src/assets/fotos/`, con `<Image />` de `astro:assets` y `alt` siempre.
- Intro animada: las piezas visibles llevan `data-capa="titular|texto|imagen|bloque|boton|nav"` y
  `data-log="verbo en pasado + qué"`. Ver `src/components/IntroAgentes.astro`.
- Accesibilidad: un único `<h1>`, encabezados en orden, foco visible, contraste AA,
  `prefers-reduced-motion` respetado.
- Primero celular: sin scroll horizontal a 360 px.
- No añadas dependencias sin preguntar.

## Comandos

- `npm run dev` → servidor local en http://localhost:4321 (se recarga solo al guardar).
- `npm run build` → compila a `dist/`. Solo lo ejecuta un agente a la vez.
- `npm run preview` → sirve lo compilado.
