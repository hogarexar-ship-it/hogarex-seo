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
FALLBACK_HUB_URL = "https://hogarex.ar/busqueda"


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
    .logo {{ color: var(--white); font-family: 'Sora', sans-serif; font-weight: 700; font-size: 1rem; text-decoration: none; }}
    nav a {{ color: rgba(255,255,255,0.75); text-decoration: none; font-size: 0.85rem; font-weight: 500; }}
    nav .nav-home {{ display: none; }}
    .breadcrumb {{ max-width: 680px; margin: 0 auto; padding: 16px 16px 0; }}
    .breadcrumb a {{ color: var(--gray-500); text-decoration: none; font-size: 0.82rem; font-weight: 500; }}
    .profile-hero {{ max-width: 680px; margin: 0 auto; padding: 14px 16px 6px; }}
    .profile-tag {{ display: inline-block; background: var(--yellow); color: var(--navy); font-size: 0.7rem; font-weight: 700; padding: 3px 12px; border-radius: 999px; margin-bottom: 12px; }}
    .profile-hero h1 {{ font-family: 'Sora', sans-serif; font-size: 1.4rem; font-weight: 700; color: var(--navy); line-height: 1.3; margin-bottom: 10px; }}
    .profile-meta {{ display: flex; gap: 14px; flex-wrap: wrap; align-items: center; font-size: 0.88rem; color: var(--gray-500); margin-bottom: 16px; }}
    .profile-content {{ max-width: 680px; margin: 0 auto; padding: 12px 16px; }}
    .profile-content p {{ font-size: 0.95rem; line-height: 1.7; color: var(--gray-700); margin-bottom: 14px; white-space: pre-line; }}
    .zonas {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px; }}
    .zona-chip {{ background: var(--gray-100); color: var(--gray-700); font-size: 0.78rem; padding: 4px 12px; border-radius: 999px; }}
    .verified-badge {{ display: inline-flex; align-items: center; gap: 4px; color: #1a7a3c; font-size: 0.85rem; font-weight: 600; }}
    .rating-badge {{ display: inline-flex; align-items: center; gap: 4px; color: #b45309; font-weight: 600; }}
    .hero-top {{ display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }}
    .profile-avatar {{ width: 52px; height: 52px; border-radius: 50%; background: var(--navy); color: #fff; display: flex; align-items: center; justify-content: center; font-family: 'Sora', sans-serif; font-weight: 700; font-size: 1.05rem; flex-shrink: 0; }}
    .profile-avatar-img {{ width: 52px; height: 52px; border-radius: 50%; object-fit: cover; flex-shrink: 0; display: block; }}
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
    .modal-cta {{ display: none; }}
    .btn-yellow {{ background: var(--yellow); color: var(--navy); font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.9rem; padding: 12px 22px; border-radius: 999px; text-decoration: none; border: none; cursor: pointer; white-space: nowrap; display: inline-block; text-align: center; }}
    .btn-yellow:hover {{ background: var(--yellow-hover); }}
    .cta-bar {{ position: fixed; left: 0; right: 0; bottom: 0; z-index: 90; background: var(--white); border-top: 1px solid var(--gray-100); box-shadow: 0 -2px 14px rgba(13,42,94,0.10); padding: 10px 16px calc(10px + env(safe-area-inset-bottom, 0px)); display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
    .cta-bar p {{ font-family: 'Sora', sans-serif; font-weight: 600; font-size: 0.85rem; color: var(--navy); margin: 0; line-height: 1.3; }}
    .cta-bar .btn-yellow {{ flex-shrink: 0; }}
    footer {{ background: var(--navy-dark); color: rgba(255,255,255,0.5); text-align: center; padding: 24px 16px; font-size: 0.8rem; margin-top: 20px; }}
    footer a {{ color: var(--yellow); text-decoration: none; }}

    @media (min-width: 640px) {{
      body {{ padding-bottom: 0; }}
      header {{ padding: 0 24px; }}
      .header-inner {{ height: 64px; }}
      .logo {{ font-size: 1.1rem; }}
      nav {{ display: flex; align-items: center; }}
      nav .nav-home {{ display: inline; color: rgba(255,255,255,0.75); text-decoration: none; font-size: 0.9rem; font-weight: 500; margin-right: 24px; }}
      nav .nav-cta {{ background: var(--yellow); color: var(--navy); padding: 8px 18px; border-radius: 999px; font-weight: 700; font-family: 'Sora', sans-serif; }}
      .breadcrumb, .profile-hero, .profile-content {{ max-width: 740px; padding-left: 24px; padding-right: 24px; }}
      .profile-hero {{ padding-top: 16px; padding-bottom: 8px; }}
      .profile-hero h1 {{ font-size: clamp(1.3rem, 3.2vw, 1.8rem); }}
      .cta-bar {{ display: none; }}
      .modal-cta {{ display: flex; margin: 24px auto 20px; max-width: 692px; padding: 20px 24px; background: var(--white); box-shadow: var(--shadow); border-radius: var(--radius); align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }}
      .modal-cta p {{ font-family: 'Sora', sans-serif; font-weight: 600; font-size: 0.95rem; color: var(--navy); margin: 0; }}
      footer {{ padding: 28px 24px; font-size: 0.82rem; margin-top: 24px; }}
    }}
  </style>
</head>
<body>

<header>
  <div class="header-inner">
    <a href="https://hogarex.ar" class="logo">Hogarex</a>
    <nav>
      <a href="https://hogarex.ar" class="nav-home">Inicio</a>
      <a href="https://hogarex.ar/solicitud-enviar" class="nav-cta">Recibir presupuesto gratis</a>
    </nav>
  </div>
</header>

<div class="breadcrumb"><a href="{oficio_hub_url}">&larr; Volver a {oficio_esc_lower}</a></div>

<div class="profile-hero">
  <div class="hero-top">
    {avatar_html}
    <span class="profile-tag">{oficio_esc}</span>
  </div>
  <h1>{name_esc} &mdash; {oficio_esc} en {ubicacion_esc}</h1>
  <div class="profile-meta">
    <span>&#128205; {ubicacion_esc}</span>
    {rating_html}
    {verified_html}
  </div>
</div>

<main class="profile-content">
  {zonas_html}
  <div class="facts-card">
    {facts_html}
  </div>
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

<footer>
  <p>&copy; 2026 <a href="https://hogarex.ar">Hogarex</a> &mdash; Conectamos profesionales del hogar con clientes en Argentina.</p>
</footer>

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

    verified_html = '<span class="verified-badge">&check; Perfil verificado</span>' if verified else ""

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
        cta_label_esc=html.escape(cta_label),
        ver_mas_html=ver_mas_html,
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


HUB_CARD_TEMPLATE = """      <div class="prof-card">
        <div class="prof-top">{avatar_html}{badge_html}</div>
        <div class="prof-name"><a href="{url}" style="color:inherit;text-decoration:none">{name_esc}</a></div>
        <div class="prof-rub">{oficio_esc} &middot; <span style="color:var(--t3);font-weight:400">{ubicacion_esc}</span></div>
        <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <div class="prof-desc">{description_esc}</div>
        <div class="prof-pop">&uarr; Popular</div>
        <a href="{cta_url}" class="btn-pedir">Pedir presupuesto</a>
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

    cta_url = f"https://hogarex.ar/solicitud-enviar?rubro={quote(oficio)}&ubicacion={quote(ubicacion)}"

    return HUB_CARD_TEMPLATE.format(
        avatar_html=avatar_html,
        badge_html=badge_html,
        url=url,
        name_esc=html.escape(name),
        oficio_esc=html.escape(oficio),
        ubicacion_esc=html.escape(ubicacion),
        description_esc=html.escape(description),
        cta_url=cta_url,
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
    print(f"Paginas generadas: {len(urls)}")
    print(f"Sitemap escrito en: {SITEMAP_PATH}")


if __name__ == "__main__":
    main()
