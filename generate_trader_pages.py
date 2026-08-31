# -*- coding: utf-8 -*-
"""
Genera una pagina estatica por cada profesional publico (por ahora: Electricista,
scoring >= 30) en profesional/<slug>/index.html, consumiendo el endpoint
get_traders_publicos de Bubble. Genera tambien sitemap-profesionales.xml aparte
(no toca sitemap.xml, que sigue siendo responsabilidad de generate_pages.py / blog).

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

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PROFESIONAL_DIR = os.path.join(REPO_ROOT, "profesional")
SITEMAP_PATH = os.path.join(REPO_ROOT, "sitemap-profesionales.xml")
SITE_ORIGIN = "https://app.hogarex.ar"
API_URL = os.environ.get(
    "TRADERS_API_URL",
    "https://hogarex.ar/api/1.1/wf/get_traders_publicos",
)


def fetch_traders():
    req = urllib.request.Request(API_URL, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    return data.get("response", {}).get("traders", [])


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


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="es-AR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title_esc} | Hogarex</title>
  <meta name="description" content="{meta_desc_esc}" />
  <link rel="canonical" href="{url}" />
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
    body {{ font-family: 'Inter', sans-serif; background: var(--gray-50); color: var(--text); min-height: 100vh; }}
    header {{ background: var(--navy); padding: 0 24px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.18); }}
    .header-inner {{ max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 64px; }}
    .logo {{ color: var(--white); font-family: 'Sora', sans-serif; font-weight: 700; font-size: 1.1rem; text-decoration: none; }}
    nav a {{ color: rgba(255,255,255,0.75); text-decoration: none; font-size: 0.9rem; font-weight: 500; margin-left: 24px; }}
    .breadcrumb {{ max-width: 740px; margin: 0 auto; padding: 20px 24px 0; }}
    .breadcrumb a {{ color: var(--gray-500); text-decoration: none; font-size: 0.85rem; font-weight: 500; }}
    .profile-hero {{ max-width: 740px; margin: 0 auto; padding: 16px 24px 8px; }}
    .profile-tag {{ display: inline-block; background: var(--yellow); color: var(--navy); font-size: 0.72rem; font-weight: 700; padding: 3px 12px; border-radius: 999px; margin-bottom: 14px; }}
    .profile-hero h1 {{ font-family: 'Sora', sans-serif; font-size: clamp(1.3rem, 3.2vw, 1.8rem); font-weight: 700; color: var(--navy); line-height: 1.3; margin-bottom: 10px; }}
    .profile-meta {{ display: flex; gap: 16px; flex-wrap: wrap; align-items: center; font-size: 0.9rem; color: var(--gray-500); margin-bottom: 16px; }}
    .profile-content {{ max-width: 740px; margin: 0 auto; padding: 12px 24px; }}
    .profile-content p {{ font-size: 0.98rem; line-height: 1.75; color: var(--gray-700); margin-bottom: 14px; white-space: pre-line; }}
    .zonas {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }}
    .zona-chip {{ background: var(--gray-100); color: var(--gray-700); font-size: 0.8rem; padding: 4px 12px; border-radius: 999px; }}
    .verified-badge {{ display: inline-flex; align-items: center; gap: 4px; color: #1a7a3c; font-size: 0.85rem; font-weight: 600; }}
    .modal-cta {{ margin: 24px auto 20px; max-width: 692px; padding: 20px 24px; background: var(--white); box-shadow: var(--shadow); border-radius: var(--radius); display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }}
    .modal-cta p {{ font-family: 'Sora', sans-serif; font-weight: 600; font-size: 0.95rem; color: var(--navy); margin: 0; }}
    .btn-yellow {{ background: var(--yellow); color: var(--navy); font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.9rem; padding: 12px 24px; border-radius: 999px; text-decoration: none; border: none; cursor: pointer; white-space: nowrap; display: inline-block; }}
    .btn-yellow:hover {{ background: var(--yellow-hover); }}
    footer {{ background: var(--navy-dark); color: rgba(255,255,255,0.5); text-align: center; padding: 28px 24px; font-size: 0.82rem; margin-top: 24px; }}
    footer a {{ color: var(--yellow); text-decoration: none; }}
  </style>
</head>
<body>

<header>
  <div class="header-inner">
    <a href="https://hogarex.ar" class="logo">Hogarex</a>
    <nav>
      <a href="https://hogarex.ar">Inicio</a>
      <a href="https://hogarex.ar/solicitud-enviar" style="background:var(--yellow);color:var(--navy);padding:8px 18px;border-radius:999px;font-weight:700;font-family:'Sora',sans-serif;">Recibir presupuesto gratis</a>
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
  <a href="https://hogarex.ar/solicitud-enviar" class="btn-yellow">Pedir presupuesto gratis</a>
</div>

<footer>
  <p>&copy; 2026 <a href="https://hogarex.ar">Hogarex</a> &mdash; Conectamos profesionales del hogar con clientes en Argentina.</p>
</footer>

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


def render_page(trader):
    slug = trader["Slug"]
    url = f"{SITE_ORIGIN}/profesional/{slug}"
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
    )
    return url, page_html


def generate_pages(traders):
    os.makedirs(PROFESIONAL_DIR, exist_ok=True)
    urls = []
    skipped = 0
    for trader in traders:
        if not trader.get("Slug"):
            skipped += 1
            continue
        url, page_html = render_page(trader)
        page_dir = os.path.join(PROFESIONAL_DIR, trader["Slug"])
        os.makedirs(page_dir, exist_ok=True)
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


def main():
    traders = fetch_traders()
    print(f"Traders recibidos del endpoint: {len(traders)}")
    urls = generate_pages(traders)
    generate_sitemap(urls)
    print(f"Paginas de profesional generadas: {len(urls)}")
    print(f"Sitemap escrito en: {SITEMAP_PATH}")


if __name__ == "__main__":
    main()
