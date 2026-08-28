# Arquitectura SEO/GEO — app.hogarex.ar

Documento de referencia fija para el sitio estático `hogarex-seo`. Cualquier cambio futuro (páginas nuevas, barrios, rubros, secciones) debe seguir estas reglas para mantener consistencia y evitar contenido duplicado. Última actualización: ver historial de git de este archivo.

## 1. Jerarquía de URLs (definitiva)

```
/                                   Home general (todos los rubros, todo CABA)
/caba/                              Hub de ciudad, cross-rubro (todos los rubros en CABA)
/{rubro}/                           Hub de rubro (flagship, landing de conversión principal)
/{rubro}/caba/                      Hub de rubro + ciudad (directorio de barrios de ese rubro)
/{rubro}/caba/{barrio}/             Landing hiper-local (rubro + barrio específico)
/blog/                              Índice de artículos
/blog/{slug}/                       Artículo individual
```

Regla general: **cada segmento de la URL (cada "/" nuevo) debe resolver en una página real con contenido único**, nunca un 404 ni un link genérico a `hogarex.ar`. Antes de agregar un nuevo path, hay que crear su página correspondiente en este mismo commit.

Rubros activos: `electricistas`, `plomeros`, `gasistas`, `pintores`, `carpinteros`, `instalaciones`.

Barrios con página propia hoy (Fase 1 — piloto "Palermo y alrededores"): `palermo`, `belgrano`, `recoleta`, `villa-crespo`, `colegiales`, `almagro`.

Barrios listados en el grid de "todos los barrios" de cada hub pero **sin página propia todavía**: el resto de los 48 barrios de CABA (Caballito, Flores, Villa Urquiza, Boedo, Balvanera, San Telmo, Devoto, Villa del Parque, Barracas, Saavedra, Núñez, Coghlan, Villa Pueyrredón, Floresta, Mataderos, Liniers, La Boca, Pompeya, Parque Patricios, Monte Castro, y otros). Estos enlazan a `/{rubro}/caba/` (el hub de rubro+ciudad) en vez de a una página inexistente, para no generar 404 ni links externos rotos. Ver "Fase 2" más abajo.

## 2. Qué contenido va en cada nivel (para evitar contenido duplicado)

- **`/` (home):** overview de marca, todos los rubros, buscador general, prueba social genérica.
- **`/caba/`:** contenido a nivel ciudad. Explica por qué CABA, lista los 6 rubros con link a `/{rubro}/caba/`, menciona barrios destacados, FAQ genérica de "cómo funciona en CABA". No repite precios/tarifas de un rubro específico.
- **`/{rubro}/`:** landing de conversión principal del rubro (ya en CABA). Tiene: hero, servicios específicos con precios, cómo funciona, profesionales destacados, por qué elegir Hogarex, grid de todos los barrios, contenido SEO largo (precios 2026, certificaciones, consejos), FAQ, CTA final. Esta es la página con más profundidad de contenido por rubro — no se debe recortar para no perder ranking.
- **`/{rubro}/caba/`:** hub intermedio, más liviano que el hub principal. Su función es ser el **directorio** de barrios para ese rubro: intro corta y única (2-3 párrafos, ángulo distinto al hub principal — enfocado en cobertura geográfica, no en precios), grid con los barrios (con página propia primero, resto después), FAQ corta propia (2-3 preguntas sobre cobertura/zonas), y siempre linkea de vuelta al hub principal `/{rubro}/`. **No duplicar** el bloque de precios/tarifas ni el FAQ largo del hub principal.
- **`/{rubro}/caba/{barrio}/`:** solo cambia el header (title, meta description, canonical, og:*, JSON-LD, breadcrumb, H1, hero-sub, geo) respecto al hub del rubro. El resto del body es idéntico al hub (mismo patrón "header-only" ya usado). Esto es intencional y aceptable porque el header ya aporta suficiente señal geo única por página (patrón validado, no generar contenido extra acá salvo que se decida lo contrario a futuro).
- **`/blog/{slug}/`:** artículo SEO/GEO individual (ver reglas de contenido en la tarea programada "Hogarex daily blog posts": primera oración autocontenida y citable, ≥1 H2 en forma de pregunta, FAQ de 2 pares antes del CTA, tono neutral, cifras en pesos fechadas "en 2026", 180-300 palabras).

## 3. Fase 2 (pendiente, no incluida en este batch)

Construir páginas propias para los ~20 barrios restantes de CABA por rubro (≈120 páginas nuevas). Cuando se haga:
1. Usar el mismo patrón "header-only" que las 6 páginas piloto.
2. Actualizar el grid de "todos los barrios" en los 6 hubs y en `/{rubro}/caba/` para que cada barrio nuevo apunte a su página real (hoy apuntan a `/{rubro}/caba/`).
3. Sumar las URLs a `STATIC_PAGES` en `generate_pages.py` y regenerar `sitemap.xml`.
4. Sumar las columnas nuevas al directorio del footer (root `index.html` y los 42+ archivos existentes).

## 4. Convención de URLs de CTA (fijo, no cambiar sin actualizar este doc)

Hay tres tipos de acción posibles en cualquier botón/tarjeta del sitio. Cada uno tiene una URL de destino fija:

| Intención | URL destino | Cuándo usarla |
|---|---|---|
| Pedir presupuesto / "qué trabajo necesitás" | `https://hogarex.ar/solicitud-enviar?rubro={Rubro}&ubicacion={Ubicacion}` | Cualquier botón o tarjeta de tipo "Recibir presupuesto", "Pedir presupuesto", tarjetas de "trabajos populares", CTAs de profesionales individuales. |
| Buscar / navegar el directorio | `https://hogarex.ar/busqueda` | "Buscar Profesionales", "Ver todos", chips de "ver también otro rubro". |
| Registrarse como profesional | `https://hogarex.ar/registro_profesional` | Todo botón "Soy Profesional". |

Reglas para `{Rubro}` y `{Ubicacion}` en `solicitud-enviar`:
- `{Rubro}` usa el valor exacto que espera el formulario real de hogarex.ar: `Electricista`, `Plomero`, `Gasista`, `Pintor`, `Carpintero`, `Instalaciones` (capitalizado, singular, no el slug de la URL).
- `{Ubicacion}` usa `Buenos Aires (CABA)` para todo lo que sea CABA (hub, hub+ciudad, y barrio — el formulario real de hogarex.ar no tiene granularidad de barrio, solo provincia/ciudad amplia). No inventar valores de barrio en este parámetro.
- En el home (`/`) y en `/caba/`, donde no hay un rubro fijo, se deja `rubro=` vacío (el usuario lo define en el selector) salvo que el CTA esté asociado a una tarjeta con rubro específico (ej. tarjeta de "Trabajos populares" de Pintores → `rubro=Pintor`).
- Ambos parámetros van con `encodeURIComponent` cuando se arman por JS (buscador del hero), o ya urlencodeados si están hardcodeados en el HTML (`Buenos%20Aires%20%28CABA%29`).

## 5. Convenciones de diseño reutilizables

- **Carrusel de tarjetas (`.carousel-wrap` / `.car-track` / `.car-btn` + función JS `carScroll`):** patrón único ya definido en `index.html`. Se usa para cualquier fila de tarjetas (profesionales, trabajos, servicios, reviews) en vez de un grid que se apila en mobile. En mobile, **todas** las filas de tarjetas deben ser `overflow-x:auto` con `scroll-snap`, nunca apiladas verticalmente.
- **Sección "Elegí cómo contratar":** un solo flujo de 3 pasos (no un toggle con dos flujos compitiendo). Un solo CTA primario ("Recibir Presupuestos") + un link secundario discreto al directorio. Evitar más de un botón de peso visual similar en esta sección.
- **Sección "¿Por qué elegir Hogarex?":** carrusel vertical infinito (marquee CSS, sin JS pesado), 3 tarjetas visibles a la vez, pausa al hover.
- **Iconos:** SVG inline, nunca emoji, para cualquier ícono nuevo de UI (rubros, checks, etc.). Los emoji que ya existan en contenido editorial (blog) no se tocan.
- **Colores:** `--navy:#003467` `--blue:#206ff7` `--yellow:#ffcc00` `--blue-bg:#eff5ff` (fondo celeste reutilizable para separar secciones).

## 6. Checklist antes de agregar/cambiar algo

1. ¿La URL nueva tiene una página real con contenido único? Si no, crearla en el mismo commit.
2. ¿El contenido se solapa con el nivel de arriba o de abajo en la jerarquía? Si es muy similar, diferenciar el ángulo (ver sección 2).
3. ¿Los CTAs de la página nueva siguen la tabla de la sección 4?
4. ¿El diseño de tarjetas nuevas usa el patrón de carrusel en mobile?
5. ¿Hay que sumar la URL a `STATIC_PAGES` en `generate_pages.py` y correr la regeneración de `sitemap.xml`?
6. ¿Hay que sumarla al directorio del footer?
7. Actualizar este archivo si la convención cambia.
