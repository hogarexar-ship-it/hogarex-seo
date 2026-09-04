# -*- coding: utf-8 -*-
"""
Genera una pagina estatica por cada trader publico y utilizable (con Slug,
nombre, rubro y ubicacion reales) de todos los rubros que devuelva la fuente
de datos - ya no se filtra por rubro ni por scoring, eso lo decide Bubble.

Fuente de datos (dos opciones, ver TRADERS_CSV_PATH mas abajo):
  - Export CSV completo de la tabla Trader de Bubble (recomendado: el
    Workflow API get_traders_publicos tiene un tope duro de 50 resultados
    que ignora cualquier parametro de paginacion - confirmado probando
    cursor/limit/page sin efecto - asi que no sirve para traer el total
    real, que a esta fecha son cientos de traders). El CSV se filtra por
    la columna `visibility` = "si" (autorizacion real de Bubble para
    mostrar el perfil publicamente) y NUNCA se usan las columnas `user` /
    `Creator` del CSV (son el email de la persona - dato sensible que no
    debe terminar en ningun HTML publico ni commitearse en texto plano).
  - Live API get_traders_publicos (POST), como fallback si no se pasa
    TRADERS_CSV_PATH - trae como mucho 50 traders por la limitacion de
    arriba.

Traders sin nombre/rubro/ubicacion (perfiles de alta incompleta, ver
is_usable) se omiten: no hay contenido real que publicar y una pagina vacia
no ayuda al SEO, ademas de exponer publicamente un registro incompleto que
la persona nunca termino de completar.

Ubicacion de cada pagina generada:
  - Rubro con hub propio (ver OFICIO_HUB) + ubicacion "Buenos Aires (CABA)"
    -> <hub>/<slug>/index.html (ej. electricistas/<slug>/, gasistas/<slug>/)
    (nested bajo el hub tematico correspondiente para agrupacion de SEO; URL
    final unica, sin contenido duplicado en /profesional/).
  - Cualquier otro caso (rubro sin hub propio todavia, u otra ubicacion)
    -> profesional/<slug>/index.html

Tambien actualiza:
  - sitemap-profesionales.xml (URLs de todas las paginas generadas, sea cual
    sea su carpeta). No se mezcla con sitemap.xml, que sigue siendo del blog.
  - <hub>/index.html de cada rubro en OFICIO_HUB: reemplaza el carrusel de
    tarjetas "Profesionales Destacados" (marcadores TRADER_CARDS_START/END)
    con los traders reales de CABA de ese rubro, linkeando a su propia pagina.

Uso: python3 generate_trader_pages.py   (ejecutar desde la raiz del repo)

Variables de entorno opcionales:
  TRADERS_CSV_PATH -> ruta a un export CSV de la tabla Trader (columnas de
                       Bubble tal cual, incluye header). Si se pasa, se usa
                       esto en vez del Workflow API.
  TRADERS_API_URL  -> para apuntar a version-test en vez de Live, ej:
                       https://hogarex.ar/version-test/api/1.1/wf/get_traders_publicos
"""
import csv
import html
import json
import os
import random
import shutil
import unicodedata
import urllib.request
from collections import Counter
from datetime import date
from urllib.parse import quote

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PROFESIONAL_DIR = os.path.join(REPO_ROOT, "profesional")
SITEMAP_PATH = os.path.join(REPO_ROOT, "sitemap-profesionales.xml")
HUB_CARDS_START = "<!-- TRADER_CARDS_START -->"
HUB_CARDS_END = "<!-- TRADER_CARDS_END -->"
SITE_ORIGIN = "https://app.hogarex.ar"
CABA_UBICACION = "Buenos Aires (CABA)"
API_URL = os.environ.get(
    "TRADERS_API_URL",
    "https://hogarex.ar/api/1.1/wf/get_traders_publicos",
)
CSV_PATH = os.environ.get("TRADERS_CSV_PATH")
USERS_CSV_PATH = os.environ.get("TRADERS_USERS_CSV_PATH")

# Rubros con hub propio en el repo (carpeta + index.html con carrusel de
# tarjetas ya existente). Un trader de CABA en uno de estos rubros se anida
# bajo su hub; el resto cae en /profesional/. Agregar un rubro nuevo aca
# requiere que exista <path>/index.html con los marcadores TRADER_CARDS.
OFICIO_HUB = {
    "Electricista": "/electricistas",
    "Gasista": "/gasistas",
    "Plomero": "/plomeros",
    "Pintor": "/pintores",
    "Carpintero": "/carpinteros",
    "Instalaciones": "/instalaciones",
}
# Rubros sin hub propio todavia (ej. Albañil, Herrero, Cerrajero): la
# breadcrumb y el link "ver mas" de esas paginas apuntan aca en vez de a un
# hub inexistente.
FALLBACK_HUB_URL = "https://app.hogarex.ar/profesionales"

def _icon_svg(paths, size=12):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">{paths}</svg>'
    )


ICON_ZAP = '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>'
ICON_FLAME = (
    '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 '
    '2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 '
    '1-3a2.5 2.5 0 0 0 2.5 2.5z"/>'
)
ICON_DROPLET = '<path d="M12 22c3.87 0 7-3.13 7-7 0-4-3-7-7-13-4 6-7 9-7 13 0 3.87 3.13 7 7 7Z"/>'
ICON_PAINTBRUSH = (
    '<path d="M18.37 2.63 14 7l-1.59-1.59a2 2 0 0 0-2.82 0L8 7l9 9 1.59-1.59a2 2 0 '
    '0 0 0-2.82L17 10l4.37-4.37a2.12 2.12 0 1 0-3-3Z"/><path d="M9 8c-2 3-4 3.5-7 4l8 8c2.5-2.5 3-4.5 4-7"/>'
)
ICON_HAMMER = (
    '<path d="m15 12-8.5 8.5a2.12 2.12 0 1 1-3-3L12 9"/><path d="M17.64 15 22 10.64"/>'
    '<path d="m20.91 11.7-1.25-1.25c-.6-.6-.93-1.4-.93-2.25v-.86L16.01 4.6a5.56 5.56 0 '
    '0 0-3.94-1.64H9l.92.82A6.18 6.18 0 0 1 12 8.4v1.56l2 2h2.47l2.26 1.91"/>'
)
ICON_WRENCH = (
    '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 '
    '7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'
)

# Icono decorativo por rubro (SVG en linea, sin emojis), usado en la tarjeta de
# /profesionales para dar identidad visual rapida.
OFICIO_ICON = {
    "Electricista": _icon_svg(ICON_ZAP),
    "Gasista": _icon_svg(ICON_FLAME),
    "Plomero": _icon_svg(ICON_DROPLET),
    "Pintor": _icon_svg(ICON_PAINTBRUSH),
    "Carpintero": _icon_svg(ICON_HAMMER),
    "Instalaciones": _icon_svg(ICON_WRENCH),
}
# Oficios fuera del set principal de rubros (Albañil, Cerrajero, Jardinero,
# Limpieza, Mudanzas, Herrero, etc.) usan un icono de herramienta generico.
FALLBACK_OFICIO_ICON = _icon_svg(ICON_WRENCH)


def _to_int(value):
    value = (value or "").strip()
    return int(value) if value.lstrip("-").isdigit() else None


def load_traders_from_csv(path):
    """Lee un export CSV de la tabla Trader de Bubble y lo normaliza al
    mismo formato de dict que devuelve la Live API, filtrando de una por
    `visibility` = "si". Deliberadamente NO mapea las columnas `user` ni
    `Creator` (email de la persona) - ese dato no debe llegar a ningun HTML
    generado."""
    traders = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("visibility") or "").strip().lower() != "si":
                continue
            zona_raw = (row.get("zonaCobertura") or "").strip()
            zonas = [z.strip() for z in zona_raw.split(" , ") if z.strip()] if zona_raw else []
            traders.append({
                "Slug": (row.get("Slug") or "").strip(),
                "main_field": (row.get("main_field") or "").strip() or None,
                "ubicacion": (row.get("ubicacion") or "").strip() or None,
                "user_name": (row.get("user_name") or "").strip() or None,
                "description": (row.get("description") or "").strip() or None,
                "zonaCobertura": zonas,
                "verified": (row.get("verified") or "").strip() or None,
                "portfolio": (row.get("portfolio") or "").strip() or None,
                "rating_count": _to_int(row.get("rating_count")),
                "rating-sum": _to_int(row.get("rating-sum")),
                "_uid": (row.get("unique id") or "").strip() or None,
            })
    return traders


def load_photo_map(path):
    """Lee un export CSV de la tabla User de Bubble y arma {uid_del_trader:
    url_de_la_foto}, SOLO para cuentas account_type=Trader con foto de
    perfil cargada. `trader_profile` en este CSV es el mismo id que `unique
    id` en el export de Trader (o `_id` en la Live API) - es el join key.

    Deliberadamente solo se leen las columnas `account_type`,
    `trader_profile` y `foto perfil `: el resto del CSV de usuarios trae
    email, nombre, apellido, googleID, whatsapp - datos sensibles que no
    se cargan en memoria mas alla de esta funcion y jamas se exponen en el
    HTML generado."""
    photos = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("account_type", "").strip('"') != "Trader":
                continue
            uid = (row.get("trader_profile") or "").strip()
            photo = (row.get("foto perfil ") or "").strip()
            if uid and photo:
                photos[uid] = photo
    return photos


def attach_photos(traders):
    """Suma trader['photo_url'] (https:// absoluta) cuando hay match real
    en el CSV de usuarios. No fabrica nada: los traders sin foto cargada
    simplemente no reciben el campo, y siguen usando el avatar con
    iniciales como hasta ahora."""
    if not USERS_CSV_PATH:
        return
    photo_map = load_photo_map(USERS_CSV_PATH)
    matched = 0
    for trader in traders:
        uid = trader.get("_uid")
        if uid and uid in photo_map:
            url = photo_map[uid]
            trader["photo_url"] = "https:" + url if url.startswith("//") else url
            matched += 1
    print(f"Fotos de perfil reales matcheadas: {matched}/{len(traders)}")


def fetch_traders():
    if CSV_PATH:
        return load_traders_from_csv(CSV_PATH)
    req = urllib.request.Request(API_URL, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    traders = data.get("response", {}).get("traders", [])
    for t in traders:
        t["_uid"] = t.get("_id")
    return traders


def _slug_token(text):
    """Normaliza texto a como aparece dentro de un slug de Bubble: sin
    acentos/diacriticos, minuscula (ej. 'Albañil' -> 'albanil',
    'Sebastián' -> 'sebastian')."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def derive_name_from_slug(slug, oficio):
    """Cuando `user_name` viene null en Bubble pero el slug si tiene el
    nombre codificado (bug real observado: ~30 traders con main_field y
    ubicacion completos pero user_name null - ej. 'yael-electricista-
    buenos-aires-gba' con user_name=null), se recupera el nombre del slug
    en vez de descartar un perfil que si tiene datos reales. No es una
    fabricacion: es el mismo nombre que la persona eligio al darse de alta,
    ya publico en la URL. Devuelve None si no se puede recuperar (slug sin
    el token de rubro, ej. altas totalmente vacias como 'daniel----3')."""
    if not slug or not oficio:
        return None
    tokens = slug.split("-")
    oficio_token = _slug_token(oficio)
    if oficio_token not in tokens:
        return None
    idx = tokens.index(oficio_token)
    name_parts = [t for t in tokens[:idx] if t]
    if not name_parts:
        return None
    return " ".join(p.capitalize() for p in name_parts)


def get_display_name(trader):
    return trader.get("user_name") or derive_name_from_slug(trader.get("Slug"), trader.get("main_field"))


def is_usable(trader):
    """Un trader es publicable si tiene los datos minimos para armar una
    pagina real: slug, nombre (real o recuperable del slug), rubro y
    ubicacion. Sin esto no hay nada que mostrar (son altas incompletas en
    Bubble, no perfiles listos)."""
    return bool(
        trader.get("Slug")
        and trader.get("main_field")
        and trader.get("ubicacion")
        and get_display_name(trader)
    )


def is_caba_with_hub(trader):
    return trader.get("main_field") in OFICIO_HUB and trader.get("ubicacion") == CABA_UBICACION


def oficio_hub_url_for(oficio):
    path = OFICIO_HUB.get(oficio)
    return f"{SITE_ORIGIN}{path}" if path else FALLBACK_HUB_URL


def pluralize_oficio(oficio):
    """Pluralizacion simple ('Electricista'->'Electricistas',
    'Pintor'->'Pintores', 'Albañil'->'Albañiles'): agrega 's' si termina en
    vocal, 'es' si termina en consonante. Cubre correctamente los 8 rubros
    que devuelve el endpoint hoy."""
    if oficio and oficio[-1].lower() in "aeiou":
        return oficio + "s"
    return oficio + "es"


def target_for(trader):
    """Devuelve (carpeta_absoluta, url_publica) para un trader.

    Los rubros con hub propio (OFICIO_HUB) y ubicacion CABA se anidan bajo
    ese hub (agrupacion tematica, URL canonica unica). El resto sigue en
    /profesional/<slug>/, como antes."""
    slug = trader["Slug"]
    if is_caba_with_hub(trader):
        hub_path = OFICIO_HUB[trader["main_field"]].lstrip("/")
        return os.path.join(REPO_ROOT, hub_path, slug), f"{SITE_ORIGIN}/{hub_path}/{slug}"
    return os.path.join(PROFESIONAL_DIR, slug), f"{SITE_ORIGIN}/profesional/{slug}"


def sanitize_description(text):
    """TODO (pendiente, decision 2026-08-31): portar aca el mismo regex que ya
    bloquea telefonos en Bubble al guardar el perfil, para tapar numeros que se
    hayan colado en descripciones viejas (ej. pegados al final del texto, caso
    real encontrado: un trader con un numero de whatsapp pegado en la bio).
    Por ahora se publica tal cual viene de la base, sin sanitizar."""
    return text


def get_rating(trader):
    """Devuelve (rating_value, review_count) solo si hay reseñas reales
    (rating_count > 0), o None si no hay dato. No se fabrica ni se
    interpola: 20 de los 22 traders actuales tienen 0 reseñas y no
    muestran nada de rating, ni en HTML ni en JSON-LD."""
    count = trader.get("rating_count")
    total = trader.get("rating-sum")
    if not count or not total:
        return None
    return round(total / count, 1), count


def build_faq_items(trader, name, oficio_lower):
    """Preguntas de alta intencion (tipo People Also Ask / AI Overviews),
    todas respondidas con datos reales del trader o con informacion generica
    y verdadera de como funciona Hogarex - nunca con afirmaciones inventadas
    sobre la persona."""
    ubicacion = trader.get("ubicacion") or ""
    zonas = trader.get("zonaCobertura") or []
    verified = trader.get("verified") == "Si"
    rating = get_rating(trader)

    items = [
        (
            f"¿En qué zonas trabaja {name}?",
            ("Cubre " + ", ".join(zonas) + ".") if zonas else f"Trabaja en {ubicacion}.",
        ),
    ]
    if rating:
        value, count = rating
        reseña_word = "reseña" if count == 1 else "reseñas"
        items.append((
            f"¿Qué calificación tiene {name} en Hogarex?",
            f"{value} de 5, según {count} {reseña_word} de clientes en Hogarex.",
        ))
    if verified:
        items.append((
            f"¿{name} está verificado en Hogarex?",
            "Sí, su perfil está verificado en Hogarex.",
        ))
    items.append((
        f"¿Cuánto cuesta pedir un presupuesto a {name}?",
        "Nada: pedir presupuesto en Hogarex es gratuito y sin compromiso.",
    ))
    items.append((
        f"¿Cómo contacto a {name} por Hogarex?",
        f"Completá el formulario de presupuesto y Hogarex te conecta directamente con {name} por WhatsApp, sin intermediarios.",
    ))
    return items


def build_jsonld(trader, url, oficio_hub_url, faq_items):
    name = get_display_name(trader) or "Profesional"
    oficio = trader.get("main_field") or ""
    ubicacion = trader.get("ubicacion") or ""
    zonas = trader.get("zonaCobertura") or []
    rating = get_rating(trader)

    person = {
        "@type": "Person",
        "@id": f"{url}#person",
        "name": name,
        "jobTitle": oficio,
        "address": {"@type": "PostalAddress", "addressLocality": ubicacion, "addressCountry": "AR"},
        "areaServed": zonas if zonas else [ubicacion],
        "worksFor": {"@type": "Organization", "name": "Hogarex", "url": "https://hogarex.ar"},
        "mainEntityOfPage": {"@id": f"{url}#webpage"},
    }
    if trader.get("photo_url"):
        person["image"] = trader["photo_url"]
    # aggregateRating solo cuando hay reseñas reales (rating_count > 0 en el
    # endpoint de Bubble). No es un self-rating de Hogarex sobre si misma
    # (el patron que Google restringe): son reseñas de clientes sobre un
    # tercero (el profesional), el mismo uso que hacen los marketplaces de
    # servicios (Yelp, Angi, etc.) al marcar a los negocios que listan.
    if rating:
        value, count = rating
        person["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": value,
            "reviewCount": count,
            "bestRating": 5,
            "worstRating": 1,
        }

    graph = [
        {
            "@type": "WebPage",
            "@id": f"{url}#webpage",
            "url": url,
            "name": f"{name} - {oficio} en {ubicacion} | Hogarex",
            "inLanguage": "es-AR",
            "breadcrumb": {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Inicio", "item": "https://hogarex.ar"},
                    {"@type": "ListItem", "position": 2, "name": oficio, "item": oficio_hub_url},
                    {"@type": "ListItem", "position": 3, "name": name, "item": url},
                ],
            },
        },
        person,
        {
            "@type": "FAQPage",
            "@id": f"{url}#faq",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
                for q, a in faq_items
            ],
        },
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


HAMBURGER_MENU_HTML = """<div class="hgx-nm-overlay" id="hgx-nm-overlay"></div>
<div class="hgx-nm-panel" id="hgx-nm-panel" aria-hidden="true">
  <div class="hgx-nm-panel-head">
    <span class="hgx-nm-logo">Hogarex</span>
    <button type="button" id="hgx-nm-close" class="hgx-nm-close" aria-label="Cerrar menú">&times;</button>
  </div>
  <nav class="hgx-nm-links" aria-label="Menú principal">
    <a href="https://hogarex.ar">Inicio</a>
    <span class="hgx-nm-label">Rubros</span>
    <div class="hgx-nm-grid">
      <a href="https://app.hogarex.ar/electricistas"><svg class="hgx-nm-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>Electricistas</a>
      <a href="https://app.hogarex.ar/gasistas"><svg class="hgx-nm-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>Gasistas</a>
      <a href="https://app.hogarex.ar/plomeros"><svg class="hgx-nm-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c3.87 0 7-3.13 7-7 0-4-3-7-7-13-4 6-7 9-7 13 0 3.87 3.13 7 7 7Z"/></svg>Plomeros</a>
      <a href="https://app.hogarex.ar/pintores"><svg class="hgx-nm-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18.37 2.63 14 7l-1.59-1.59a2 2 0 0 0-2.82 0L8 7l9 9 1.59-1.59a2 2 0 0 0 0-2.82L17 10l4.37-4.37a2.12 2.12 0 1 0-3-3Z"/><path d="M9 8c-2 3-4 3.5-7 4l8 8c2.5-2.5 3-4.5 4-7"/></svg>Pintores</a>
      <a href="https://app.hogarex.ar/carpinteros"><svg class="hgx-nm-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 12-8.5 8.5a2.12 2.12 0 1 1-3-3L12 9"/><path d="M17.64 15 22 10.64"/><path d="m20.91 11.7-1.25-1.25c-.6-.6-.93-1.4-.93-2.25v-.86L16.01 4.6a5.56 5.56 0 0 0-3.94-1.64H9l.92.82A6.18 6.18 0 0 1 12 8.4v1.56l2 2h2.47l2.26 1.91"/></svg>Carpinteros</a>
      <a href="https://app.hogarex.ar/instalaciones"><svg class="hgx-nm-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>Instalaciones</a>
    </div>
    <span class="hgx-nm-label">Explorar</span>
    <a href="https://app.hogarex.ar/profesionales">Explorar profesionales</a>
    <a href="https://app.hogarex.ar/precios-mano-de-obra">Precios de mano de obra</a>
    <span class="hgx-nm-label">Recursos</span>
    <a href="https://app.hogarex.ar/blog">Blog</a>
    <a href="https://app.hogarex.ar/preguntas-frecuentes">Preguntas Frecuentes</a>
    <a href="https://app.hogarex.ar/glosario">Glosario</a>
  </nav>
  <div class="hgx-nm-actions">
    <a href="https://hogarex.ar/busqueda" class="hgx-nm-btn hgx-nm-btn-outline">Buscar profesional</a>
    <a href="https://hogarex.ar/registro_profesional" class="hgx-nm-btn hgx-nm-btn-outline">Soy profesional</a>
    <a href="https://hogarex.ar/solicitud-enviar" class="hgx-nm-btn hgx-nm-btn-yellow">Pedir presupuesto gratis</a>
  </div>
</div>
<script>
(function(){
  var toggle=document.getElementById('hgx-nm-toggle');
  var panel=document.getElementById('hgx-nm-panel');
  var overlay=document.getElementById('hgx-nm-overlay');
  var closeBtn=document.getElementById('hgx-nm-close');
  function openMenu(){panel.classList.add('hgx-nm-open');overlay.classList.add('hgx-nm-open');panel.setAttribute('aria-hidden','false');toggle.setAttribute('aria-expanded','true');document.body.style.overflow='hidden';}
  function closeMenu(){panel.classList.remove('hgx-nm-open');overlay.classList.remove('hgx-nm-open');panel.setAttribute('aria-hidden','true');toggle.setAttribute('aria-expanded','false');document.body.style.overflow='';}
  if(toggle){toggle.addEventListener('click',openMenu);}
  if(closeBtn){closeBtn.addEventListener('click',closeMenu);}
  if(overlay){overlay.addEventListener('click',closeMenu);}
  document.addEventListener('keydown',function(e){if(e.key==='Escape')closeMenu();});
})();
</script>"""

HAMBURGER_MENU_CSS = """.hgx-nm-toggle{display:flex;flex-direction:column;justify-content:center;align-items:center;gap:5px;width:38px;height:38px;background:transparent;border:none;cursor:pointer;flex-shrink:0;padding:0;margin-left:6px}
    .hgx-nm-toggle span{display:block;width:22px;height:2.5px;background:#003366;border-radius:2px;transition:transform .25s ease,opacity .25s ease}
    .hgx-nm-toggle.hgx-nm-toggle-dark span{background:#ffffff}
    .hgx-nm-toggle[aria-expanded="true"] span:nth-child(1){transform:translateY(7.5px) rotate(45deg)}
    .hgx-nm-toggle[aria-expanded="true"] span:nth-child(2){opacity:0}
    .hgx-nm-toggle[aria-expanded="true"] span:nth-child(3){transform:translateY(-7.5px) rotate(-45deg)}
    .hgx-nm-overlay{position:fixed;inset:0;background:rgba(9,30,68,.5);opacity:0;visibility:hidden;transition:opacity .25s ease;z-index:998}
    .hgx-nm-overlay.hgx-nm-open{opacity:1;visibility:visible}
    .hgx-nm-panel{position:fixed;top:0;right:0;bottom:0;width:82%;max-width:320px;background:#fff;z-index:999;transform:translateX(100%);transition:transform .28s ease;display:flex;flex-direction:column;box-shadow:-8px 0 24px rgba(0,0,0,.15);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
    .hgx-nm-panel.hgx-nm-open{transform:translateX(0)}
    .hgx-nm-panel-head{display:flex;align-items:center;justify-content:space-between;padding:18px 20px;border-bottom:1px solid #eef1f6}
    .hgx-nm-logo{font-weight:800;font-size:17px;color:#003366;font-family:inherit}
    .hgx-nm-close{background:none;border:none;font-size:26px;line-height:1;color:#64708a;cursor:pointer;padding:4px 8px}
    .hgx-nm-links{display:flex;flex-direction:column;align-items:stretch;padding:10px 8px;overflow-y:auto;flex:1}
    .hgx-nm-links a{display:block;padding:13px 12px;color:#1a1a2e;text-decoration:none;font-weight:600;font-size:15px;border-radius:8px}
    .hgx-nm-links a:hover,.hgx-nm-links a:active{background:#f0f2f5}
    .hgx-nm-label{display:block;font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#9aa5b8;padding:16px 12px 6px}
    .hgx-nm-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px;padding:0 4px}
    .hgx-nm-grid a{padding:11px 8px;font-size:13px;line-height:1.25;display:flex;align-items:center;gap:6px}
    .hgx-nm-ic{width:15px;height:15px;flex-shrink:0;color:#206ff7}
    .hgx-nm-actions{display:flex;flex-direction:column;gap:8px;padding:14px 16px 20px;border-top:1px solid #eef1f6}
    .hgx-nm-btn{display:block;text-align:center;padding:12px;border-radius:999px;font-weight:700;font-size:14px;text-decoration:none}
    .hgx-nm-btn-outline{border:1.5px solid #003366;color:#003366;background:#fff}
    .hgx-nm-btn-yellow{background:#F5C518;color:#003366}
    @media (min-width:900px){.hgx-nm-panel{width:340px}}"""

HAMBURGER_TOGGLE_DARK = ('<button type="button" id="hgx-nm-toggle" class="hgx-nm-toggle hgx-nm-toggle-dark" '
                          'aria-label="Abrir menú" aria-expanded="false" aria-controls="hgx-nm-panel">'
                          '<span></span><span></span><span></span></button>')

# Footer identico en todo el sitio (mismos links de "Empresa/Soporte/Legal"
# y mismo directorio de barrios de CABA por rubro, para no fragmentar el link
# equity y darle a Google/LLMs una arquitectura de sitio consistente).
FOOTER_HTML = """<footer>
  <div class="ft-wrap">
    <div class="ft-grid">
      <div class="ft-col">
        <h5>Empresa</h5>
        <a href="mailto:soporte@hogarex.ar">Contacto</a>
        <a href="https://app.hogarex.ar">Inicio</a>
      </div>
      <div class="ft-col">
        <h5>Soporte</h5>
        <a href="https://hogarex.ar/ayuda">Ayuda</a>
        <a href="https://app.hogarex.ar/preguntas-frecuentes">Preguntas Frecuentes</a>
        <a href="https://app.hogarex.ar/glosario">Glosario</a>
        <a href="https://hogarex.ar/ayuda">Más información</a>
      </div>
      <div class="ft-col">
        <h5>Legal</h5>
        <a href="https://hogarex.ar/terminos-condiciones">Términos y Condiciones</a>
        <a href="https://hogarex.ar/terminos-condiciones">Privacidad</a>
      </div>
    </div>
    <div class="ft-directory">
      <div class="ft-directory-grid">
        <div class="ft-col"><h5>Electricistas</h5><a href="https://app.hogarex.ar/electricistas/caba/palermo">Palermo</a><a href="https://app.hogarex.ar/electricistas/caba/belgrano">Belgrano</a><a href="https://app.hogarex.ar/electricistas/caba/recoleta">Recoleta</a><a href="https://app.hogarex.ar/electricistas/caba/villa-crespo">Villa Crespo</a><a href="https://app.hogarex.ar/electricistas/caba/colegiales">Colegiales</a><a href="https://app.hogarex.ar/electricistas/caba/almagro">Almagro</a></div>
        <div class="ft-col"><h5>Plomeros</h5><a href="https://app.hogarex.ar/plomeros/caba/palermo">Palermo</a><a href="https://app.hogarex.ar/plomeros/caba/belgrano">Belgrano</a><a href="https://app.hogarex.ar/plomeros/caba/recoleta">Recoleta</a><a href="https://app.hogarex.ar/plomeros/caba/villa-crespo">Villa Crespo</a><a href="https://app.hogarex.ar/plomeros/caba/colegiales">Colegiales</a><a href="https://app.hogarex.ar/plomeros/caba/almagro">Almagro</a></div>
        <div class="ft-col"><h5>Gasistas</h5><a href="https://app.hogarex.ar/gasistas/caba/palermo">Palermo</a><a href="https://app.hogarex.ar/gasistas/caba/belgrano">Belgrano</a><a href="https://app.hogarex.ar/gasistas/caba/recoleta">Recoleta</a><a href="https://app.hogarex.ar/gasistas/caba/villa-crespo">Villa Crespo</a><a href="https://app.hogarex.ar/gasistas/caba/colegiales">Colegiales</a><a href="https://app.hogarex.ar/gasistas/caba/almagro">Almagro</a></div>
        <div class="ft-col"><h5>Pintores</h5><a href="https://app.hogarex.ar/pintores/caba/palermo">Palermo</a><a href="https://app.hogarex.ar/pintores/caba/belgrano">Belgrano</a><a href="https://app.hogarex.ar/pintores/caba/recoleta">Recoleta</a><a href="https://app.hogarex.ar/pintores/caba/villa-crespo">Villa Crespo</a><a href="https://app.hogarex.ar/pintores/caba/colegiales">Colegiales</a><a href="https://app.hogarex.ar/pintores/caba/almagro">Almagro</a></div>
        <div class="ft-col"><h5>Carpinteros</h5><a href="https://app.hogarex.ar/carpinteros/caba/palermo">Palermo</a><a href="https://app.hogarex.ar/carpinteros/caba/belgrano">Belgrano</a><a href="https://app.hogarex.ar/carpinteros/caba/recoleta">Recoleta</a><a href="https://app.hogarex.ar/carpinteros/caba/villa-crespo">Villa Crespo</a><a href="https://app.hogarex.ar/carpinteros/caba/colegiales">Colegiales</a><a href="https://app.hogarex.ar/carpinteros/caba/almagro">Almagro</a></div>
        <div class="ft-col"><h5>Instalaciones</h5><a href="https://app.hogarex.ar/instalaciones/caba/palermo">Palermo</a><a href="https://app.hogarex.ar/instalaciones/caba/belgrano">Belgrano</a><a href="https://app.hogarex.ar/instalaciones/caba/recoleta">Recoleta</a><a href="https://app.hogarex.ar/instalaciones/caba/villa-crespo">Villa Crespo</a><a href="https://app.hogarex.ar/instalaciones/caba/colegiales">Colegiales</a><a href="https://app.hogarex.ar/instalaciones/caba/almagro">Almagro</a></div>
      </div>
    </div>
    <div class="ft-bot">&copy; 2026 <a href="https://hogarex.ar">Hogarex</a> &mdash; Conectamos profesionales del hogar con clientes en Argentina.</div>
  </div>
</footer>"""

FOOTER_CSS = """footer{background:#fff;border-top:1px solid #eef1f6;padding:36px 16px 20px}
    .ft-wrap{max-width:1100px;margin:0 auto}
    .ft-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-bottom:20px}
    .ft-col h5{font-size:13px;font-weight:700;color:#111827;margin:0 0 10px}
    .ft-col a{display:block;font-size:13px;color:#6b7280;text-decoration:none;margin-bottom:6px}
    .ft-col a:hover{color:#206ff7}
    .ft-directory{margin-bottom:20px;padding-top:20px;border-top:1px solid #eef1f6}
    .ft-directory-grid{display:flex;flex-wrap:wrap;gap:24px}
    .ft-directory-grid .ft-col{min-width:120px}
    .ft-bot{font-size:12px;color:#9ca3af}
    .ft-bot a{color:#9ca3af;text-decoration:underline}
    @media(max-width:640px){.ft-grid{grid-template-columns:1fr 1fr}}
    @media(max-width:420px){.ft-grid{grid-template-columns:1fr}}"""


# Template mobile-first: los estilos base (sin media query) son los de mobile;
# @media (min-width:640px) agrega/ajusta para tablet+desktop. La barra de CTA
# fija abajo es el patron mobile habitual para perfiles de servicios locales;
# en desktop se oculta a favor de la tarjeta de CTA normal en el flujo.
PAGE_TEMPLATE = """<!-- generado automaticamente por generate_trader_pages.py - no editar a mano -->
<!DOCTYPE html>
<html lang="es-AR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title_esc} | Hogarex</title>
  <meta name="description" content="{meta_desc_esc}" />
  <link rel="canonical" href="{url}" />
  <meta name="theme-color" content="#003366" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet" />
  <meta property="og:type" content="profile" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{title_esc} | Hogarex" />
  <meta property="og:description" content="{meta_desc_esc}" />
  {og_image_html}
  <meta property="og:locale" content="es_AR" />
  <meta property="og:site_name" content="Hogarex" />
  <script type="application/ld+json">
{jsonld}
  </script>
  <style>
    :root {{
      --navy: #003366; --navy-dark: #091e44; --yellow: #F5C518; --yellow-hover: #e0b200;
      --white: #ffffff; --gray-50: #f8f9fb; --gray-100: #f0f2f5;
      --gray-500: #6b7280; --gray-700: #374151; --text: #1a1a2e; --radius: 12px;
      --shadow: 0 2px 16px rgba(13,42,94,0.10);
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ -webkit-text-size-adjust: 100%; }}
    body {{ font-family: 'Inter', sans-serif; background: var(--gray-50); color: var(--text); min-height: 100vh; padding-bottom: 88px; }}
    header {{ background: var(--navy); padding: 0 16px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.18); }}
    .header-inner {{ max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 56px; }}
    .logo {{ display: flex; align-items: center; text-decoration: none; }}
    .logo img {{ height: 26px; width: auto; display: block; }}
    nav {{ display: flex; align-items: center; gap: 8px; }}
    nav a {{ color: rgba(255,255,255,0.75); text-decoration: none; font-size: 0.85rem; font-weight: 500; }}
    nav .nav-home {{ display: none; }}
    nav .nav-cta {{ display: none; }}
    {menu_css}
    .profile-hero {{ max-width: 680px; margin: 0 auto 4px; padding: 0 16px 22px; text-align: center; position: relative; }}
    .hero-banner {{ height: 56px; background: var(--navy); margin: 0 -16px; display: flex; align-items: center; padding: 0 16px; }}
    .hero-back {{ color: #fff; text-decoration: none; font-size: 0.82rem; font-weight: 600; }}
    .hero-back:hover {{ text-decoration: underline; }}
    .hero-avatar-wrap {{ margin-top: -44px; margin-bottom: 12px; }}
    .profile-hero h1 {{ font-family: 'Sora', sans-serif; font-size: 1.4rem; font-weight: 700; color: var(--navy); line-height: 1.3; margin-bottom: 4px; }}
    .hero-subtitle {{ font-size: 0.95rem; font-weight: 600; color: #206ff7; margin-bottom: 14px; }}
    .hero-badges {{ display: flex; justify-content: center; align-items: center; gap: 8px; flex-wrap: wrap; }}
    .profile-content {{ max-width: 680px; margin: 0 auto; padding: 12px 16px; }}
    .profile-content p {{ font-size: 0.95rem; line-height: 1.7; color: var(--gray-700); margin-bottom: 14px; white-space: pre-line; }}
    .zonas {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px; }}
    .zona-chip {{ background: var(--gray-100); color: var(--gray-700); font-size: 0.78rem; padding: 4px 12px; border-radius: 999px; }}
    .verified-badge {{ display: inline-flex; align-items: center; gap: 5px; background: #e6f4ea; color: #1a7a3c; font-size: 0.8rem; font-weight: 700; padding: 6px 14px; border-radius: 999px; }}
    .rating-badge {{ display: inline-flex; align-items: center; gap: 5px; background: #fdf1de; color: #b45309; font-size: 0.8rem; font-weight: 700; padding: 6px 14px; border-radius: 999px; }}
    .profile-avatar {{ width: 92px; height: 92px; border-radius: 50%; background: var(--navy); color: #fff; display: flex; align-items: center; justify-content: center; font-family: 'Sora', sans-serif; font-weight: 700; font-size: 1.6rem; border: 4px solid #fff; box-shadow: 0 3px 12px rgba(0,0,0,.18); margin: 0 auto; }}
    .profile-avatar-img {{ width: 92px; height: 92px; border-radius: 50%; object-fit: cover; display: block; border: 4px solid #fff; box-shadow: 0 3px 12px rgba(0,0,0,.18); margin: 0 auto; }}
    .facts-card {{ background: var(--white); border: 1px solid var(--gray-100); border-radius: var(--radius); padding: 6px 16px; margin-bottom: 18px; }}
    .facts-row {{ display: flex; justify-content: space-between; gap: 12px; padding: 10px 0; font-size: 0.88rem; border-bottom: 1px solid var(--gray-100); }}
    .facts-row:last-child {{ border-bottom: none; }}
    .facts-row span {{ color: var(--gray-500); }}
    .facts-row strong {{ color: var(--text); font-weight: 600; text-align: right; }}
    .faq-section {{ margin-top: 22px; }}
    .faq-section h2 {{ font-family: 'Sora', sans-serif; font-size: 1.05rem; color: var(--navy); margin-bottom: 10px; }}
    .faq-item {{ background: var(--white); border: 1px solid var(--gray-100); border-radius: 10px; margin-bottom: 8px; padding: 2px 14px; }}
    .faq-item summary {{ cursor: pointer; font-weight: 600; font-size: 0.9rem; padding: 12px 0; color: var(--text); list-style: none; }}
    .faq-item summary::-webkit-details-marker {{ display: none; }}
    .faq-item summary::after {{ content: '+'; float: right; color: var(--gray-500); }}
    .faq-item[open] summary::after {{ content: '\\2212'; }}
    .faq-item p {{ font-size: 0.87rem; color: var(--gray-700); line-height: 1.6; padding-bottom: 12px; margin: 0; }}
    .ver-mas-link {{ display: inline-block; color: var(--navy); font-weight: 600; font-size: 0.88rem; text-decoration: none; margin: 18px 0 4px; }}
    .ver-mas-link:hover {{ text-decoration: underline; }}
    .btn-contact {{ display: block; width: 100%; text-align: center; margin: 6px 0 8px; }}
    .btn-full-profile {{ display: block; text-align: center; color: var(--navy); font-weight: 600; font-size: 0.85rem; text-decoration: none; margin: 0 0 20px; }}
    .btn-full-profile:hover {{ text-decoration: underline; }}
    .modal-cta {{ display: none; }}
    .btn-yellow {{ background: var(--yellow); color: var(--navy); font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.9rem; padding: 12px 22px; border-radius: 999px; text-decoration: none; border: none; cursor: pointer; white-space: nowrap; display: inline-block; text-align: center; }}
    .btn-yellow:hover {{ background: var(--yellow-hover); }}
    .cta-bar {{ position: fixed; left: 0; right: 0; bottom: 0; z-index: 90; background: var(--white); border-top: 1px solid var(--gray-100); box-shadow: 0 -2px 14px rgba(13,42,94,0.10); padding: 10px 16px calc(10px + env(safe-area-inset-bottom, 0px)); display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
    .cta-bar p {{ font-family: 'Sora', sans-serif; font-weight: 600; font-size: 0.85rem; color: var(--navy); margin: 0; line-height: 1.3; }}
    .cta-bar .btn-yellow {{ flex-shrink: 0; }}
{footer_css}

    @media (min-width: 640px) {{
      body {{ padding-bottom: 0; }}
      header {{ padding: 0 24px; }}
      .header-inner {{ height: 64px; }}
      .logo img {{ height: 32px; }}
      nav .nav-home {{ display: inline; color: rgba(255,255,255,0.75); text-decoration: none; font-size: 0.9rem; font-weight: 500; margin-right: 24px; }}
      nav .nav-cta {{ display: inline-block; background: var(--yellow); color: var(--navy); padding: 8px 18px; border-radius: 999px; font-weight: 700; font-family: 'Sora', sans-serif; }}
      .profile-hero, .profile-content {{ max-width: 740px; padding-left: 24px; padding-right: 24px; }}
      .profile-hero {{ padding-bottom: 26px; }}
      .hero-banner {{ height: 76px; padding: 0 24px; }}
      .hero-back {{ font-size: 0.88rem; }}
      .hero-avatar-wrap {{ margin-top: -58px; }}
      .profile-avatar, .profile-avatar-img {{ width: 120px; height: 120px; }}
      .profile-hero h1 {{ font-size: clamp(1.6rem, 3.2vw, 2rem); }}
      .hero-subtitle {{ font-size: 1.05rem; }}
      .cta-bar {{ display: none; }}
      .modal-cta {{ display: flex; margin: 24px auto 20px; max-width: 692px; padding: 20px 24px; background: var(--white); box-shadow: var(--shadow); border-radius: var(--radius); align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }}
      .modal-cta p {{ font-family: 'Sora', sans-serif; font-weight: 600; font-size: 0.95rem; color: var(--navy); margin: 0; }}
    }}
  </style>
</head>
<body>

<header>
  <div class="header-inner">
    <a href="https://hogarex.ar" class="logo"><img src="/blog/assets/logo-white.png" alt="Hogarex" /></a>
    <nav>
      <a href="https://hogarex.ar" class="nav-home">Inicio</a>
      <a href="https://hogarex.ar/solicitud-enviar" class="nav-cta">Recibir presupuesto gratis</a>
      <button type="button" id="hgx-nm-toggle" class="hgx-nm-toggle hgx-nm-toggle-dark" aria-label="Abrir menú" aria-expanded="false" aria-controls="hgx-nm-panel"><span></span><span></span><span></span></button>
    </nav>
  </div>
</header>

{menu_html}

<div class="profile-hero">
  <div class="hero-banner"><a href="{oficio_hub_url}" id="hgx-back" class="hero-back">&larr; Volver a {oficio_esc_lower}</a></div>
  <script>(function(){{var b=document.getElementById('hgx-back');if(document.referrer&&document.referrer.indexOf(location.hostname)!==-1&&history.length>1){{b.addEventListener('click',function(e){{e.preventDefault();history.back();}});}}}})();</script>
  <div class="hero-avatar-wrap">
    {avatar_html}
  </div>
  <h1>{name_esc}</h1>
  <p class="hero-subtitle">{oficio_esc} en {ubicacion_esc}</p>
  <div class="hero-badges">
    {verified_html}
    {rating_html}
  </div>
</div>

<main class="profile-content">
  {zonas_html}
  <div class="facts-card">
    {facts_html}
  </div>
  <a href="{contact_url}" class="btn-yellow btn-contact">Contactar a {name_esc}</a>
  <a href="{main_profile_url}" class="btn-full-profile">Ver perfil completo &rarr;</a>
  <p>{description_esc}</p>
  <section class="faq-section">
    <h2>Preguntas frecuentes</h2>
    {faq_html}
  </section>
  {ver_mas_html}
</main>

<div class="modal-cta">
  <p>&iquest;Necesit&aacute;s un {oficio_esc_lower} en {ubicacion_esc}?</p>
  <a href="{cta_url}" class="btn-yellow">{cta_label_esc}</a>
</div>

{footer_html}

<div class="cta-bar">
  <p>&iquest;Necesit&aacute;s un {oficio_esc_lower} en {ubicacion_esc}?</p>
  <a href="{cta_url}" class="btn-yellow">Pedir presupuesto</a>
</div>

</body>
</html>
"""

def render_page(trader, url):
    name = get_display_name(trader) or "Profesional"
    oficio = trader.get("main_field") or ""
    ubicacion = trader.get("ubicacion") or ""
    description = sanitize_description(trader.get("description") or "")
    zonas = trader.get("zonaCobertura") or []
    verified = trader.get("verified") == "Si"
    rating = get_rating(trader)
    oficio_hub_url = oficio_hub_url_for(oficio)
    photo_url = trader.get("photo_url")
    photo_alt = html.escape(f"{name}, {oficio} en {ubicacion}")

    if photo_url:
        avatar_html = (
            f'<img src="{html.escape(photo_url)}" alt="{photo_alt}" class="profile-avatar-img" '
            'loading="lazy" referrerpolicy="no-referrer" '
            "onerror=\"this.style.display='none';this.nextElementSibling.style.display='flex'\">"
            f'<div class="profile-avatar" style="display:none">{html.escape(get_initials(name))}</div>'
        )
        og_image_html = f'<meta property="og:image" content="{html.escape(photo_url)}" />'
    else:
        avatar_html = f'<div class="profile-avatar">{html.escape(get_initials(name))}</div>'
        og_image_html = ""

    zonas_html = ""
    if zonas:
        chips = "".join(f'<span class="zona-chip">{html.escape(z)}</span>' for z in zonas)
        zonas_html = f'<div class="zonas">{chips}</div>'

    verified_html = (
        '<span class="verified-badge"><svg width="12" height="12" fill="none" stroke="currentColor" '
        'stroke-width="3" viewBox="0 0 24 24"><polyline points="20,6 9,17 4,12"/></svg>'
        'Identidad Verificada</span>'
    ) if verified else ""

    rating_html = ""
    if rating:
        value, count = rating
        reseña_word = "reseña" if count == 1 else "reseñas"
        rating_html = (
            f'<span class="rating-badge">&#9733; {value} '
            f'<span style="color:var(--gray-500);font-weight:400">({count} {reseña_word})</span></span>'
        )

    facts_rows = [
        ("Rubro", html.escape(oficio)),
        ("Ubicación", html.escape(ubicacion)),
    ]
    if verified:
        facts_rows.append(("Verificado", '<span style="color:#1a7a3c">&check; Sí</span>'))
    if rating:
        value, count = rating
        facts_rows.append(("Calificación", f"&#9733; {value} ({count})"))
    facts_html = "".join(
        f'<div class="facts-row"><span>{label}</span><strong>{value}</strong></div>'
        for label, value in facts_rows
    )

    faq_items = build_faq_items(trader, name, oficio.lower())
    faq_html = "".join(
        f'<details class="faq-item"><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>'
        for q, a in faq_items
    )

    meta_desc = f"{name}, {oficio} en {ubicacion}. Pedi presupuesto gratis en Hogarex, sin intermediarios."
    cta_url = f"https://hogarex.ar/solicitud-enviar?rubro={quote(oficio)}&ubicacion={quote(ubicacion)}"
    # Boton de contacto directo a ESTE trader puntual (no generico por
    # rubro+ubicacion como cta_url): usa el mismo id que identifica al
    # trader (_uid, columna "unique id" en el CSV / _id en la Live API).
    contact_url = f"https://hogarex.ar/solicitud-enviar?trader={quote(trader['_uid'])}&rubro={quote(oficio)}"
    # Perfil completo del trader en el dominio principal (hogarex.ar), distinto
    # de esta pagina del subdominio app.hogarex.ar/{oficio}/{slug}.
    main_profile_url = f"https://hogarex.ar/perfilprofesional/{quote(trader['Slug'])}"
    # CTA con texto especifico de rubro+ubicacion (no generico "pedir presupuesto")
    # para intencion de busqueda alta y coincidencia semantica con la query.
    cta_label = f"Pedir presupuesto a un {oficio.lower()} en {ubicacion}"
    ver_mas_html = (
        f'<a href="{oficio_hub_url}" class="ver-mas-link">'
        f"Ver m&aacute;s {html.escape(pluralize_oficio(oficio).lower())} en {html.escape(ubicacion)} &rarr;</a>"
    )

    page_html = PAGE_TEMPLATE.format(
        title_esc=html.escape(f"{name} - {oficio} en {ubicacion}"),
        meta_desc_esc=html.escape(meta_desc),
        url=url,
        jsonld=build_jsonld(trader, url, oficio_hub_url, faq_items),
        oficio_esc=html.escape(oficio),
        oficio_esc_lower=html.escape(oficio.lower()),
        oficio_hub_url=oficio_hub_url,
        name_esc=html.escape(name),
        avatar_html=avatar_html,
        og_image_html=og_image_html,
        ubicacion_esc=html.escape(ubicacion),
        verified_html=verified_html,
        rating_html=rating_html,
        zonas_html=zonas_html,
        facts_html=facts_html,
        faq_html=faq_html,
        description_esc=html.escape(description),
        cta_url=cta_url,
        contact_url=contact_url,
        main_profile_url=main_profile_url,
        cta_label_esc=html.escape(cta_label),
        ver_mas_html=ver_mas_html,
        menu_css=HAMBURGER_MENU_CSS,
        menu_html=HAMBURGER_MENU_HTML,
        footer_css=FOOTER_CSS,
        footer_html=FOOTER_HTML,
    )
    return page_html


GENERATED_MARKER = "<!-- generado automaticamente por generate_trader_pages.py"
MANAGED_DIRS = [PROFESIONAL_DIR] + [os.path.join(REPO_ROOT, p.lstrip("/")) for p in OFICIO_HUB.values()]


def cleanup_stale_pages(traders):
    """Borra carpetas de perfiles generadas en corridas anteriores que ya no
    corresponden a ningun trader actual del endpoint (ej. el trader fue dado
    de baja o eliminado en Bubble - visto en la practica: 12 de 14
    electricistas de CABA de una corrida anterior ya no estaban en el
    endpoint). Solo borra carpetas cuyo index.html tiene GENERATED_MARKER
    como primera linea: paginas de terceros hechas a mano (ej.
    electricistas/caba/) nunca lo tienen y no se tocan."""
    valid_dirs = {target_for(t)[0] for t in traders if is_usable(t)}
    removed = []
    for root in MANAGED_DIRS:
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            path = os.path.join(root, name)
            if not os.path.isdir(path) or path in valid_dirs:
                continue
            index_path = os.path.join(path, "index.html")
            if not os.path.isfile(index_path):
                continue
            with open(index_path, encoding="utf-8") as f:
                first_line = f.readline()
            if GENERATED_MARKER not in first_line:
                continue
            shutil.rmtree(path)
            removed.append(os.path.relpath(path, REPO_ROOT))
    if removed:
        print(f"Paginas obsoletas eliminadas ({len(removed)} - traders que ya no estan en el endpoint):")
        for r in removed:
            print(f"  - {r}")
    return removed


def generate_pages(traders):
    urls = []
    skipped_slugs = []
    for trader in traders:
        if not is_usable(trader):
            skipped_slugs.append(trader.get("Slug") or trader.get("_id") or "(sin slug ni id)")
            continue
        page_dir, url = target_for(trader)
        os.makedirs(page_dir, exist_ok=True)
        page_html = render_page(trader, url)
        with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(page_html)
        urls.append(url)
    if skipped_slugs:
        print(f"Aviso: {len(skipped_slugs)} traders omitidos por datos incompletos "
              f"(sin nombre, rubro o ubicacion): {', '.join(skipped_slugs)}")
    return urls


def generate_sitemap(urls):
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', ""]
    for url in urls:
        lines += ["  <url>", f"    <loc>{url}</loc>", f"    <lastmod>{today}</lastmod>",
                  "    <changefreq>weekly</changefreq>",
                  "    <priority>0.75</priority>", "  </url>", ""]
    lines.append("</urlset>")
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


SITEMAP_INDEX_PATH = os.path.join(REPO_ROOT, "sitemap_index.xml")
SITEMAP_MAIN_PATH = os.path.join(REPO_ROOT, "sitemap.xml")


def generate_sitemap_index():
    """sitemap_index.xml agrupa sitemap.xml (paginas fijas, hubs, barrios y
    blog) y sitemap-profesionales.xml (682+ perfiles). Es el unico sitemap
    que hace falta dar de alta en Search Console."""
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', ""]
    for path in (SITEMAP_MAIN_PATH, SITEMAP_PATH):
        lines += ["  <sitemap>", f"    <loc>{SITE_ORIGIN}/{os.path.basename(path)}</loc>",
                   f"    <lastmod>{today}</lastmod>", "  </sitemap>", ""]
    lines.append("</sitemapindex>")
    with open(SITEMAP_INDEX_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


HUB_CARD_TEMPLATE = """      <div class="prof-card">
        <div class="prof-top">{avatar_html}{badge_html}</div>
        <div class="prof-name"><a href="{url}" style="color:inherit;text-decoration:none">{name_esc}</a></div>
        <div class="prof-rub">{oficio_esc} &middot; <span style="color:var(--t3);font-weight:400">{ubicacion_esc}</span></div>
        <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <div class="prof-desc">{description_esc}</div>
        <div class="prof-pop">&uarr; Popular</div>
        <a href="{pedir_url}" class="btn-pedir">Pedir presupuesto</a>
      </div>
"""

# Ciclo de colores de avatar solo decorativo (sin significado); None = color por
# defecto (var(--navy)) definido en el CSS de .prof-av.
HUB_AVATAR_COLORS = [
    None, "var(--blue)", "#065f46", "#0f766e", "#7c3aed",
    "#b45309", "#be123c", "#0e7490", "#4d7c0f", "#9d174d",
]


def get_initials(name):
    parts = [p for p in name.split() if p]
    if not parts:
        return "??"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()


def render_hub_card(trader, index, url):
    name = get_display_name(trader) or "Profesional"
    oficio = trader.get("main_field") or ""
    ubicacion = trader.get("ubicacion") or ""
    description = sanitize_description(trader.get("description") or "")
    verified = trader.get("verified") == "Si"

    photo_url = trader.get("photo_url")
    if photo_url:
        photo_alt = html.escape(f"{name}, {oficio} en {ubicacion}")
        avatar_html = (
            f'<img src="{html.escape(photo_url)}" alt="{photo_alt}" class="prof-av-img" '
            'loading="lazy" referrerpolicy="no-referrer" '
            "onerror=\"this.style.display='none';this.nextElementSibling.style.display='flex'\">"
            f'<div class="prof-av" style="display:none">{html.escape(get_initials(name))}</div>'
        )
    else:
        color = HUB_AVATAR_COLORS[index % len(HUB_AVATAR_COLORS)]
        avatar_style = f' style="background:{color}"' if color else ""
        avatar_html = f'<div class="prof-av"{avatar_style}>{html.escape(get_initials(name))}</div>'

    # Unico badge real: solo se muestra si el dato `verified` de Bubble es "Si".
    # No se fabrican afirmaciones de verificacion (identidad/matricula) sin dato
    # real detras - ver discusion 2026-08-31.
    badge_html = ""
    if verified:
        badge_html = (
            '<div style="display:flex;flex-direction:column;gap:4px;align-items:flex-end">'
            '<span class="vbadge"><svg width="12" height="12" fill="none" stroke="currentColor" '
            'stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20,6 9,17 4,12"/></svg>'
            "Perfil verificado</span></div>"
        )

    # El nombre linkea al perfil real del trader en Bubble (mismo slug); el
    # boton "Pedir presupuesto" va al formulario generico filtrado por rubro
    # y ubicacion, no al perfil de un trader puntual.
    cta_url = f"https://hogarex.ar/perfilprofesional/{quote(trader['Slug'])}"
    pedir_url = f"https://hogarex.ar/solicitud-enviar?rubro={quote(oficio)}&ubicacion={quote(ubicacion)}"

    return HUB_CARD_TEMPLATE.format(
        avatar_html=avatar_html,
        badge_html=badge_html,
        url=url,
        name_esc=html.escape(name),
        oficio_esc=html.escape(oficio),
        ubicacion_esc=html.escape(ubicacion),
        description_esc=html.escape(description),
        cta_url=cta_url,
        pedir_url=pedir_url,
    )


def update_hub_page(oficio, hub_path, traders):
    """Reemplaza el carrusel de 'Profesionales Destacados' en <hub_path>/index.html
    (marcadores TRADER_CARDS_START/END) con los traders reales de CABA de ese
    rubro, linkeando a su propia pagina. No toca el resto de la pagina."""
    page_path = os.path.join(REPO_ROOT, hub_path.lstrip("/"), "index.html")
    if not os.path.exists(page_path):
        print(f"Aviso: {hub_path}/index.html no encontrado, se omite actualizacion de tarjetas.")
        return

    with open(page_path, encoding="utf-8") as f:
        page_html = f.read()

    start_idx = page_html.find(HUB_CARDS_START)
    end_idx = page_html.find(HUB_CARDS_END)
    if start_idx == -1 or end_idx == -1:
        print(f"Aviso: marcadores TRADER_CARDS_START/END no encontrados en {hub_path}/index.html, se omite.")
        return

    caba_traders = [t for t in traders if is_usable(t) and t.get("main_field") == oficio
                     and t.get("ubicacion") == CABA_UBICACION]
    # perfiles verificados primero (siempre), el resto mantiene su orden.
    caba_traders.sort(key=lambda t: t.get("verified") != "Si")
    cards_html = "".join(
        render_hub_card(t, i, target_for(t)[1]) for i, t in enumerate(caba_traders)
    )

    new_page_html = (
        page_html[: start_idx + len(HUB_CARDS_START)]
        + "\n"
        + cards_html
        + page_html[end_idx:]
    )
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(new_page_html)
    print(f"Tarjetas actualizadas en {hub_path}/index.html: {len(caba_traders)} profesionales de CABA")


def update_hub_pages(traders):
    for oficio, hub_path in OFICIO_HUB.items():
        update_hub_page(oficio, hub_path, traders)


HOME_PAGE_PATH = os.path.join(REPO_ROOT, "index.html")
# La home no es de un rubro puntual: se muestra una muestra cruzada de todos
# los rubros, no los 682 (esto es una vidriera, el listado completo esta en
# /profesionales). Tope arbitrario para que el carrusel no sea interminable.
HOME_CARDS_CAP = 24

HOME_CARD_TEMPLATE = """      <div class="prof-card">
        <div class="prof-top">
          {avatar_html}
          {badge_html}
        </div>
        <div class="prof-name"><a href="{cta_url}" style="color:inherit;text-decoration:none">{name_esc}</a></div>
        <div class="prof-rub">{oficio_esc}</div>
        <div class="prof-desc">{description_esc}</div>
        <div class="prof-meta">
          <span class="prof-popular">&uarr; Popular</span>
          <span class="prof-loc" style="display:inline-flex;align-items:center;gap:4px"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>{ubicacion_esc}</span>
        </div>
        <a href="{pedir_url}" class="btn-pedir">Pedir presupuesto</a>
      </div>
"""


def render_home_card(trader, index):
    name = get_display_name(trader) or "Profesional"
    oficio = trader.get("main_field") or ""
    ubicacion = trader.get("ubicacion") or ""
    description = sanitize_description(trader.get("description") or "")
    verified = trader.get("verified") == "Si"

    photo_url = trader.get("photo_url")
    if photo_url:
        photo_alt = html.escape(f"{name}, {oficio} en {ubicacion}")
        avatar_html = (
            f'<img src="{html.escape(photo_url)}" alt="{photo_alt}" class="prof-av-img" '
            'loading="lazy" referrerpolicy="no-referrer" '
            "onerror=\"this.style.display='none';this.nextElementSibling.style.display='flex'\">"
            f'<div class="prof-av" style="display:none">{html.escape(get_initials(name))}</div>'
        )
    else:
        color = HUB_AVATAR_COLORS[index % len(HUB_AVATAR_COLORS)]
        avatar_style = f' style="background:{color}"' if color else ""
        avatar_html = f'<div class="prof-av"{avatar_style}>{html.escape(get_initials(name))}</div>'

    badge_html = ""
    if verified:
        badge_html = (
            '<div style="display:flex;flex-direction:column;gap:4px;align-items:flex-end">'
            '<span class="vbadge"><svg width="10" height="10" fill="none" stroke="currentColor" '
            'stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20,6 9,17 4,12"/></svg>'
            "Perfil verificado</span></div>"
        )

    # El nombre linkea al perfil real del trader; el boton "Pedir presupuesto"
    # va al formulario generico filtrado por rubro y ubicacion (no al perfil).
    cta_url = f"https://hogarex.ar/perfilprofesional/{quote(trader['Slug'])}"
    pedir_url = f"https://hogarex.ar/solicitud-enviar?rubro={quote(oficio)}&ubicacion={quote(ubicacion)}"

    return HOME_CARD_TEMPLATE.format(
        avatar_html=avatar_html,
        badge_html=badge_html,
        cta_url=cta_url,
        pedir_url=pedir_url,
        name_esc=html.escape(name),
        oficio_esc=html.escape(oficio),
        ubicacion_esc=html.escape(ubicacion),
        description_esc=html.escape(description),
    )


def _interleave_by_oficio(items, oficio_key):
    """Reordena una lista al azar de forma que nunca queden dos elementos
    seguidos del mismo rubro (salvo que un rubro domine tanto la lista que
    sea matematicamente inevitable)."""
    groups = {}
    for it in items:
        groups.setdefault(oficio_key(it), []).append(it)
    for g in groups.values():
        random.shuffle(g)

    result = []
    last_oficio = None
    while any(groups.values()):
        candidates = [o for o, g in groups.items() if g and o != last_oficio]
        if not candidates:
            candidates = [o for o, g in groups.items() if g]
        oficio = random.choice(candidates)
        result.append(groups[oficio].pop())
        last_oficio = oficio
    return result


def update_home_page(traders):
    """Reemplaza el carrusel 'Profesionales Verificados' de la home
    (marcadores TRADER_CARDS_START/END) con una muestra real cruzada de
    todos los rubros (hasta HOME_CARDS_CAP), en vez de las 10 tarjetas
    ficticias originales.

    La muestra se arma repartiendo cupos parejos entre rubros (para que
    ningun rubro domine el carrusel) priorizando perfiles verificados
    dentro de cada rubro, y despues se reordena al azar sin dejar dos
    tarjetas seguidas del mismo rubro - pero siempre con los perfiles
    verificados primero como bloque."""
    if not os.path.exists(HOME_PAGE_PATH):
        print("Aviso: index.html no encontrado, se omite actualizacion de tarjetas de home.")
        return

    with open(HOME_PAGE_PATH, encoding="utf-8") as f:
        page_html = f.read()

    start_idx = page_html.find(HUB_CARDS_START)
    end_idx = page_html.find(HUB_CARDS_END)
    if start_idx == -1 or end_idx == -1:
        print("Aviso: marcadores TRADER_CARDS_START/END no encontrados en index.html, se omite.")
        return

    usable = [t for t in traders if is_usable(t)]

    by_oficio = {}
    for t in usable:
        by_oficio.setdefault(t["main_field"], []).append(t)
    for g in by_oficio.values():
        # verificados primero, despues con foto primero (mejor primera
        # impresion) dentro de cada rubro, con orden aleatorio entre empates.
        random.shuffle(g)
        g.sort(key=lambda t: (t.get("verified") != "Si", t.get("photo_url") is None))

    oficios = list(by_oficio.keys())
    random.shuffle(oficios)
    pool = []
    i = 0
    while len(pool) < HOME_CARDS_CAP and any(by_oficio.values()):
        oficio = oficios[i % len(oficios)]
        if by_oficio[oficio]:
            pool.append(by_oficio[oficio].pop(0))
        i += 1

    verified_pool = [t for t in pool if t.get("verified") == "Si"]
    rest_pool = [t for t in pool if t.get("verified") != "Si"]
    sample = (_interleave_by_oficio(verified_pool, lambda t: t["main_field"])
              + _interleave_by_oficio(rest_pool, lambda t: t["main_field"]))

    cards_html = "".join(render_home_card(t, i) for i, t in enumerate(sample))

    new_page_html = (
        page_html[: start_idx + len(HUB_CARDS_START)]
        + "\n"
        + cards_html
        + page_html[end_idx:]
    )
    with open(HOME_PAGE_PATH, "w", encoding="utf-8") as f:
        f.write(new_page_html)
    print(f"Tarjetas actualizadas en index.html (home): {len(sample)} profesionales de distintos rubros")


EXPLORE_DIR = os.path.join(REPO_ROOT, "profesionales")
EXPLORE_PAGE_PATH = os.path.join(EXPLORE_DIR, "index.html")

EXPLORE_CARD_TEMPLATE = """        <a class="ex-card" href="{profile_url}" data-oficio="{oficio_attr}" data-ubicacion="{ubicacion_attr}">
          <div class="ex-top">
            {avatar_html}
            <div class="ex-id">
              <div class="ex-name">{name_esc}</div>
              <span class="ex-badge">{oficio_icon}{oficio_esc}</span>
            </div>
          </div>
          <p class="ex-desc">{description_esc}</p>
          <div class="ex-loc"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>{ubicacion_esc}</div>
          <div class="ex-foot">
            {rating_html}
            {verified_html}
          </div>
          <div class="ex-cta"><span>Pedir presupuesto &rarr;</span></div>
        </a>
"""

EXPLORE_PAGE_TEMPLATE = """<!-- generado automaticamente por generate_trader_pages.py - no editar a mano -->
<!DOCTYPE html>
<html lang="es-AR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Explorá todos los profesionales de Hogarex | Electricistas, gasistas, plomeros y más</title>
  <meta name="description" content="Buscá entre {total} profesionales de Hogarex: electricistas, gasistas, plomeros, pintores, carpinteros y más. Filtrá por rubro y zona." />
  <link rel="canonical" href="https://app.hogarex.ar/profesionales" />
  <meta name="theme-color" content="#003366" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://app.hogarex.ar/profesionales" />
  <meta property="og:title" content="Explorá todos los profesionales de Hogarex" />
  <meta property="og:description" content="Buscá entre {total} profesionales de Hogarex: electricistas, gasistas, plomeros, pintores, carpinteros y más." />
  <meta property="og:locale" content="es_AR" />
  <meta property="og:site_name" content="Hogarex" />
  <script type="application/ld+json">
{{"@context":"https://schema.org","@graph":[{{"@type":"WebPage","@id":"https://app.hogarex.ar/profesionales#webpage","url":"https://app.hogarex.ar/profesionales","name":"Explorá todos los profesionales de Hogarex","inLanguage":"es-AR","breadcrumb":{{"@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Inicio","item":"https://hogarex.ar"}},{{"@type":"ListItem","position":2,"name":"Profesionales","item":"https://app.hogarex.ar/profesionales"}}]}}}}]}}
  </script>
  <style>
    :root {{
      --navy: #003366; --navy-dark: #091e44; --yellow: #F5C518; --yellow-hover: #e0b200;
      --white: #ffffff; --gray-50: #f8f9fb; --gray-100: #f0f2f5;
      --gray-500: #6b7280; --gray-700: #374151; --text: #1a1a2e; --radius: 12px;
      --shadow: 0 2px 16px rgba(13,42,94,0.10);
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ -webkit-text-size-adjust: 100%; }}
    body {{ font-family: 'Inter', sans-serif; background: var(--gray-50); color: var(--text); min-height: 100vh; }}
    header {{ background: var(--navy); padding: 0 16px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.18); }}
    .header-inner {{ max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 56px; }}
    .logo {{ display: flex; align-items: center; text-decoration: none; }}
    .logo img {{ height: 26px; width: auto; display: block; }}
    nav {{ display: flex; align-items: center; gap: 8px; }}
    nav a {{ color: rgba(255,255,255,0.75); text-decoration: none; font-size: 0.85rem; font-weight: 500; }}
    nav .nav-home {{ display: none; }}
    nav .nav-cta {{ display: none; background: var(--yellow); color: var(--navy); padding: 8px 16px; border-radius: 999px; font-weight: 700; font-family: 'Sora', sans-serif; font-size: 0.8rem; }}
    .breadcrumb {{ max-width: 1100px; margin: 0 auto; padding: 16px 16px 0; }}
    .breadcrumb a {{ color: var(--gray-500); text-decoration: none; font-size: 0.82rem; font-weight: 500; }}
    .hero {{ max-width: 1100px; margin: 0 auto; padding: 14px 16px 4px; }}
    .hero h1 {{ font-family: 'Sora', sans-serif; font-size: 1.4rem; font-weight: 800; color: var(--navy); line-height: 1.28; margin-bottom: 8px; }}
    .hero p {{ font-size: 0.92rem; color: var(--gray-700); line-height: 1.6; }}
    .filters {{ max-width: 1100px; margin: 0 auto; padding: 14px 16px; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; position: sticky; top: 56px; background: var(--gray-50); z-index: 50; border-bottom: 1px solid var(--gray-100); }}
    .filters select {{ flex: 1; min-width: 140px; padding: 10px 12px; border-radius: 10px; border: 1.5px solid var(--gray-100); background: var(--white); font-size: 0.88rem; font-family: inherit; color: var(--text); }}
    .filters .ex-count {{ font-size: 0.82rem; color: var(--gray-500); width: 100%; order: 3; }}
    .ex-grid {{ max-width: 1100px; margin: 0 auto; padding: 8px 16px 40px; display: grid; grid-template-columns: 1fr; gap: 14px; }}
    .ex-card {{ display: flex; flex-direction: column; min-width: 0; background: var(--white); border: 1px solid var(--gray-100); border-radius: 14px; padding: 16px; text-decoration: none; color: inherit; box-shadow: 0 1px 3px rgba(13,42,94,.06); transition: box-shadow .18s ease, transform .18s ease, border-color .18s ease; }}
    .ex-card:hover {{ box-shadow: var(--shadow); transform: translateY(-2px); border-color: rgba(32,111,247,.25); }}
    .ex-top {{ display: flex; align-items: center; gap: 12px; margin-bottom: 10px; min-width: 0; }}
    .ex-av {{ width: 46px; height: 46px; border-radius: 50%; background: var(--navy); color: #fff; display: flex; align-items: center; justify-content: center; font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.92rem; flex-shrink: 0; }}
    .ex-av-img {{ width: 46px; height: 46px; border-radius: 50%; object-fit: cover; flex-shrink: 0; display: block; }}
    .ex-id {{ min-width: 0; }}
    .ex-name {{ font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.98rem; color: var(--navy); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .ex-badge {{ display: inline-flex; align-items: center; gap: 4px; background: rgba(32,111,247,.08); color: var(--navy); font-size: 0.72rem; font-weight: 700; padding: 2px 9px 2px 7px; border-radius: 999px; margin-top: 4px; }}
    .ex-desc {{ font-size: 0.85rem; color: var(--gray-700); line-height: 1.5; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-width: 0; }}
    .ex-loc {{ display: flex; align-items: center; gap: 5px; font-size: 0.78rem; color: var(--gray-500); margin-bottom: 10px; }}
    .ex-loc svg {{ flex-shrink: 0; color: var(--gray-500); }}
    .ex-foot {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; min-height: 18px; }}
    .ex-rating {{ font-size: 0.8rem; color: #b45309; font-weight: 600; }}
    .ex-verified {{ display: inline-flex; align-items: center; gap: 3px; font-size: 0.78rem; color: #1a7a3c; font-weight: 700; background: rgba(26,122,60,.08); padding: 2px 9px; border-radius: 999px; }}
    .ex-cta {{ display: block; text-align: center; margin-top: auto; padding-top: 12px; }}
    .ex-cta span {{ display: inline-block; width: 100%; padding: 9px; border: 1.5px solid var(--navy); border-radius: 999px; color: var(--navy); font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.82rem; text-align: center; transition: background .18s ease, color .18s ease; }}
    .ex-card:hover .ex-cta span {{ background: var(--navy); color: #fff; }}
    .ex-empty {{ text-align: center; color: var(--gray-500); font-size: 0.9rem; padding: 40px 16px; }}
{footer_css}

    {menu_css}

    @media (min-width: 640px) {{
      header {{ padding: 0 24px; }}
      .header-inner {{ height: 64px; }}
      .logo img {{ height: 32px; }}
      nav .nav-home {{ display: inline; color: rgba(255,255,255,0.75); text-decoration: none; font-size: 0.9rem; font-weight: 500; margin-right: 24px; }}
      nav .nav-cta {{ display: inline-block; padding: 8px 18px; font-size: 0.9rem; }}
      .breadcrumb, .hero, .filters, .ex-grid {{ max-width: 1100px; padding-left: 24px; padding-right: 24px; }}
      .hero {{ padding-top: 24px; }}
      .hero h1 {{ font-size: clamp(1.5rem, 3vw, 2rem); }}
      .filters {{ top: 64px; }}
      .ex-grid {{ grid-template-columns: repeat(2, 1fr); gap: 16px; }}
    }}
    @media (min-width: 960px) {{
      .ex-grid {{ grid-template-columns: repeat(3, 1fr); }}
    }}
  </style>
</head>
<body>

<header>
  <div class="header-inner">
    <a href="https://hogarex.ar" class="logo"><img src="/blog/assets/logo-white.png" alt="Hogarex" /></a>
    <nav>
      <a href="https://hogarex.ar" class="nav-home">Inicio</a>
      <a href="https://hogarex.ar/solicitud-enviar" class="nav-cta">Recibir presupuesto gratis</a>
      <button type="button" id="hgx-nm-toggle" class="hgx-nm-toggle hgx-nm-toggle-dark" aria-label="Abrir menú" aria-expanded="false" aria-controls="hgx-nm-panel"><span></span><span></span><span></span></button>
    </nav>
  </div>
</header>

<div class="breadcrumb"><a href="https://hogarex.ar">&larr; Inicio</a></div>

<div class="hero">
  <h1>Explorá todos los profesionales de Hogarex</h1>
  <p>{total} profesionales listos para tu presupuesto. Filtrá por rubro y zona.</p>
</div>

<div class="filters">
  <select id="filterOficio" onchange="hgxFilter()">
    <option value="">Todos los rubros</option>
{oficio_options}
  </select>
  <select id="filterUbicacion" onchange="hgxFilter()">
    <option value="">Todas las zonas</option>
{ubicacion_options}
  </select>
  <span class="ex-count" id="exCount">{total} profesionales encontrados</span>
</div>

<div class="ex-grid" id="exGrid">
{cards_html}
</div>
<p class="ex-empty" id="exEmpty" style="display:none">Ningún profesional coincide con ese filtro. Probá con otra combinación.</p>

{footer_html}

{menu_html}

<script>
function hgxFilter() {{
  var oficio = document.getElementById('filterOficio').value;
  var ubicacion = document.getElementById('filterUbicacion').value;
  var cards = document.querySelectorAll('.ex-card');
  var visible = 0;
  cards.forEach(function(c) {{
    var show = (!oficio || c.dataset.oficio === oficio) && (!ubicacion || c.dataset.ubicacion === ubicacion);
    c.style.display = show ? '' : 'none';
    if (show) visible++;
  }});
  document.getElementById('exCount').textContent = visible + ' profesional' + (visible === 1 ? '' : 'es') + ' encontrado' + (visible === 1 ? '' : 's');
  document.getElementById('exEmpty').style.display = visible === 0 ? 'block' : 'none';
}}
</script>

</body>
</html>
"""


def render_explore_card(trader):
    name = get_display_name(trader) or "Profesional"
    oficio = trader.get("main_field") or ""
    ubicacion = trader.get("ubicacion") or ""
    description = sanitize_description(trader.get("description") or "")
    verified = trader.get("verified") == "Si"
    rating = get_rating(trader)
    profile_url = target_for(trader)[1]

    photo_url = trader.get("photo_url")
    if photo_url:
        photo_alt = html.escape(f"{name}, {oficio} en {ubicacion}")
        avatar_html = (
            f'<img src="{html.escape(photo_url)}" alt="{photo_alt}" class="ex-av-img" '
            'loading="lazy" referrerpolicy="no-referrer" '
            "onerror=\"this.style.display='none';this.nextElementSibling.style.display='flex'\">"
            f'<div class="ex-av" style="display:none">{html.escape(get_initials(name))}</div>'
        )
    else:
        avatar_html = f'<div class="ex-av">{html.escape(get_initials(name))}</div>'

    rating_html = ""
    if rating:
        value, count = rating
        reseña_word = "reseña" if count == 1 else "reseñas"
        rating_html = f'<span class="ex-rating">&#9733; {value} ({count} {reseña_word})</span>'

    verified_html = '<span class="ex-verified">&check; Verificado</span>' if verified else ""

    return EXPLORE_CARD_TEMPLATE.format(
        profile_url=profile_url,
        oficio_attr=html.escape(oficio),
        ubicacion_attr=html.escape(ubicacion),
        avatar_html=avatar_html,
        name_esc=html.escape(name),
        oficio_esc=html.escape(oficio),
        oficio_icon=OFICIO_ICON.get(oficio, FALLBACK_OFICIO_ICON),
        ubicacion_esc=html.escape(ubicacion),
        description_esc=html.escape(description),
        rating_html=rating_html,
        verified_html=verified_html,
    )


def generate_explore_page(traders):
    usable = [t for t in traders if is_usable(t)]
    # perfiles verificados primero (siempre), despues agrupados por rubro y nombre.
    usable.sort(key=lambda t: (t.get("verified") != "Si", t["main_field"], get_display_name(t) or ""))

    oficios = sorted({t["main_field"] for t in usable})
    ubicaciones = sorted({t["ubicacion"] for t in usable})

    oficio_options = "\n".join(
        f'    <option value="{html.escape(o)}">{html.escape(o)}</option>' for o in oficios
    )
    ubicacion_options = "\n".join(
        f'    <option value="{html.escape(u)}">{html.escape(u)}</option>' for u in ubicaciones
    )
    cards_html = "".join(render_explore_card(t) for t in usable)

    os.makedirs(EXPLORE_DIR, exist_ok=True)
    page_html = EXPLORE_PAGE_TEMPLATE.format(
        total=len(usable),
        oficio_options=oficio_options,
        ubicacion_options=ubicacion_options,
        cards_html=cards_html,
        menu_css=HAMBURGER_MENU_CSS,
        menu_html=HAMBURGER_MENU_HTML,
        footer_css=FOOTER_CSS,
        footer_html=FOOTER_HTML,
    )
    with open(EXPLORE_PAGE_PATH, "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"Pagina de exploracion generada: profesionales/index.html ({len(usable)} profesionales, "
          f"{len(oficios)} rubros, {len(ubicaciones)} zonas)")
    return f"{SITE_ORIGIN}/profesionales"


def main():
    traders = fetch_traders()
    print(f"Traders recibidos del endpoint: {len(traders)}")
    attach_photos(traders)
    usable = [t for t in traders if is_usable(t)]
    print(f"Traders utilizables (con nombre, rubro y ubicacion): {len(usable)}")
    por_rubro = Counter(t["main_field"] for t in usable)
    for oficio, count in sorted(por_rubro.items()):
        print(f"  - {oficio}: {count}")
    cleanup_stale_pages(traders)
    urls = generate_pages(traders)
    generate_sitemap(urls)
    update_hub_pages(traders)
    update_home_page(traders)
    explore_url = generate_explore_page(traders)
    generate_sitemap_index()
    print(f"Paginas generadas: {len(urls)}")
    print(f"Sitemap escrito en: {SITEMAP_PATH}")
    print(f"Sitemap index escrito en: {SITEMAP_INDEX_PATH}")
    return explore_url


if __name__ == "__main__":
    main()
