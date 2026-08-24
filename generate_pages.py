# -*- coding: utf-8 -*-
"""
Genera una página estática por cada nota de blog/posts.json en blog/<slug>/index.html,
con meta tags, Open Graph, canonical y JSON-LD (Article + FAQPage) propios.
También regenera sitemap.xml incluyendo las landing pages existentes + una URL por nota.

Uso: python3 generate_pages.py   (ejecutar desde la raíz del repo)
"""
import base64
import json
import os
import re
import html
import unicodedata

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_PATH = os.path.join(REPO_ROOT, "blog", "posts.json")
BLOG_DIR = os.path.join(REPO_ROOT, "blog")
SITEMAP_PATH = os.path.join(REPO_ROOT, "sitemap.xml")
LOGO_PATH = os.path.join(REPO_ROOT, "blog", "assets", "logo-white.png")
SITE_ORIGIN = "https://landing.hogarex.ar"


def load_logo_data_uri():
    with open(LOGO_PATH, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"

MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
}

STATIC_PAGES = [
    ("/electricistas", "monthly", "1.0"),
    ("/plomeros", "monthly", "1.0"),
    ("/gasistas", "monthly", "1.0"),
    ("/pintores", "monthly", "1.0"),
    ("/carpinteros", "monthly", "1.0"),
    ("/instalaciones", "monthly", "1.0"),
    ("/blog", "daily", "0.9"),
]


def slugify(title, maxlen=70):
    t = title.lower()
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^a-z0-9]+", "-", t)
    t = re.sub(r"-+", "-", t).strip("-")
    if len(t) > maxlen:
        t = t[:maxlen]
        if "-" in t:
            t = t.rsplit("-", 1)[0]
    return t


def ensure_slugs(posts):
    """Asigna slug a los posts que no lo tengan todavía, sin tocar los existentes.
    Devuelve True si hubo que guardar posts.json (se agregaron slugs nuevos)."""
    seen = {p["slug"] for p in posts if p.get("slug")}
    changed = False
    for p in posts:
        if p.get("slug"):
            continue
        base = slugify(p["title"])
        slug = base
        i = 2
        while slug in seen:
            slug = f"{base}-{i}"
            i += 1
        seen.add(slug)
        p["slug"] = slug
        changed = True
    if changed:
        with open(POSTS_PATH, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
    return changed


def parse_date_to_iso(date_str):
    """'Agosto 2026' -> '2026-08-01'. Fallback a 2026-01-01 si no matchea."""
    m = re.match(r"([A-Za-zÁÉÍÓÚñÑ]+)\s+(\d{4})", date_str.strip())
    if not m:
        return "2026-01-01"
    mes, anio = m.group(1).lower(), m.group(2)
    return f"{anio}-{MESES.get(mes, '01')}-01"


def extract_faq_pairs(content_html):
    """Extrae pares <h2>¿Pregunta?</h2><p>Respuesta</p> del HTML de la nota."""
    pairs = re.findall(r"<h2>(¿[^<]*\?)</h2>\s*<p>(.*?)</p>", content_html, re.DOTALL)
    clean = []
    for q, a in pairs:
        a_text = re.sub(r"<[^>]+>", "", a).strip()
        a_text = html.unescape(a_text)
        q_text = html.unescape(q.strip())
        clean.append((q_text, a_text))
    return clean


def build_jsonld(post):
    iso_date = parse_date_to_iso(post["date"])
    url = f"{SITE_ORIGIN}/blog/{post['slug']}"
    graph = [
        {
            "@type": "WebSite",
            "@id": f"{SITE_ORIGIN}/#website",
            "url": "https://hogarex.ar",
            "name": "Hogarex",
            "inLanguage": "es-AR",
        },
        {
            "@type": "WebPage",
            "@id": f"{url}#webpage",
            "url": url,
            "name": f"{post['title']} | Hogarex",
            "inLanguage": "es-AR",
            "isPartOf": {"@id": f"{SITE_ORIGIN}/#website"},
            "breadcrumb": {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Inicio", "item": "https://hogarex.ar"},
                    {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE_ORIGIN}/blog"},
                    {"@type": "ListItem", "position": 3, "name": post["title"], "item": url},
                ],
            },
        },
        {
            "@type": "Article",
            "@id": f"{url}#article",
            "headline": post["title"],
            "description": post["excerpt"],
            "image": post["image"],
            "datePublished": iso_date,
            "dateModified": iso_date,
            "inLanguage": "es-AR",
            "author": {"@type": "Organization", "name": "Hogarex", "url": "https://hogarex.ar"},
            "publisher": {"@type": "Organization", "name": "Hogarex", "url": "https://hogarex.ar"},
            "mainEntityOfPage": {"@id": f"{url}#webpage"},
            "articleSection": post["tag"],
        },
    ]

    faq_pairs = extract_faq_pairs(post["content"])
    if faq_pairs:
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
                for q, a in faq_pairs
            ],
        })

    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="es-AR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title_esc} | Hogarex</title>
  <meta name="description" content="{excerpt_esc}" />
  <link rel="canonical" href="{url}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{title_esc} | Hogarex" />
  <meta property="og:description" content="{excerpt_esc}" />
  <meta property="og:image" content="{image}" />
  <meta property="og:locale" content="es_AR" />
  <meta property="og:site_name" content="Hogarex" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title_esc} | Hogarex" />
  <meta name="twitter:description" content="{excerpt_esc}" />
  <meta name="twitter:image" content="{image}" />
  <script type="application/ld+json">
{jsonld}
  </script>
  <style>
    :root {{
      --navy:    #003366;
      --navy-dark: #091e44;
      --yellow:  #F5C518;
      --yellow-hover: #e0b200;
      --white:   #ffffff;
      --gray-50: #f8f9fb;
      --gray-100:#f0f2f5;
      --gray-300:#d1d5db;
      --gray-500:#6b7280;
      --gray-700:#374151;
      --text:    #1a1a2e;
      --radius:  12px;
      --shadow:  0 2px 16px rgba(13,42,94,0.10);
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Inter', sans-serif; background: var(--gray-50); color: var(--text); min-height: 100vh; }}
    header {{ background: var(--navy); padding: 0 24px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.18); }}
    .header-inner {{ max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 64px; }}
    .logo {{ display: flex; align-items: center; text-decoration: none; }}
    .logo img {{ height: 32px; width: auto; display: block; }}
    nav a {{ color: rgba(255,255,255,0.75); text-decoration: none; font-size: 0.9rem; font-weight: 500; margin-left: 24px; transition: color 0.2s; }}
    nav a:hover, nav a.active {{ color: var(--yellow); }}
    .breadcrumb {{ max-width: 740px; margin: 0 auto; padding: 20px 24px 0; }}
    .breadcrumb a {{ color: var(--gray-500); text-decoration: none; font-size: 0.85rem; font-weight: 500; }}
    .breadcrumb a:hover {{ color: var(--navy); }}
    .article-hero {{ max-width: 740px; margin: 0 auto; padding: 16px 24px 8px; }}
    .article-tag {{ display: inline-block; background: var(--yellow); color: var(--navy); font-size: 0.72rem; font-weight: 700; padding: 3px 12px; border-radius: 999px; margin-bottom: 14px; }}
    .article-hero h1 {{ font-family: 'Sora', sans-serif; font-size: clamp(1.4rem, 3.2vw, 1.9rem); font-weight: 700; color: var(--navy); line-height: 1.3; margin-bottom: 14px; }}
    .article-meta {{ display: flex; gap: 16px; flex-wrap: wrap; font-size: 0.85rem; color: var(--gray-500); margin-bottom: 20px; }}
    .article-thumb {{ max-width: 740px; margin: 0 auto; padding: 0 24px; }}
    .article-thumb img {{ width: 100%; max-height: 380px; object-fit: cover; border-radius: var(--radius); box-shadow: var(--shadow); }}
    .article-content {{ max-width: 740px; margin: 0 auto; padding: 28px 24px 12px; }}
    .article-content h2 {{ font-family: 'Sora', sans-serif; font-size: 1.15rem; color: var(--navy); margin: 24px 0 10px; }}
    .article-content p {{ font-size: 0.98rem; line-height: 1.75; color: var(--gray-700); margin-bottom: 14px; }}
    .article-content ul {{ margin: 10px 0 16px 20px; }}
    .article-content li {{ font-size: 0.95rem; line-height: 1.7; color: var(--gray-700); margin-bottom: 6px; }}
    .modal-cta {{ margin-top: 20px; padding: 20px 24px; background: var(--white); box-shadow: var(--shadow); border-radius: var(--radius); display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }}
    .modal-cta p {{ font-family: 'Sora', sans-serif; font-weight: 600; font-size: 0.95rem; color: var(--navy); margin: 0; }}
    .btn-yellow {{ background: var(--yellow); color: var(--navy); font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.9rem; padding: 12px 24px; border-radius: 999px; text-decoration: none; border: none; cursor: pointer; transition: background 0.2s, transform 0.15s; white-space: nowrap; display: inline-block; }}
    .btn-yellow:hover {{ background: var(--yellow-hover); transform: scale(1.03); }}
    .back-link {{ max-width: 740px; margin: 8px auto 48px; padding: 0 24px; }}
    .back-link a {{ color: var(--navy); text-decoration: none; font-weight: 600; font-size: 0.9rem; }}
    .back-link a:hover {{ color: var(--yellow-hover); }}
    footer {{ background: var(--navy-dark); color: rgba(255,255,255,0.5); text-align: center; padding: 28px 24px; font-size: 0.82rem; }}
    footer a {{ color: var(--yellow); text-decoration: none; }}
    @media (max-width: 600px) {{
      nav {{ display: none; }}
    }}
  </style>
  <script>
    window.va = window.va || function () {{ (window.vaq = window.vaq || []).push(arguments); }};
  </script>
  <script defer src="/_vercel/insights/script.js"></script>
</head>
<body>

<header>
  <div class="header-inner">
    <a href="https://hogarex.ar" class="logo"><img src="{logo_data_uri}" alt="Hogarex" /></a>
    <nav>
      <a href="https://hogarex.ar">Inicio</a>
      <a href="https://landing.hogarex.ar/blog" class="active">Blog</a>
      <a href="https://hogarex.ar" style="background:var(--yellow);color:var(--navy);padding:8px 18px;border-radius:999px;font-weight:700;font-family:'Sora',sans-serif;margin-left:16px;">Solicitar profesional</a>
    </nav>
  </div>
</header>

<div class="breadcrumb"><a href="/blog/">← Volver al blog</a></div>

<div class="article-hero">
  <span class="article-tag">{tag_esc}</span>
  <h1>{title_esc}</h1>
  <div class="article-meta"><span>📅 {date_esc}</span><span>⏱ {readtime_esc} de lectura</span></div>
</div>

<div class="article-thumb">
  <img src="{image}" alt="{tag_esc}" />
</div>

<main class="article-content">
{content}
</main>

<p class="back-link"><a href="/blog/">← Volver al blog</a></p>

<footer>
  <p>© 2026 <a href="https://hogarex.ar">Hogarex</a> — Conectamos profesionales del hogar con clientes en Argentina.</p>
</footer>

</body>
</html>
"""


def render_page(post, logo_data_uri):
    url = f"{SITE_ORIGIN}/blog/{post['slug']}"
    return PAGE_TEMPLATE.format(
        title_esc=html.escape(post["title"]),
        excerpt_esc=html.escape(post["excerpt"]),
        tag_esc=html.escape(post["tag"]),
        date_esc=html.escape(post["date"]),
        readtime_esc=html.escape(post["readTime"]),
        url=url,
        image=post["image"],
        jsonld=build_jsonld(post),
        content=post["content"],
        logo_data_uri=logo_data_uri,
    )


def generate_pages(posts):
    logo_data_uri = load_logo_data_uri()
    created = 0
    for post in posts:
        slug = post["slug"]
        page_dir = os.path.join(BLOG_DIR, slug)
        os.makedirs(page_dir, exist_ok=True)
        page_path = os.path.join(page_dir, "index.html")
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(render_page(post, logo_data_uri))
        created += 1
    return created


def generate_sitemap(posts):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', ""]

    for path, freq, prio in STATIC_PAGES:
        lines.append("  <url>")
        lines.append(f"    <loc>{SITE_ORIGIN}{path}</loc>")
        lines.append("    <lastmod>2026-08-24</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{prio}</priority>")
        lines.append("  </url>")
        lines.append("")

    for post in posts:
        lastmod = parse_date_to_iso(post["date"])
        lines.append("  <url>")
        lines.append(f"    <loc>{SITE_ORIGIN}/blog/{post['slug']}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("    <priority>0.7</priority>")
        lines.append("  </url>")
        lines.append("")

    lines.append("</urlset>")
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    with open(POSTS_PATH, encoding="utf-8") as f:
        posts = json.load(f)

    if ensure_slugs(posts):
        print("Se generaron slugs nuevos para posts sin slug y se guardó posts.json")

    created = generate_pages(posts)
    generate_sitemap(posts)
    print(f"Páginas generadas/actualizadas: {created}")
    print(f"Sitemap regenerado con {len(STATIC_PAGES) + len(posts)} URLs")


if __name__ == "__main__":
    main()
