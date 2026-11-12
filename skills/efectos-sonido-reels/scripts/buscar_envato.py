#!/usr/bin/env python3
"""Busca efectos de sonido reales en Envato Elements.

Usa el servidor MCP público de Envato (https://mcp.envato.com/mcp), que no pide
iniciar sesión para buscar. Devuelve título, autor y enlace de cada resultado.
No descarga nada: para descargar hace falta la cuenta de Envato de la persona.

Uso:
  python buscar_envato.py "cinematic hit" "whoosh transition" [--n 3] [--max-seg 3]
  python buscar_envato.py --kit kit.json [--json resultados.json]

kit.json es una lista de búsquedas:
  [{"id": "hit", "termino": "cinematic hit", "max_seg": 2},
   {"id": "whoosh", "termino": "whoosh transition", "max_seg": 2, "categoria": "Transitions & Movement"},
   {"id": "pack_whoosh", "termino": "whoosh", "categoria": "Sound Packs"}]

Solo usa la biblioteca estándar de Python.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

URL = "https://mcp.envato.com/mcp"
CATEGORIAS = [
    "Game Sounds", "Transitions & Movement", "Domestic Sounds", "Human Sounds",
    "Urban Sounds", "Nature Sounds", "Futuristic Sounds", "Interface Sounds",
    "Cartoon Sounds", "Industrial Sounds", "Sound Packs",
]


class ErrorEnvato(Exception):
    pass


def llamar(herramienta, argumentos, timeout=30):
    cuerpo = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": herramienta, "arguments": argumentos},
    }).encode()
    req = urllib.request.Request(URL, data=cuerpo, headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "efectos-sonido-reels/1.0",
    })
    try:
        crudo = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise ErrorEnvato(f"no se pudo conectar con {URL}: {e}")
    datos = [l[5:].strip() for l in crudo.splitlines() if l.startswith("data:")]
    try:
        resp = json.loads(datos[0] if datos else crudo)
    except (json.JSONDecodeError, IndexError):
        raise ErrorEnvato(f"respuesta inesperada de Envato: {crudo[:200]}")
    if "error" in resp:
        raise ErrorEnvato(f"Envato devolvió un error: {resp['error']}")
    res = resp.get("result", {})
    if res.get("isError"):
        texto = " ".join(c.get("text", "") for c in res.get("content", []))
        raise ErrorEnvato(f"Envato rechazó la búsqueda: {texto[:300]}")
    for c in res.get("content", []):
        if c.get("type") == "text":
            try:
                return json.loads(c["text"])
            except json.JSONDecodeError:
                pass
    raise ErrorEnvato("la respuesta de Envato no trae resultados legibles")


def buscar(termino, n=3, max_seg=None, min_seg=None, categoria=None, orden="relevance", idioma="en"):
    filtros = {}
    if max_seg is not None:
        filtros["max_media_length"] = int(round(max_seg))
    if min_seg is not None:
        filtros["min_media_length"] = int(round(min_seg))
    if categoria:
        if categoria not in CATEGORIAS:
            raise ErrorEnvato(f"categoría desconocida '{categoria}'. Usa una de: {', '.join(CATEGORIAS)}")
        filtros["categories"] = categoria
    args = {"searchTerms": termino[:60], "perPage": max(1, min(20, n)),
            "sortBy": orden, "languageCode": idioma}
    if filtros:
        args["filters"] = filtros
    r = llamar("search_sound_effects", args)
    items = [{"titulo": (it.get("title") or "").strip(), "autor": it.get("author"),
              "enlace": it.get("item_url")} for it in r.get("items", [])]
    return items


def main():
    ap = argparse.ArgumentParser(description="Busca efectos de sonido reales en Envato Elements.")
    ap.add_argument("terminos", nargs="*", help="términos de búsqueda en inglés")
    ap.add_argument("--kit", help="JSON con una lista de búsquedas (id, termino, max_seg, min_seg, categoria, n)")
    ap.add_argument("--n", type=int, default=3, help="resultados por término (1-20, por defecto 3)")
    ap.add_argument("--max-seg", type=float, help="duración máxima del clip en segundos")
    ap.add_argument("--min-seg", type=float, help="duración mínima del clip en segundos")
    ap.add_argument("--categoria", help="categoría de Envato, p. ej. 'Transitions & Movement' o 'Sound Packs'")
    ap.add_argument("--orden", default="relevance", choices=["relevance", "popular", "latest"])
    ap.add_argument("--json", help="guarda los resultados en este archivo JSON")
    a = ap.parse_args()

    busquedas = []
    if a.kit:
        with open(a.kit, encoding="utf-8") as f:
            for i, b in enumerate(json.load(f)):
                busquedas.append({"id": b.get("id", str(i + 1)), "termino": b["termino"],
                                  "n": b.get("n", a.n), "max_seg": b.get("max_seg"),
                                  "min_seg": b.get("min_seg"), "categoria": b.get("categoria")})
    for t in a.terminos:
        busquedas.append({"id": t, "termino": t, "n": a.n, "max_seg": a.max_seg,
                          "min_seg": a.min_seg, "categoria": a.categoria})
    if not busquedas:
        ap.error("da al menos un término o --kit")

    salida, fallos = [], 0
    for b in busquedas:
        try:
            items = buscar(b["termino"], b["n"], b["max_seg"], b["min_seg"], b["categoria"], a.orden)
            error = None
        except ErrorEnvato as e:
            items, error = [], str(e)
            fallos += 1
        salida.append({**b, "resultados": items, "error": error})
        filtro = []
        if b["max_seg"] is not None:
            filtro.append(f"≤{b['max_seg']:g}s")
        if b["categoria"]:
            filtro.append(b["categoria"])
        print(f"\n## {b['id']}: \"{b['termino']}\"" + (f" ({', '.join(filtro)})" if filtro else ""))
        if error:
            print(f"   ERROR: {error}")
        elif not items:
            print("   sin resultados")
        for i, it in enumerate(items, 1):
            print(f"   {i}. {it['titulo']} — {it['autor']} — {it['enlace']}")

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(salida, f, ensure_ascii=False, indent=2)
        print(f"\nResultados guardados en {a.json}")
    if fallos == len(busquedas):
        print("\nNo se pudo buscar en Envato. Usa los términos y el enlace de búsqueda "
              "https://elements.envato.com/sound-effects/<termino-con-guiones>.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
