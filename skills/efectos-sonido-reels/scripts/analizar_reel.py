#!/usr/bin/env python3
"""Analiza un reel ya editado para planear sus efectos de sonido.

Uso:
    python analizar_reel.py VIDEO [--out CARPETA] [--umbral-corte 0.30] [--umbral-cambio 0.05]

Genera en CARPETA (por defecto: <nombre-del-video>_sfx junto al video):
    analisis.json        duración, fps, eventos (cortes, cambios visuales), pausas y golpes de audio
    hoja_eventos*.jpg    un fotograma por evento, con su número, timecode y tipo (para mirarla)
    hoja_general.jpg     fotogramas repartidos por todo el reel (vista rápida del contenido)
    fotogramas/          los fotogramas sueltos

Requiere ffmpeg y ffprobe en el PATH, y los paquetes numpy y Pillow.
"""

import argparse
import json
import math

import shutil
import subprocess
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - mensaje para el usuario
    sys.exit("Faltan paquetes de Python. Instálalos con:  pip install numpy pillow")


# ---------------------------------------------------------------- utilidades

def run(cmd, binary=False):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        err = res.stderr.decode("utf-8", "ignore")[-1500:]
        raise RuntimeError(f"Falló: {' '.join(cmd[:4])} ...\n{err}")
    return res.stdout if binary else res.stdout.decode("utf-8", "ignore")


def parse_rate(txt):
    try:
        if "/" in txt:
            a, b = txt.split("/")
            return float(a) / float(b) if float(b) else 0.0
        return float(txt)
    except (ValueError, ZeroDivisionError):
        return 0.0


def timecode(t, fps_tc):
    """Timecode HH:MM:SS:FF contando fotogramas con la base entera (como Premiere/DaVinci sin drop-frame)."""
    frame = int(round(t * fps_tc))
    ff = frame % fps_tc
    total_s = frame // fps_tc
    return f"{total_s // 3600:02d}:{(total_s % 3600) // 60:02d}:{total_s % 60:02d}:{ff:02d}"


def load_font(size):
    for name in ("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf", "Arial.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


# ---------------------------------------------------------------- análisis de video

def probe(video):
    data = json.loads(run(["ffprobe", "-v", "error", "-print_format", "json",
                           "-show_streams", "-show_format", str(video)]))
    v = next((s for s in data["streams"] if s.get("codec_type") == "video"), None)
    if v is None:
        sys.exit("El archivo no tiene pista de video.")
    a = next((s for s in data["streams"] if s.get("codec_type") == "audio"), None)
    fps = parse_rate(v.get("avg_frame_rate", "0/0")) or parse_rate(v.get("r_frame_rate", "0/0")) or 30.0
    dur = float(data["format"].get("duration") or v.get("duration") or 0)
    w, h = int(v.get("width", 0)), int(v.get("height", 0))
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = abs(int(sd["rotation"]))
    if rot in (90, 270):
        w, h = h, w
    return {"duracion": dur, "fps": fps, "ancho": w, "alto": h, "tiene_audio": a is not None}


def metricas_video(video, info):
    """Recorre el video en miniatura y mide, fotograma a fotograma:
    pix  = fracción de píxeles que cambian fuerte respecto al fotograma anterior
    hist = cuánto cambia la paleta de colores (0-1); alto en un corte a otra toma
    """
    vertical = info["alto"] > info["ancho"]
    sw = 96 if vertical else 170
    sh = max(2, int(round(sw * info["alto"] / max(1, info["ancho"]) / 2)) * 2)
    proc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video), "-an",
                             "-vf", f"scale={sw}:{sh}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
                            stdout=subprocess.PIPE)
    size = sw * sh * 3
    prev, hprev = None, None
    pix, hist = [], []
    while True:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        f = np.frombuffer(buf, dtype=np.uint8).reshape(sh, sw, 3)
        q = (f >> 5).astype(np.int32)
        h = np.bincount((q[..., 0] * 64 + q[..., 1] * 8 + q[..., 2]).ravel(), minlength=512) / (sw * sh)
        if prev is None:
            pix.append(0.0)
            hist.append(0.0)
        else:
            d = np.abs(f.astype(np.int16) - prev.astype(np.int16)).max(axis=2)
            pix.append(float((d > 32).mean()))
            hist.append(float(0.5 * np.abs(h - hprev).sum()))
        prev, hprev = f, h
    proc.wait()
    return np.array(pix), np.array(hist)


def detectar_eventos(pix, hist, fps, dur, sens=1.0):
    """Clasifica cada fotograma con cambio brusco:
    corte  = cambia la toma (cambia casi toda la imagen y la paleta de color)
    salto  = cambia casi toda la imagen pero con la misma paleta (jump cut, zoom/punch-in, movimiento brusco)
    cambio = cambio localizado y repentino (texto, emoji, gráfico o sticker que aparece; destello pequeño)
    """
    n = len(pix)
    cand = []
    for i in range(1, n):
        vec = np.concatenate([pix[max(1, i - 6):i - 1], pix[i + 2:i + 7]])
        base = float(np.median(vec)) if vec.size else 0.0
        spike = pix[i] - base
        t = i / fps
        if (hist[i] >= 0.35 and spike >= 0.2) or hist[i] >= 0.6:
            cand.append({"t": t, "tipo": "corte", "fuerza": hist[i]})
        elif spike >= 0.30 * sens:
            cand.append({"t": t, "tipo": "salto", "fuerza": spike})
        elif spike >= 0.006 * sens and pix[i] >= 3 * base + 0.003:
            cand.append({"t": t, "tipo": "cambio", "fuerza": spike})

    # cortes y saltos: se fusionan los que caen a menos de 0.25 s (destellos, fundidos muy cortos)
    grandes = []
    for c in (c for c in cand if c["tipo"] in ("corte", "salto")):
        if grandes and c["t"] - grandes[-1]["t"] < 0.25:
            if c["tipo"] == "corte":
                grandes[-1]["tipo"] = "corte"
            grandes[-1]["fuerza"] = max(grandes[-1]["fuerza"], c["fuerza"])
            grandes[-1]["doble"] = True
            continue
        grandes.append(dict(c))

    # cambios: el pico más fuerte en cada ventana de 0.3 s, lejos de cortes, con un tope razonable
    peq = sorted((c for c in cand if c["tipo"] == "cambio"), key=lambda c: -c["fuerza"])
    cambios = []
    tope = int(dur) + 4
    for c in peq:
        if len(cambios) >= tope:
            break
        if any(abs(c["t"] - g["t"]) < 0.3 for g in grandes):
            continue
        if all(abs(c["t"] - k["t"]) >= 0.3 for k in cambios):
            cambios.append(c)
    return sorted(grandes + cambios, key=lambda e: e["t"])


# ---------------------------------------------------------------- análisis de audio

def analizar_audio(video, dur):
    sr = 16000
    raw = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vn", "-ac", "1",
               "-ar", str(sr), "-f", "s16le", "-"], binary=True)
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if x.size < sr // 10:
        return None
    hop = int(sr * 0.05)  # ventanas de 50 ms
    n = x.size // hop
    frames = x[: n * hop].reshape(n, hop)
    rms = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    p95 = float(np.percentile(db, 95))
    med = float(np.median(db))
    # envolvente: máximo en ±100 ms, para que el hueco entre sílabas o golpes de batería no cuente como pausa
    env = np.array([db[max(0, i - 2):i + 3].max() for i in range(n)])
    # pausa = el audio cae al menos 14 dB bajo las partes fuertes durante >= 0.3 s.
    # Con voz + música debajo, esto suele ser "la voz se calla y queda solo la música".
    umbral = p95 - 14.0
    pausas, ini = [], None
    for i, v in enumerate(env):
        if v < umbral and ini is None:
            ini = i
        elif v >= umbral and ini is not None:
            if (i - ini) * 0.05 >= 0.3:
                pausas.append((ini * 0.05, i * 0.05))
            ini = None
    if ini is not None and (n - ini) * 0.05 >= 0.3:
        pausas.append((ini * 0.05, n * 0.05))

    return {"db": db, "p95": p95, "mediana": med, "umbral": umbral, "pausas": pausas}


def nivel_en(audio, t):
    if audio is None:
        return None
    i0 = max(0, int((t - 0.15) / 0.05))
    i1 = max(i0 + 1, int((t + 0.15) / 0.05))
    seg = audio["db"][i0:i1]
    return round(float(seg.max()), 1) if seg.size else None


def en_pausa(audio, t):
    if audio is None:
        return None
    return any(a - 0.05 <= t <= b + 0.05 for a, b in audio["pausas"])


# ---------------------------------------------------------------- fotogramas y hojas

def extraer_fotograma(video, t, dest, ancho):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video),
         "-frames:v", "1", "-vf", f"scale={ancho}:-2", "-q:v", "3", str(dest)])


def hoja(tiles, ruta_base, por_hoja=40):
    """tiles: lista de (ruta_img, etiqueta). Crea una o varias hojas de contacto."""
    rutas = []
    tiles = [(p, l) for p, l in tiles if Path(p).exists()]
    if not tiles:
        return rutas
    for k in range(0, len(tiles), por_hoja):
        grupo = tiles[k:k + por_hoja]
        ims = [Image.open(p).convert("RGB") for p, _ in grupo]
        tw, th = ims[0].size
        cols = 8 if th > tw else 5
        cols = min(cols, len(ims))
        filas = math.ceil(len(ims) / cols)
        banda = 46
        font = load_font(16)
        lienzo = Image.new("RGB", (cols * tw, filas * (th + banda)), "white")
        draw = ImageDraw.Draw(lienzo)
        for j, (im, (_, etiqueta)) in enumerate(zip(ims, grupo)):
            x, y = (j % cols) * tw, (j // cols) * (th + banda)
            lienzo.paste(im.resize((tw, th)), (x, y))
            draw.rectangle([x, y + th, x + tw - 2, y + th + banda], fill="black")
            for k_lin, linea in enumerate(etiqueta.split("\n")[:2]):
                draw.text((x + 5, y + th + 3 + 21 * k_lin), linea, fill="white", font=font)
        sufijo = "" if len(tiles) <= por_hoja else f"_{k // por_hoja + 1}"
        ruta = ruta_base.with_name(ruta_base.stem + sufijo + ".jpg")
        lienzo.save(ruta, quality=85)
        rutas.append(ruta.name)
    return rutas


# ---------------------------------------------------------------- principal

def main():
    ap = argparse.ArgumentParser(description="Analiza un reel para planear efectos de sonido.")
    ap.add_argument("video")
    ap.add_argument("--out", help="carpeta de salida (por defecto <video>_sfx)")
    ap.add_argument("--sensibilidad", type=float, default=1.0,
                    help="multiplica los umbrales de 'salto' y 'cambio': <1 detecta más, >1 detecta menos")
    args = ap.parse_args()

    for b in ("ffmpeg", "ffprobe"):
        if not shutil.which(b):
            sys.exit("No encuentro ffmpeg. Instálalo: macOS 'brew install ffmpeg', "
                     "Windows 'winget install ffmpeg', Linux 'sudo apt install ffmpeg'.")

    video = Path(args.video).expanduser().resolve()
    if not video.exists():
        sys.exit(f"No existe el archivo: {video}")
    out = Path(args.out).expanduser().resolve() if args.out else video.with_name(video.stem + "_sfx")
    (out / "fotogramas").mkdir(parents=True, exist_ok=True)

    info = probe(video)
    dur, fps = info["duracion"], info["fps"]
    fps_tc = max(1, int(round(fps)))
    vertical = info["alto"] > info["ancho"]
    ancho_tile = 180 if vertical else 288

    print(f"Analizando {video.name}: {dur:.2f} s, {fps:.3f} fps, {info['ancho']}x{info['alto']}")
    pix, hist = metricas_video(video, info)
    if len(pix) > 1 and dur > 0:
        fps = len(pix) / dur if abs(len(pix) / dur - fps) > 1 else fps
    detectados = detectar_eventos(pix, hist, fps, dur, args.sensibilidad)
    audio = analizar_audio(video, dur) if info["tiene_audio"] else None

    eventos = [{"t": 0.0, "tipo": "inicio", "fuerza": None}]
    for d in detectados:
        e = {"t": d["t"], "tipo": d["tipo"], "fuerza": round(float(d["fuerza"]), 3)}
        if d.get("doble"):
            e["nota"] = "dos cambios seguidos (destello, fundido corto o flash)"
        eventos.append(e)
    t_cierre = max(0.0, dur - 1.5)
    if dur > 4 and all(abs(e["t"] - t_cierre) > 0.6 for e in eventos):
        eventos.append({"t": t_cierre, "tipo": "cierre", "fuerza": None})
    eventos.sort(key=lambda e: e["t"])

    tiles = []
    for i, e in enumerate(eventos, 1):
        e["id"] = i
        e["t"] = round(e["t"], 3)
        e["tc"] = timecode(e["t"], fps_tc)
        e["audio_db"] = nivel_en(audio, e["t"])
        e["en_pausa"] = en_pausa(audio, e["t"])
        # el fotograma se toma un poco después del evento para ver lo que aparece
        t_img = min(max(0.0, dur - 0.05), e["t"] + (0.1 if e["tipo"] == "inicio" else 0.2))
        nombre = f"fotogramas/evento_{i:02d}.jpg"
        extraer_fotograma(video, t_img, out / nombre, ancho_tile)
        e["fotograma"] = nombre
        tiles.append((out / nombre, f"#{i} {e['tipo']}\n{e['tc']}"))

    hojas_ev = hoja(tiles, out / "hoja_eventos.jpg")

    paso = max(1.0, dur / 40.0)
    gen_tiles, t = [], 0.0
    k = 1
    while t < dur - 0.05:
        nombre = f"fotogramas/general_{k:03d}.jpg"
        extraer_fotograma(video, min(t + 0.05, dur - 0.05), out / nombre, ancho_tile)
        gen_tiles.append((out / nombre, f"{timecode(t, fps_tc)}"))
        t += paso
        k += 1
    hojas_gen = hoja(gen_tiles, out / "hoja_general.jpg", por_hoja=48)

    resultado = {
        "video": str(video),
        "duracion_s": round(dur, 3),
        "fps": round(fps, 3),
        "fps_timecode": fps_tc,
        "resolucion": f"{info['ancho']}x{info['alto']}",
        "vertical": vertical,
        "tiene_audio": info["tiene_audio"],
        "nota_timecode": ("Timecodes del video exportado, empiezan en 00:00:00:00. "
                          "Si la línea de tiempo empieza en 01:00:00:00 (típico en DaVinci), súmale 1 hora."),
        "audio": None if audio is None else {
            "mediana_db": round(audio["mediana"], 1),
            "p95_db": round(audio["p95"], 1),
            "umbral_pausa_db": round(audio["umbral"], 1),
        },
        "eventos": eventos,
        "pausas": [] if audio is None else [
            {"inicio": round(a, 2), "fin": round(b, 2), "dur": round(b - a, 2),
             "tc_inicio": timecode(a, fps_tc), "tc_fin": timecode(b, fps_tc)} for a, b in audio["pausas"]],
        "hojas_eventos": hojas_ev,
        "hojas_generales": hojas_gen,
    }
    (out / "analisis.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    cuenta = {k: sum(1 for e in eventos if e["tipo"] == k) for k in ("corte", "salto", "cambio")}
    print(f"Cortes: {cuenta['corte']} · saltos: {cuenta['salto']} · cambios en plano: {cuenta['cambio']} · "
          f"pausas de audio: {len(resultado['pausas'])}")
    print(f"{'#':>3}  {'timecode':<12} {'seg':>7}  {'tipo':<7} {'fuerza':>6}  {'audio dB':>8}  pausa")
    for e in eventos:
        sc = f"{e['fuerza']:.2f}" if e["fuerza"] is not None else "-"
        ad = f"{e['audio_db']:.1f}" if e["audio_db"] is not None else "-"
        pz = {True: "sí", False: "", None: "-"}[e["en_pausa"]]
        print(f"{e['id']:>3}  {e['tc']:<12} {e['t']:>7.2f}  {e['tipo']:<7} {sc:>6}  {ad:>8}  {pz}")
    if resultado["pausas"]:
        print("Pausas:", ", ".join(f"{p['inicio']:.2f}-{p['fin']:.2f}s" for p in resultado["pausas"]))
    print(f"\nListo. Mira {', '.join(hojas_ev + hojas_gen)} y analisis.json en:\n{out}")


if __name__ == "__main__":
    main()
