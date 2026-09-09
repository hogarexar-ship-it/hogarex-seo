# -*- coding: utf-8 -*-
"""
Genera las páginas de autenticación nativa (login/registro) de Hogarex, como
primer paso de la migración de la gestión de cuentas desde Bubble hacia este
sitio. Por ahora son SOLO FRONTEND: los formularios validan en el navegador
y muestran un estado de éxito simulado al enviar, pero no persisten datos en
ningún lado (eso se conecta en un paso futuro, cuando haya una base de datos
propia o una integración con la API de Bubble desde acá).

A propósito NO están linkeadas desde ningún lado del sitio (nav, footer,
sitemap.xml) ni indexadas (noindex, nofollow): son páginas de trabajo en
progreso, pensadas para revisarse solo por URL directa mientras se define
el diseño final, antes de integrarlas al resto del sitio.

Estructura:
  /cuenta/cliente/ingresar/       - login de clientes
  /cuenta/cliente/registro/       - registro de clientes
  /cuenta/profesional/ingresar/   - login de profesionales
  /cuenta/profesional/registro/   - registro de profesionales
"""
import os

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_ORIGIN = "https://app.hogarex.ar"

BASE_CSS = """
    :root {
      --navy: #003366; --navy-dark: #091e44; --blue: #206ff7; --blue-bg: #eaf1ff;
      --yellow: #F5C518; --yellow-hover: #e0b200;
      --white: #ffffff; --gray-50: #f8f9fb; --gray-100: #f0f2f5; --gray-200: #e5e9f0;
      --gray-500: #6b7280; --gray-700: #374151; --text: #1a1a2e; --radius: 14px;
      --green: #1a7a3c; --green-bg: #e6f4ea; --red: #c02626; --red-bg: #fdecec;
      --shadow: 0 2px 16px rgba(13,42,94,0.10);
      --shadow-lg: 0 12px 40px rgba(13,42,94,0.16);
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
    body { font-family: 'Inter', -apple-system, sans-serif; background: var(--gray-50); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; }
    header { background: var(--navy); padding: 0 16px; }
    .header-inner { max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: center; height: 56px; }
    .logo { display: flex; align-items: center; text-decoration: none; }
    .logo img { height: 26px; width: auto; display: block; }
    @media (min-width: 640px) { header { padding: 0 24px; } .header-inner { height: 64px; } .logo img { height: 30px; } }

    main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 32px 16px 48px; }
    .auth-card { width: 100%; max-width: 440px; background: var(--white); border-radius: 20px; box-shadow: var(--shadow-lg); padding: 32px 24px; }
    @media (min-width: 480px) { .auth-card { padding: 40px 36px; } }

    .auth-badge { display: inline-flex; align-items: center; gap: 6px; font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.72rem; text-transform: uppercase; letter-spacing: .04em; padding: 5px 12px; border-radius: 999px; margin-bottom: 16px; }
    .auth-badge.role-cliente { background: var(--blue-bg); color: var(--blue); }
    .auth-badge.role-profesional { background: #fff4d6; color: #8a6a00; }

    .auth-card h1 { font-family: 'Sora', sans-serif; font-size: 1.45rem; font-weight: 800; color: var(--navy); line-height: 1.3; margin-bottom: 8px; }
    .auth-card p.auth-sub { font-size: 0.92rem; color: var(--gray-700); line-height: 1.55; margin-bottom: 26px; }

    .field { margin-bottom: 16px; }
    .field label { display: block; font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.84rem; color: var(--navy); margin-bottom: 6px; }
    .field-row { display: grid; grid-template-columns: 1fr; gap: 16px; }
    @media (min-width: 480px) { .field-row.two-col { grid-template-columns: 1fr 1fr; } }
    input[type=text], input[type=email], input[type=tel], input[type=password], select {
      width: 100%; border: 1.5px solid var(--gray-200); border-radius: 10px; padding: 13px 14px; font-size: 16px;
      font-family: inherit; color: var(--text); background: var(--white); appearance: none;
    }
    input:focus, select:focus { outline: none; border-color: var(--blue); }
    input:invalid:not(:placeholder-shown) { border-color: var(--red); }
    select { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 14px center; background-size: 18px; padding-right: 40px; }
    .field-hint { font-size: 0.76rem; color: var(--gray-500); margin-top: 5px; }
    .field-error { font-size: 0.78rem; color: var(--red); margin-top: 5px; display: none; }
    .field.has-error .field-error { display: block; }
    .field.has-error input { border-color: var(--red); }

    .pw-wrap { position: relative; }
    .pw-wrap input { padding-right: 46px; }
    .pw-toggle { position: absolute; right: 4px; top: 4px; bottom: 4px; width: 38px; background: none; border: none; cursor: pointer; color: var(--gray-500); display: flex; align-items: center; justify-content: center; }
    .pw-toggle:hover { color: var(--navy); }

    .check-row { display: flex; align-items: flex-start; gap: 9px; margin-bottom: 20px; }
    .check-row input[type=checkbox] { margin-top: 3px; width: 16px; height: 16px; accent-color: var(--blue); flex-shrink: 0; }
    .check-row label { font-size: 0.82rem; color: var(--gray-700); line-height: 1.5; }
    .check-row a { color: var(--blue); text-decoration: none; }
    .check-row a:hover { text-decoration: underline; }

    .between-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; font-size: 0.82rem; }
    .between-row label { display: flex; align-items: center; gap: 7px; color: var(--gray-700); }
    .between-row input[type=checkbox] { width: 15px; height: 15px; accent-color: var(--blue); }
    .between-row a { color: var(--blue); text-decoration: none; font-weight: 600; }
    .between-row a:hover { text-decoration: underline; }

    .btn-submit { width: 100%; background: var(--yellow); color: var(--navy); font-family: 'Sora', sans-serif; font-weight: 800; font-size: 0.98rem; padding: 15px; border-radius: 999px; border: none; cursor: pointer; transition: background .15s ease, transform .15s ease; }
    .btn-submit:hover { background: var(--yellow-hover); transform: translateY(-1px); }

    .auth-footer { margin-top: 22px; text-align: center; font-size: 0.86rem; color: var(--gray-700); }
    .auth-footer a { color: var(--blue); font-weight: 700; text-decoration: none; }
    .auth-footer a:hover { text-decoration: underline; }
    .role-switch { margin-top: 14px; text-align: center; font-size: 0.8rem; }
    .role-switch a { color: var(--gray-500); text-decoration: none; }
    .role-switch a:hover { color: var(--navy); text-decoration: underline; }

    .auth-success { display: none; text-align: center; padding: 8px 0; }
    .auth-success.show { display: block; }
    .auth-success-icon { width: 56px; height: 56px; border-radius: 50%; background: var(--green-bg); color: var(--green); display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
    .auth-success h2 { font-family: 'Sora', sans-serif; font-size: 1.2rem; color: var(--navy); margin-bottom: 8px; }
    .auth-success p { font-size: 0.9rem; color: var(--gray-700); line-height: 1.55; margin-bottom: 6px; }
    .auth-success .demo-note { margin-top: 16px; padding: 12px 14px; background: var(--gray-50); border-radius: 10px; font-size: 0.78rem; color: var(--gray-500); text-align: left; }
    #authForm.hide { display: none; }

    .wip-banner { background: #fff4d6; color: #8a6a00; text-align: center; font-size: 0.78rem; font-weight: 600; padding: 8px 16px; }
"""

WIP_BANNER = (
    '<div class="wip-banner">🚧 Página en construcción — todavía no está conectada '
    "a ninguna base de datos, es solo una vista previa del diseño.</div>"
)

HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="es-AR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title_esc} | Hogarex</title>
  <meta name="robots" content="noindex, nofollow" />
  <link rel="canonical" href="{url}" />
  <meta name="theme-color" content="#003366" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>{css}</style>
</head>
<body>
{wip_banner}
<header>
  <div class="header-inner">
    <a href="https://hogarex.ar" class="logo"><img src="/blog/assets/logo-white.png" alt="Hogarex" /></a>
  </div>
</header>
<main>
  <div class="auth-card">
    <span class="auth-badge role-{role}">{badge_label}</span>
    <h1>{h1}</h1>
    <p class="auth-sub">{sub}</p>

    <form id="authForm" novalidate>
{fields_html}
      <button type="submit" class="btn-submit">{submit_label}</button>
    </form>

    <div class="auth-success" id="authSuccess">
      <div class="auth-success-icon">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="m9 12 2 2 4-4"/></svg>
      </div>
      <h2>{success_title}</h2>
      <p>{success_body}</p>
      <div class="demo-note">Esto es una demo de front end: el formulario validó correctamente, pero todavía no se conecta a ninguna base de datos ni crea una cuenta real. Eso se integra en el próximo paso de la migración.</div>
    </div>

    <div class="auth-footer">{footer_html}</div>
    <div class="role-switch">{role_switch_html}</div>
  </div>
</main>
<script>
(function () {{
  var form = document.getElementById('authForm');
  var success = document.getElementById('authSuccess');

  document.querySelectorAll('.pw-toggle').forEach(function (btn) {{
    btn.addEventListener('click', function () {{
      var input = document.getElementById(btn.getAttribute('data-target'));
      var showing = input.type === 'text';
      input.type = showing ? 'password' : 'text';
      btn.setAttribute('aria-label', showing ? 'Mostrar contraseña' : 'Ocultar contraseña');
    }});
  }});

  function clearError(field) {{ field.classList.remove('has-error'); }}
  function setError(field) {{ field.classList.add('has-error'); }}

  form.addEventListener('submit', function (e) {{
    e.preventDefault();
    var ok = form.checkValidity();
    if (!ok) {{ form.reportValidity(); return; }}

    var pw = document.getElementById('password');
    var pw2 = document.getElementById('password2');
    if (pw && pw2) {{
      var field2 = pw2.closest('.field');
      if (pw.value !== pw2.value) {{
        setError(field2);
        pw2.focus();
        return;
      }}
      clearError(field2);
    }}

    form.classList.add('hide');
    success.classList.add('show');
  }});
}})();
</script>
</body>
</html>
"""


def field_text(id_, label, type_="text", placeholder="", required=True, autocomplete=None, hint=None, pattern=None, minlength=None):
    attrs = f'id="{id_}" name="{id_}" type="{type_}" placeholder="{placeholder}"'
    if required:
        attrs += " required"
    if autocomplete:
        attrs += f' autocomplete="{autocomplete}"'
    if pattern:
        attrs += f' pattern="{pattern}"'
    if minlength:
        attrs += f' minlength="{minlength}"'
    hint_html = f'<p class="field-hint">{hint}</p>' if hint else ""
    return f"""      <div class="field">
        <label for="{id_}">{label}</label>
        <input {attrs} />
        {hint_html}
      </div>"""


def field_password(id_, label, placeholder="Mínimo 8 caracteres", autocomplete="new-password", error=None):
    error_html = f'<p class="field-error">{error}</p>' if error else ""
    return f"""      <div class="field">
        <label for="{id_}">{label}</label>
        <div class="pw-wrap">
          <input id="{id_}" name="{id_}" type="password" placeholder="{placeholder}" required minlength="8" autocomplete="{autocomplete}" />
          <button type="button" class="pw-toggle" data-target="{id_}" aria-label="Mostrar contraseña">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8Z"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
        </div>
        {error_html}
      </div>"""


def field_select(id_, label, options, required=True):
    opts = '<option value="" disabled selected>Elegí una opción</option>'
    for value, text in options:
        opts += f'<option value="{value}">{text}</option>'
    req = " required" if required else ""
    return f"""      <div class="field">
        <label for="{id_}">{label}</label>
        <select id="{id_}" name="{id_}"{req}>{opts}</select>
      </div>"""


UBICACIONES = [
    ("Buenos Aires (CABA)", "Buenos Aires (CABA)"),
    ("Buenos Aires (GBA)", "Buenos Aires (GBA)"),
    ("Córdoba Capital", "Córdoba Capital"),
]

RUBROS = [
    ("Electricista", "Electricista"), ("Gasista", "Gasista"), ("Plomero", "Plomero"),
    ("Pintor", "Pintor"), ("Carpintero", "Carpintero"), ("Albañil", "Albañil"),
    ("Herrero", "Herrero"), ("Jardinero", "Jardinero"), ("Instalaciones", "Instalaciones"),
    ("Cerrajero", "Cerrajero"), ("Limpieza", "Limpieza"), ("Mudanzas", "Mudanzas"),
]


def render_page(path, title, role, badge_label, h1, sub, fields_html, submit_label,
                 success_title, success_body, footer_html, role_switch_html):
    url = f"{SITE_ORIGIN}/{path}"
    html_out = HEAD_TEMPLATE.format(
        title_esc=title,
        url=url,
        css=BASE_CSS,
        wip_banner=WIP_BANNER,
        role=role,
        badge_label=badge_label,
        h1=h1,
        sub=sub,
        fields_html=fields_html,
        submit_label=submit_label,
        success_title=success_title,
        success_body=success_body,
        footer_html=footer_html,
        role_switch_html=role_switch_html,
    )
    page_dir = os.path.join(REPO_ROOT, path)
    os.makedirs(page_dir, exist_ok=True)
    with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Generado: /{path}")


def main():
    # 1. Cliente - Ingresar
    fields = "\n".join([
        field_text("email", "Email", type_="email", placeholder="tu@email.com", autocomplete="email"),
        field_password("password", "Contraseña", placeholder="Tu contraseña", autocomplete="current-password"),
    ])
    fields += """
      <div class="between-row">
        <label><input type="checkbox" name="recordarme" /> Recordarme</label>
        <a href="#">¿Olvidaste tu contraseña?</a>
      </div>"""
    render_page(
        "cuenta/cliente/ingresar",
        "Ingresá a tu cuenta",
        "cliente", "Cliente",
        "Ingresá a tu cuenta",
        "Accedé para ver tus solicitudes y hablar con los profesionales que te contactaron.",
        fields,
        "Ingresar",
        "¡Listo!",
        "Si esto fuera real, ya habrías ingresado a tu cuenta de Hogarex.",
        '¿No tenés cuenta? <a href="/cuenta/cliente/registro/">Registrate gratis</a>',
        '¿Sos profesional? <a href="/cuenta/profesional/ingresar/">Ingresá acá</a>',
    )

    # 2. Cliente - Registro
    fields = "\n".join([
        field_text("nombre", "Nombre completo", placeholder="Nombre y apellido", autocomplete="name"),
        field_text("email", "Email", type_="email", placeholder="tu@email.com", autocomplete="email"),
        field_text("telefono", "WhatsApp", type_="tel", placeholder="11 1234 5678", autocomplete="tel"),
        field_password("password", "Contraseña", autocomplete="new-password"),
        field_password("password2", "Confirmar contraseña", placeholder="Repetí tu contraseña", autocomplete="new-password",
                        error="Las contraseñas no coinciden."),
    ])
    fields += """
      <div class="check-row">
        <input type="checkbox" id="terminos" name="terminos" required />
        <label for="terminos">Acepto los <a href="https://hogarex.ar/terminos-condiciones" target="_blank" rel="noopener">Términos y Condiciones</a> y la Política de Privacidad de Hogarex.</label>
      </div>"""
    render_page(
        "cuenta/cliente/registro",
        "Creá tu cuenta gratis",
        "cliente", "Cliente",
        "Creá tu cuenta gratis",
        "Pedí presupuestos y encontrá profesionales verificados en minutos, sin costo.",
        fields,
        "Crear cuenta",
        "¡Cuenta creada!",
        "Si esto fuera real, ya podrías pedir presupuestos desde tu cuenta nueva.",
        '¿Ya tenés cuenta? <a href="/cuenta/cliente/ingresar/">Iniciá sesión</a>',
        '¿Sos profesional? <a href="/cuenta/profesional/registro/">Registrate acá</a>',
    )

    # 3. Profesional - Ingresar
    fields = "\n".join([
        field_text("email", "Email", type_="email", placeholder="tu@email.com", autocomplete="email"),
        field_password("password", "Contraseña", placeholder="Tu contraseña", autocomplete="current-password"),
    ])
    fields += """
      <div class="between-row">
        <label><input type="checkbox" name="recordarme" /> Recordarme</label>
        <a href="#">¿Olvidaste tu contraseña?</a>
      </div>"""
    render_page(
        "cuenta/profesional/ingresar",
        "Ingresá a tu cuenta de profesional",
        "profesional", "Profesional",
        "Ingresá a tu cuenta de profesional",
        "Accedé para ver las solicitudes que te llegaron y gestionar tu perfil.",
        fields,
        "Ingresar",
        "¡Listo!",
        "Si esto fuera real, ya habrías ingresado a tu panel de profesional.",
        '¿No tenés cuenta? <a href="/cuenta/profesional/registro/">Sumate como profesional</a>',
        '¿Buscás un profesional? <a href="/cuenta/cliente/ingresar/">Ingresá como cliente</a>',
    )

    # 4. Profesional - Registro
    fields = "\n".join([
        field_text("nombre", "Nombre completo", placeholder="Nombre y apellido", autocomplete="name"),
        field_text("email", "Email", type_="email", placeholder="tu@email.com", autocomplete="email"),
        field_text("telefono", "WhatsApp", type_="tel", placeholder="11 1234 5678", autocomplete="tel"),
    ])
    fields += '\n      <div class="field-row two-col">\n'
    fields += field_select("rubro", "Rubro principal", RUBROS) + "\n"
    fields += field_select("ubicacion", "Ubicación", UBICACIONES) + "\n"
    fields += "      </div>\n"
    fields += field_password("password", "Contraseña", autocomplete="new-password")
    fields += "\n" + field_password("password2", "Confirmar contraseña", placeholder="Repetí tu contraseña", autocomplete="new-password",
                                     error="Las contraseñas no coinciden.")
    fields += """
      <div class="check-row">
        <input type="checkbox" id="matricula" name="matricula" required />
        <label for="matricula">Declaro contar con la matrícula o habilitación correspondiente a mi rubro, si mi actividad lo requiere.</label>
      </div>
      <div class="check-row">
        <input type="checkbox" id="terminos" name="terminos" required />
        <label for="terminos">Acepto los <a href="https://hogarex.ar/terminos-condiciones" target="_blank" rel="noopener">Términos y Condiciones</a> y la Política de Privacidad de Hogarex.</label>
      </div>"""
    render_page(
        "cuenta/profesional/registro",
        "Sumate como profesional",
        "profesional", "Profesional",
        "Sumate como profesional",
        "Creá tu perfil y empezá a recibir solicitudes de presupuesto de clientes verificados en tu zona.",
        fields,
        "Crear mi perfil de profesional",
        "¡Perfil creado!",
        "Si esto fuera real, tu perfil ya estaría listo para empezar a recibir solicitudes.",
        '¿Ya tenés cuenta? <a href="/cuenta/profesional/ingresar/">Iniciá sesión</a>',
        '¿Buscás un profesional? <a href="/cuenta/cliente/registro/">Registrate como cliente</a>',
    )


if __name__ == "__main__":
    main()
