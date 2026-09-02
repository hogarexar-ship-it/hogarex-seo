# -*- coding: utf-8 -*-
"""
Genera una pagina estatica por cada profesional publico (por ahora: Electricista,
scoring >= 30) consumiendo el endpoint get_traders_publicos de Bubble.

Ubicacion de cada pagina generada:
  - Electricista + ubicacion "Buenos Aires (CABA)" -> electricistas/<slug>/index.html
    (nested bajo el hub /electricistas para agrupacion tematica de SEO; URL final
    unica, sin contenido duplicado en /profesional/).
  - Cualquier otro caso (otros rubros u otras ubicaciones)
    -> profesional/<slug>/index.html

Tambien actualiza:
  - sitemap-profesionales.xml (URLs de todas las paginas generadas, sea cual sea
    su carpeta). No se mezcla con sitemap.xml, que sigue siendo del blog.
  - electricistas/index.html: reemplaza el carrusel de tarjetas "Profesionales
    Destacados" (marcadores TRADER_CARDS_START/END) con los electricistas reales
    de CABA, linkeando a su pagina /electricistas/<slug>/.

El endpoint de Bubble es un Workflow API y SOLO acepta POST (no GET).

Uso: python3 generate_trader_pages.py   (ejecutar desde la raiz del repo)

Variable de entorno opcional:
  TRADERS_API_URL  -> para apuntar a version-test en vez de Live, ej:
                       https://hogarex.ar/version-test/api/1.1/wf/get_traders_publicos
"""
import html
import json
import os
import urllib.request
from urllib.parse import quote

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PROFESIONAL_DIR = os.path.join(REPO_ROOT, "profesional")
ELECTRICISTAS_DIR = os.path.join(REPO_ROOT, "electricistas")
SITEMAP_PATH = os.path.join(REPO_ROOT, "sitemap-profesionales.xml")
HUB_PAGE_PATH = os.path.join(ELECTRICISTAS_DIR, "index.html")
HUB_CARDS_START = "<!-- TRADER_CARDS_START -->"
HUB_CARDS_END = "<!-- TRADER_CARDS_END -->"
SITE_ORIGIN = "https://app.hogarex.ar"
CABA_UBICACION = "Buenos Aires (CABA)"
API_URL = os.environ.get(
    "TRADERS_API_URL",
    "https://hogarex.ar/api/1.1/wf/get_traders_publicos",
)


def fetch_traders():
    req = urllib.request.Request(API_URL, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    return data.get("response", {}).get("traders", [])


def is_caba_electricista(trader):
    return trader.get("main_field") == "Electricista" and trader.get("ubicacion") == CABA_UBICACION


def target_for(trader):
    """Devuelve (carpeta_absoluta, url_publica) para un trader.

    Electricistas de CABA se anidan bajo /electricistas/<slug>/ (agrupacion
    tematica bajo el hub, URL canonica unica). El resto sigue en
    /profesional/<slug>/, como antes."""
    slug = trader["Slug"]
    if is_caba_electricista(trader):
        return os.path.join(ELECTRICISTAS_DIR, slug), f"{SITE_ORIGIN}/electricistas/{slug}"
    return os.path.join(PROFESIONAL_DIR, slug), f"{SITE_ORIGIN}/profesional/{slug}"


def sanitize_description(text):
    """TODO (pendiente, decision 2026-08-31): portar aca el mismo regex que ya
    bloquea telefonos en Bubble al guardar el perfil, para tapar numeros que se
    hayan colado en descripciones viejas (ej. pegados al final del texto, caso
    real encontrado: un trader con un numero de whatsapp pegado en la bio).
    Por ahora se publica tal cual viene de la base, sin sanitizar."""
    return text


def build_jsonld(trader, url, oficio_hub_url):
    name = trader.get("user_name") or "Profesional"
    oficio = trader.get("main_field") or ""
    ubicacion = trader.get("ubicacion") or ""
    zonas = trader.get("zonaCobertura") or []

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
        {
            "@type": "Person",
            "@id": f"{url}#person",
            "name": name,
            "jobTitle": oficio,
            "address": {"@type": "PostalAddress", "addressLocality": ubicacion, "addressCountry": "AR"},
            "areaServed": zonas if zonas else [ubicacion],
            "worksFor": {"@type": "Organization", "name": "Hogarex", "url": "https://hogarex.ar"},
            "mainEntityOfPage": {"@id": f"{url}#webpage"},
        },
    ]
    # Nota deliberada: NO se agrega aggregateRating aca. Google bloquea estrellas
    # para reviews auto-alojadas sobre Organization/LocalBusiness/Person propios
    # (politica "self-serving reviews", 2019, reforzada en 2026 - ver
    # claude/seo-reviews-estrellas-google-trustpilot.md). El camino real para
    # estrellas es GBP / Trustpilot / schema SoftwareApplication a nivel Hogarex,
    # no aca por-perfil.
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


# Template mobile-first: los estilos base (sin media query) son los de mobile;
# @media (min-width:640px) agrega/ajusta para tablet+desktop. La barra de CTA
# fija abajo es el patron mobile habitual para perfiles de servicios locales;
# en desktop se oculta a favor de la tarjeta de CTA normal en el flujo.
PAGE_TEMPLATE = """<!DOCTYPE html>
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
  <span class="profile-tag">{oficio_esc}</span>
  <h1>{name_esc} &mdash; {oficio_esc} en {ubicacion_esc}</h1>
  <div class="profile-meta">
    <span>&#128205; {ubicacion_esc}</span>
    {verified_html}
  </div>
</div>

<main class="profile-content">
  {zonas_html}
  <p>{description_esc}</p>
</main>

<div class="modal-cta">
  <p>&iquest;Necesit&aacute;s un {oficio_esc_lower} en {ubicacion_esc}?</p>
  <a href="{cta_url}" class="btn-yellow">Pedir presupuesto gratis</a>
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

OFICIO_HUB = {
    "Electricista": "/electricistas",
    "Gasista": "/gasistas",
    "Plomero": "/plomeros",
    "Pintor": "/pintores",
    "Carpintero": "/carpinteros",
}


def render_page(trader, url):
    name = trader.get("user_name") or "Profesional"
    oficio = trader.get("main_field") or ""
    ubicacion = trader.get("ubicacion") or ""
    description = sanitize_description(trader.get("description") or "")
    zonas = trader.get("zonaCobertura") or []
    verified = trader.get("verified") == "Si"
    oficio_hub_path = OFICIO_HUB.get(oficio, "/")
    oficio_hub_url = f"{SITE_ORIGIN}{oficio_hub_path}"

    zonas_html = ""
    if zonas:
        chips = "".join(f'<span class="zona-chip">{html.escape(z)}</span>' for z in zonas)
        zonas_html = f'<div class="zonas">{chips}</div>'

    verified_html = '<span class="verified-badge">&check; Perfil verificado</span>' if verified else ""

    meta_desc = f"{name}, {oficio} en {ubicacion}. Pedi presupuesto gratis en Hogarex, sin intermediarios."
    cta_url = f"https://hogarex.ar/solicitud-enviar?rubro={quote(oficio)}&ubicacion={quote(ubicacion)}"

    page_html = PAGE_TEMPLATE.format(
        title_esc=html.escape(f"{name} - {oficio} en {ubicacion}"),
        meta_desc_esc=html.escape(meta_desc),
        url=url,
        jsonld=build_jsonld(trader, url, oficio_hub_url),
        oficio_esc=html.escape(oficio),
        oficio_esc_lower=html.escape(oficio.lower()),
        oficio_hub_url=oficio_hub_url,
        name_esc=html.escape(name),
        ubicacion_esc=html.escape(ubicacion),
        verified_html=verified_html,
        zonas_html=zonas_html,
        description_esc=html.escape(description),
        cta_url=cta_url,
    )
    return page_html


def generate_pages(traders):
    urls = []
    skipped = 0
    for trader in traders:
        if not trader.get("Slug"):
            skipped += 1
            continue
        page_dir, url = target_for(trader)
        os.makedirs(page_dir, exist_ok=True)
        page_html = render_page(trader, url)
        with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(page_html)
        urls.append(url)
    if skipped:
        print(f"Aviso: {skipped} traders sin Slug fueron omitidos.")
    return urls


def generate_sitemap(urls):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', ""]
    for url in urls:
        lines += ["  <url>", f"    <loc>{url}</loc>", "    <changefreq>weekly</changefreq>",
                  "    <priority>0.75</priority>", "  </url>", ""]
    lines.append("</urlset>")
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


HUB_CARD_TEMPLATE = """      <div class="prof-card">
        <div class="prof-top"><div class="prof-av"{avatar_style}>{initials}</div>{badge_html}</div>
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
    name = trader.get("user_name") or "Profesional"
    oficio = trader.get("main_field") or ""
    ubicacion = trader.get("ubicacion") or ""
    description = sanitize_description(trader.get("description") or "")
    verified = trader.get("verified") == "Si"

    color = HUB_AVATAR_COLORS[index % len(HUB_AVATAR_COLORS)]
    avatar_style = f' style="background:{color}"' if color else ""

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
        avatar_style=avatar_style,
        initials=html.escape(get_initials(name)),
        badge_html=badge_html,
        url=url,
        name_esc=html.escape(name),
        oficio_esc=html.escape(oficio),
        ubicacion_esc=html.escape(ubicacion),
        description_esc=html.escape(description),
        cta_url=cta_url,
    )


def update_hub_page(traders):
    """Reemplaza el carrusel de 'Profesionales Destacados' en electricistas/index.html
    (marcadores TRADER_CARDS_START/END) con los electricistas reales de CABA
    (misma cobertura geografica que declara la pagina), linkeando a su propia
    pagina /electricistas/<slug>/. No toca el resto de la pagina."""
    if not os.path.exists(HUB_PAGE_PATH):
        print("Aviso: electricistas/index.html no encontrado, se omite actualizacion de tarjetas.")
        return

    with open(HUB_PAGE_PATH, encoding="utf-8") as f:
        page_html = f.read()

    start_idx = page_html.find(HUB_CARDS_START)
    end_idx = page_html.find(HUB_CARDS_END)
    if start_idx == -1 or end_idx == -1:
        print("Aviso: marcadores TRADER_CARDS_START/END no encontrados, se omite actualizacion de tarjetas.")
        return

    caba_electricistas = [t for t in traders if t.get("Slug") and is_caba_electricista(t)]
    cards_html = "".join(
        render_hub_card(t, i, target_for(t)[1]) for i, t in enumerate(caba_electricistas)
    )

    new_page_html = (
        page_html[: start_idx + len(HUB_CARDS_START)]
        + "\n"
        + cards_html
        + page_html[end_idx:]
    )
    with open(HUB_PAGE_PATH, "w", encoding="utf-8") as f:
        f.write(new_page_html)
    print(f"Tarjetas actualizadas en electricistas/index.html: {len(caba_electricistas)} profesionales de CABA")


def main():
    traders = fetch_traders()
    print(f"Traders recibidos del endpoint: {len(traders)}")
    caba_count = sum(1 for t in traders if is_caba_electricista(t) and t.get("Slug"))
    print(f"De los cuales electricistas de CABA (-> /electricistas/<slug>/): {caba_count}")
    urls = generate_pages(traders)
    generate_sitemap(urls)
    update_hub_page(traders)
    print(f"Paginas de profesional generadas: {len(urls)}")
    print(f"Sitemap escrito en: {SITEMAP_PATH}")


if __name__ == "__main__":
    main()
