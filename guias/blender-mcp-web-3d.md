# Guía: webs con hero 3D usando Claude Code + Blender

Guía paso a paso para reproducir en tu computadora el flujo del video
[“ASTRA + BLENDER = websites 3d INCREÍBLES”](https://youtu.be/GrhdYKD02_M):
un agente de IA modela un objeto en Blender, lo exporta a GLB y lo monta en la sección
principal (hero) de una web que sigue el mouse y reacciona al scroll.

> **Nota sobre las fuentes.** El video no se pudo ver directamente (YouTube estaba bloqueado en el
> entorno donde se preparó esta guía). El flujo se reconstruyó con el título del video, la versión en
> inglés del mismo tutorial y la documentación oficial de las herramientas. El video usa GPT-6 Astra
> dentro de Codex; aquí se usa **Claude Code**, que hace lo mismo con Blender MCP.

**Lo que vas a tener al final:** un proyecto web (Vite + Three.js) con tu modelo 3D en el hero,
optimizado para cargar rápido y publicado en internet.

---

## Requisitos

| Herramienta | Para qué | Dónde |
|---|---|---|
| Blender 4.x o superior (mínimo 3.0) | Crear y exportar el modelo 3D | [blender.org/download](https://www.blender.org/download/) |
| Claude Code | El agente que controla Blender y escribe la web | [claude.com/claude-code](https://claude.com/claude-code) |
| `uv` (incluye `uvx`) | Ejecuta el servidor Blender MCP | Paso 2 |
| Python 3.10+ | Lo usa `uv` | `uv` lo instala si falta |
| Node.js 18+ | Proyecto web con Vite | [nodejs.org](https://nodejs.org/) |

Funciona en macOS, Windows y Linux. Los comandos que cambian según el sistema están marcados.

---

## Paso 1 — Instalar Blender

Descarga Blender desde [blender.org/download](https://www.blender.org/download/), instálalo y ábrelo una
vez para confirmar que arranca.

## Paso 2 — Instalar `uv`

Usa el instalador oficial (no `pip`):

```bash
# macOS
brew install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cierra y vuelve a abrir la terminal, y comprueba con `uvx --version`.

## Paso 3 — Conectar Blender con Claude Code (Blender MCP)

[Blender MCP](https://github.com/ahujasid/blender-mcp) es un complemento que abre una conexión local
dentro de Blender para que Claude pueda leer la escena y ejecutar código Python en ella.

1. **Registrar el servidor en Claude Code** (con `--scope user` queda disponible en cualquier carpeta):

   ```bash
   claude mcp add --scope user blender -- uvx mcp-for-blender
   ```

2. **Instalar el complemento en Blender:**

   ```bash
   uvx mcp-for-blender install-addon
   ```

3. **Activarlo:** en Blender, *Edit → Preferences → Add-ons*, busca **“MCP for Blender”** y márcalo.

4. **Iniciar la conexión:** en el visor 3D pulsa la tecla **N**, abre la pestaña **MCP for Blender** y
   haz clic en **Start MCP Server**. Esto hay que repetirlo cada vez que abras Blender.

5. **Comprobar:** ejecuta `claude mcp list` en la terminal (debe aparecer `blender`) y, dentro de
   Claude Code, escribe `/mcp` para ver que está conectado.

> El paquete antes se llamaba `blender-mcp`. Si un tutorial viejo usa ese nombre, cámbialo por
> `mcp-for-blender`. Usa **un solo** cliente conectado a Blender a la vez (no Claude Desktop y Claude
> Code al mismo tiempo).

## Paso 4 — Crear el modelo con prompts

Crea una carpeta para el proyecto, ábrela en la terminal y ejecuta `claude`. Con Blender abierto y el
servidor iniciado, pídele el modelo por partes. Ejemplos:

**Modelo:**

> Usando Blender, crea una escultura abstracta para el hero de una web: un nudo toroidal con superficie
> suave, centrado en el origen, de unos 2 metros. Menos de 50.000 polígonos. Muéstrame una captura del
> visor cuando termines.

**Materiales y luz:**

> Aplícale un material metálico con reflejos, color [tu color de marca en HEX], rugosidad 0.25.
> Agrega una luz de estudio de tres puntos para revisar el modelo.

**Ajustes:**

> Hazlo un 20 % más delgado y suaviza los bordes con un modificador Bevel. Aplica todos los modificadores.

**Exportar:**

> Exporta el modelo (sin luces ni cámara) como GLB en `public/modelo.glb` dentro de esta carpeta,
> aplicando transformaciones y con compresión Draco. Dime cuánto pesa el archivo.

Consejos:
- Pide capturas del visor para revisar el resultado antes de exportar.
- Guarda el `.blend` antes de cada cambio grande (ver *Seguridad*).
- El complemento también puede traer modelos de Poly Haven, Sketchfab o generarlos con Hyper3D/Hunyuan3D
  (algunos requieren clave de API propia).

## Paso 5 — Crear la web

Puedes pedírselo a Claude Code directamente:

> Crea un proyecto Vite + Three.js en esta carpeta. El hero debe mostrar `public/modelo.glb` en un canvas
> a pantalla completa, el modelo debe girar suavemente hacia el cursor y, al hacer scroll, rotar, crecer
> y bajar. Respeta `prefers-reduced-motion`.

O hacerlo a mano con el código de referencia de abajo (probado con Three.js 0.186 y Vite 8: el modelo
carga, sigue el cursor y responde al scroll, sin errores en consola).

**5.1 Crear el proyecto:**

```bash
npm create vite@latest mi-web-3d -- --template vanilla
cd mi-web-3d
npm install three
```

**5.2 Copiar el decodificador Draco** (necesario porque el GLB va comprimido; así no dependes de un
servidor externo):

```bash
# macOS / Linux
mkdir -p public/draco && cp node_modules/three/examples/jsm/libs/draco/gltf/* public/draco/

# Windows (PowerShell)
New-Item -ItemType Directory -Force public/draco; Copy-Item node_modules/three/examples/jsm/libs/draco/gltf/* public/draco/
```

Coloca tu `modelo.glb` en `public/`.

**5.3 Reemplazar `index.html`:**

```html
<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Hero 3D</title>
    <style>
      body { margin: 0; background: #0b0b10; color: #fff; font-family: system-ui, sans-serif; }
      #hero-canvas { position: fixed; inset: 0; width: 100%; height: 100vh; z-index: 0; }
      section { position: relative; z-index: 1; min-height: 100vh; display: grid; place-items: center; }
    </style>
  </head>
  <body>
    <canvas id="hero-canvas"></canvas>
    <section><h1>Tu marca en 3D</h1></section>
    <section><h2>Sección 2</h2></section>
    <section><h2>Sección 3</h2></section>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

**5.4 Reemplazar `src/main.js`:**

```js
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const canvas = document.querySelector('#hero-canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
camera.position.set(0, 0, 6);

scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 1.5));
const luz = new THREE.DirectionalLight(0xffffff, 2);
luz.position.set(3, 4, 5);
scene.add(luz);

// "pivot" es el grupo que movemos; el modelo va adentro
const pivot = new THREE.Group();
scene.add(pivot);

const draco = new DRACOLoader();
draco.setDecoderPath('/draco/');
const loader = new GLTFLoader();
loader.setDRACOLoader(draco);
loader.load('/modelo.glb', (gltf) => {
  const modelo = gltf.scene;
  // Centrar el modelo y ajustarlo a un tamaño fijo, venga como venga de Blender
  const caja = new THREE.Box3().setFromObject(modelo);
  modelo.position.sub(caja.getCenter(new THREE.Vector3()));
  const contenedor = new THREE.Group();
  contenedor.add(modelo);
  contenedor.scale.setScalar(3 / caja.getSize(new THREE.Vector3()).length());
  pivot.add(contenedor);
});

// Posición del mouse normalizada de -1 a 1
const mouse = { x: 0, y: 0 };
window.addEventListener('pointermove', (e) => {
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = (e.clientY / window.innerHeight) * 2 - 1;
});

// Progreso del scroll de 0 (arriba) a 1 (abajo)
let scroll = 0;
window.addEventListener('scroll', () => {
  const max = document.documentElement.scrollHeight - window.innerHeight;
  scroll = max > 0 ? window.scrollY / max : 0;
}, { passive: true });

const sinMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function ajustarTamano() {
  const { clientWidth: w, clientHeight: h } = canvas;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', ajustarTamano);
ajustarTamano();

renderer.setAnimationLoop(() => {
  if (!sinMovimiento) {
    const suave = 0.08; // más bajo = movimiento más lento y suave
    // 1) El modelo "mira" hacia el cursor
    pivot.rotation.y += (mouse.x * 0.6 + scroll * Math.PI * 2 - pivot.rotation.y) * suave;
    pivot.rotation.x += (mouse.y * 0.3 - pivot.rotation.x) * suave;
    // 2) Con el scroll crece y baja
    const escala = 1 + scroll * 0.6;
    pivot.scale.setScalar(pivot.scale.x + (escala - pivot.scale.x) * suave);
    pivot.position.y += (-scroll * 1.5 - pivot.position.y) * suave;
  }
  renderer.render(scene, camera);
});
```

**5.5 Verlo en el navegador:** `npm run dev` y abre la dirección que aparece (normalmente
`http://localhost:5173`).

Para ajustar el efecto, cambia los números del bloque final: `0.6` (cuánto sigue al cursor),
`Math.PI * 2` (vueltas con el scroll), `0.6` en `escala` (cuánto crece) y `1.5` (cuánto baja).

## Paso 6 — Optimizar

Un hero 3D pesado arruina la carga en celulares. Objetivo: **GLB de menos de 3–5 MB**.

```bash
npx @gltf-transform/cli optimize public/modelo.glb public/modelo.glb --compress draco --texture-compress webp
```

- Opciones útiles: `--texture-size 1024` (limita texturas) y `--simplify true` (reduce polígonos).
- Si el modelo sigue pesando, pide a Claude en Blender: *“Reduce el modelo a 20.000 polígonos con
  Decimate sin perder la silueta”*.
- Prueba en un celular real, no solo en la computadora.

## Paso 7 — Publicar

```bash
npm run build
```

Esto genera la carpeta `dist/`. Súbela a:
- **Vercel:** `npx vercel` (o conecta el repositorio de GitHub en vercel.com).
- **Netlify:** arrastra la carpeta `dist/` a [app.netlify.com/drop](https://app.netlify.com/drop).

---

## Seguridad

- **El complemento ejecuta Python sin restricciones dentro de Blender.** Guarda tu archivo `.blend`
  antes de cada cambio grande; un error del agente puede borrar o romper la escena.
- **La conexión no tiene contraseña ni cifrado.** Déjala solo en tu computadora (localhost); no la
  expongas en redes públicas.
- Es un complemento de la comunidad, no oficial de Blender.
- Las descargas grandes de modelos pueden congelar Blender unos segundos.

## Problemas comunes

| Síntoma | Solución |
|---|---|
| `blender` no aparece en `/mcp` | Revisa `claude mcp list`; reinicia Claude Code después de `claude mcp add`. |
| “Connection refused” al usar Blender | Falta pulsar **Start MCP Server** en la pestaña N de Blender. |
| `uvx: command not found` | Cierra y abre la terminal tras instalar `uv`. |
| El modelo no aparece en la web | Confirma que el archivo está en `public/modelo.glb`; revisa la consola del navegador (F12). |
| Error de Draco al cargar | Falta copiar el decodificador a `public/draco/` (paso 5.2). |
| El modelo se ve negro | Faltan luces o el material es 100 % metálico sin entorno; baja el metálico o agrega luces. |
| La página va lenta en celular | Vuelve al paso 6: menos polígonos y texturas más pequeñas. |

## Alternativa sin tener Blender abierto

Existe una skill de la comunidad para Claude Code, `czlonkowski/blender-web-3d-skill`, que usa Blender
en modo *headless* (sin interfaz) con exportación GLB y Three.js. No se pudo verificar para esta guía;
revisa su repositorio antes de usarla.

## Ejemplos para inspirarte

- [Model X Studio](https://model-x-studio.vercel.app): visor de auto con vista explosionada.
- [Human Atlas](https://human-atlas-seven.vercel.app): anatomía interactiva por partes.
- [Seoul 3D Atlas](https://seoul-3d-atlas.synabreu.chatgpt.site/): ciudad en miniatura con día y noche.
- Más en [awesome-gpt-6-astra](https://github.com/magiccreator-ai/awesome-gpt-6-astra).

## Fuentes

- [Video original](https://youtu.be/GrhdYKD02_M) y versión en inglés: [GPT 6 Astra + Blender = INSANE 3D Websites](https://www.youtube.com/watch?v=RhGiG-yZP-c)
- [Blender MCP (README)](https://github.com/ahujasid/blender-mcp)
- [Build 3D Websites with GPT-6 Astra + Blender — Chase AI](https://www.chaseai.io/blog/gpt-6-astra-blender-3d-websites)
- [GPT-6 Astra Blender MCP — Neural4D](https://blog.neural4d.com/user-guide/gpt-6-astra-blender-mcp/)
- [Three.js — GLTFLoader](https://threejs.org/docs/#examples/en/loaders/GLTFLoader)
- [glTF Transform CLI](https://gltf-transform.dev/cli)
