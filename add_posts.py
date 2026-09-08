import json

posts_path = "blog/posts.json"
with open(posts_path, encoding="utf-8") as f:
    posts = json.load(f)

max_id = max(p["id"] for p in posts)
next_id = max_id + 1

new_posts = []

def cta(rubro_label, rubro_param, ubicacion):
    ub = ubicacion.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
    href = f"https://hogarex.ar/solicitud-enviar?rubro={rubro_param}&ubicacion={ub}"
    return f"<div class='modal-cta'><p>¿Necesitás un {rubro_label} verificado en CABA?</p><a href='{href}' class='btn-yellow'>Enviar solicitud &rarr;</a></div>"

def add(cat, emoji, image, tag, title, excerpt, content, read_time="4 min", image_credit=None):
    global next_id
    post = {
        "id": next_id,
        "cat": cat,
        "emoji": emoji,
        "image": image,
        "tag": tag,
        "title": title,
        "excerpt": excerpt,
        "date": "Septiembre 2026",
        "readTime": read_time,
        "content": content
    }
    if image_credit:
        post["imageCredit"] = image_credit
    new_posts.append(post)
    next_id += 1

# 1. Retiro - gas - calefon tiro balanceado
add(
    "gas", "🔥",
    "https://blog2.edificor.com.ar/wp-content/uploads/2025/08/termo-calentador-caldera-1920w.webp",
    "Gas",
    "Instalar un calefón a gas de tiro balanceado en tu departamento de Retiro: cuánto cuesta en 2026",
    "Instalar un calefón a gas de tiro balanceado en un departamento de Retiro cuesta en 2026 entre $180.000 y $230.000, según el metraje del caño de venteo y si hay que adaptar la salida existente.",
    """<p>Instalar un calefón a gas de tiro balanceado en un departamento de Retiro cuesta en 2026 entre <strong>$180.000 y $230.000</strong>, según el metraje del caño de venteo y si hay que adaptar la salida existente en la pared.</p><h2>¿Por qué elegir tiro balanceado en un departamento?</h2><p>El tiro balanceado toma el aire de combustión del exterior y expulsa los gases quemados por el mismo caño, algo clave en departamentos de Retiro sin buena ventilación natural en el baño o la cocina.</p><h2>Qué incluye la instalación</h2><ul><li>✅ Fijación del calefón y conexión a la cañería de gas existente</li><li>✅ Caño de venteo balanceado hasta la fachada o el patio</li><li>✅ Prueba de hermeticidad y verificación de tiraje</li></ul><h2>¿Hace falta certificado de gasista matriculado?</h2><p>Sí, en CABA la instalación de un calefón debe hacerla un gasista matriculado, que además deja asentada la habilitación del artefacto en el trámite correspondiente.</p><h2>¿Cuánto dura el trabajo?</h2><p>En un departamento de Retiro sin obra adicional, la instalación completa del calefón suele resolverse en una sola visita de tres a cinco horas.</p><h2>¿El precio incluye el calefón?</h2><p>No, el valor cotizado es solo la mano de obra: el calefón se compra aparte y su costo varía según la marca y la capacidad en litros por minuto.</p>""" + cta("gasista", "Gasista", "Buenos Aires (CABA)"),
    image_credit="Foto: Edificor"
)

# 2. Once - gas - deteccion de fuga
add(
    "gas", "🔥",
    "https://images.pexels.com/photos/8293635/pexels-photo-8293635.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Gas",
    "Detección de fuga de gas en tu casa de Once: cuánto cuesta la revisión y qué hacer mientras esperás al gasista",
    "La detección de una fuga de gas en una casa de Once cuesta en 2026 entre $100.000 y $140.000, e incluye la prueba manométrica de toda la instalación hasta encontrar el origen del escape.",
    """<p>La detección de una fuga de gas en una casa de Once cuesta en 2026 entre <strong>$100.000 y $140.000</strong>, e incluye la prueba manométrica de toda la instalación hasta encontrar el origen exacto del escape.</p><h2>¿Qué hacer apenas se siente olor a gas?</h2><p>Lo primero es cortar la llave de paso general, ventilar abriendo puertas y ventanas, y no accionar ningún interruptor de luz ni encender nada con llama mientras se ventila el ambiente.</p><h2>Qué incluye la revisión del gasista</h2><ul><li>✅ Prueba manométrica de presión en toda la cañería</li><li>✅ Revisión de conexiones y artefactos uno por uno</li><li>✅ Detección de fugas con espuma o detector electrónico</li></ul><h2>¿Es urgente llamar a un gasista aunque sea de noche?</h2><p>Sí, una fuga de gas es una urgencia real en cualquier casa de Once: mientras se resuelve, conviene mantener la llave de paso cerrada y no volver a abrirla hasta confirmar que no hay pérdidas.</p><h2>¿Cómo se soluciona una vez detectada la fuga?</h2><p>Depende de dónde esté: puede ser un cambio de junta, un tramo de cañería dañado o una conexión floja, y el gasista cotiza esa reparación aparte una vez identificado el punto exacto.</p><h2>¿La revisión incluye certificado?</h2><p>Se puede pedir un informe de conformidad una vez resuelta la fuga, útil para tener un respaldo de que la instalación quedó en condiciones seguras.</p>""" + cta("gasista", "Gasista", "Buenos Aires (CABA)")
)

# 3. Constitucion - albanileria - porcelanato
add(
    "albanileria", "🧱",
    "https://images.pexels.com/photos/5179534/pexels-photo-5179534.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Albañilería",
    "Colocar porcelanato en el piso de tu departamento en Constitución: cuánto cuesta un albañil en 2026",
    "Colocar porcelanato en el piso de un departamento en Constitución cuesta en 2026 entre $21.000 y $28.000 por m², sin contar el valor de las piezas ni el material de pegado.",
    """<p>Colocar porcelanato en el piso de un departamento en Constitución cuesta en 2026 entre <strong>$21.000 y $28.000 por m²</strong>, un valor que corresponde solo a la mano de obra, sin contar las piezas ni el material de pegado.</p><h2>¿Por qué el porcelanato cuesta más que la cerámica común?</h2><p>El porcelanato es más pesado y requiere una nivelación más precisa del contrapiso, además de un pegamento especial que soporte piezas grandes sin que se levanten con el tiempo.</p><h2>Qué incluye el trabajo del albañil</h2><ul><li>✅ Nivelación y preparación del contrapiso existente</li><li>✅ Colocación de las piezas con pegamento específico para porcelanato</li><li>✅ Colocación de juntas y limpieza final del piso</li></ul><h2>¿Hace falta sacar el piso viejo antes de colocar el porcelanato?</h2><p>En la mayoría de los departamentos de Constitución conviene retirar el piso anterior si es cerámico, aunque en algunos casos se puede colocar el porcelanato encima si la superficie está firme y nivelada.</p><h2>Cuánto dura la obra</h2><p>Un albañil suele colocar el porcelanato de un departamento de dos ambientes en Constitución en tres a cuatro días, incluyendo el tiempo de secado antes de pisar el piso nuevo.</p><h2>¿Conviene porcelanato rectificado o no rectificado?</h2><p>El rectificado tiene bordes más parejos y permite juntas más finas, con una terminación más prolija, aunque suele costar más que el no rectificado.</p>""" + cta("albañil", "Alba%C3%B1il", "Buenos Aires (CABA)")
)

# 4. Villa Lugano - albanileria - grietas y humedad
add(
    "albanileria", "🧱",
    "https://images.unsplash.com/photo-1503387762-592deb58ef4e?q=80&w=2070&auto=format&fit=crop",
    "Albañilería",
    "Reparar grietas y humedad en las paredes de tu casa de Villa Lugano: cuánto cuesta arreglarlo en 2026",
    "Reparar grietas y humedad en las paredes de una casa de Villa Lugano cuesta en 2026 entre $6.500 y $15.000 por m², según si la humedad es superficial o viene de una filtración más profunda.",
    """<p>Reparar grietas y humedad en las paredes de una casa de Villa Lugano cuesta en 2026 entre <strong>$6.500 y $15.000 por m²</strong>, según si la humedad es superficial o viene de una filtración más profunda que hay que resolver antes.</p><h2>¿Cómo saber si una grieta es solo estética o estructural?</h2><p>Una grieta fina y superficial que no crece con el tiempo suele ser cosmética, mientras que una grieta ancha, que atraviesa toda la pared o sigue una línea diagonal marcada, conviene que la revise un profesional antes de taparla.</p><h2>Qué incluye la reparación</h2><ul><li>✅ Apertura y sellado de la grieta con material elástico</li><li>✅ Tratamiento de la humedad si es la causa de fondo</li><li>✅ Enduido y terminación lista para pintar</li></ul><h2>¿Por qué vuelve a aparecer la misma grieta después de tapada?</h2><p>Si la causa de fondo no se resuelve, como una filtración de agua o un movimiento en la estructura, la grieta suele reaparecer en el mismo lugar aunque se haya tapado bien la primera vez.</p><h2>Cuánto dura el trabajo</h2><p>Una reparación puntual de grietas en una casa de Villa Lugano suele resolverse en uno o dos días, aunque si hay que tratar humedad de filtración el plazo se extiende según el secado de cada capa.</p><h2>¿Conviene pintar enseguida después de reparar la humedad?</h2><p>No, conviene esperar a que la pared esté completamente seca antes de pintar, para que la pintura no encierre humedad residual y la grieta vuelva a marcarse pronto.</p>""" + cta("albañil", "Alba%C3%B1il", "Buenos Aires (CABA)")
)

# 5. Puerto Madero - instalaciones - split aire acondicionado
add(
    "instalaciones", "🔧",
    "https://images.unsplash.com/photo-1601628828688-632f38a5a7d0?q=80&w=2070&auto=format&fit=crop",
    "Instalaciones",
    "Instalar un split de aire acondicionado en tu departamento de Puerto Madero: cuánto cuesta en 2026",
    "Instalar un split de aire acondicionado de 3.000 a 4.500 frigorías en un departamento de Puerto Madero cuesta en 2026 entre $130.000 y $200.000, sin contar el valor del equipo.",
    """<p>Instalar un split de aire acondicionado de 3.000 a 4.500 frigorías en un departamento de Puerto Madero cuesta en 2026 entre <strong>$130.000 y $200.000</strong>, un valor que corresponde solo a la mano de obra, sin contar el equipo.</p><h2>¿Por qué el precio varía tanto entre departamentos?</h2><p>El costo final depende de la distancia entre la unidad interior y la exterior, si hay que perforar mampostería y del piso donde está el departamento, ya que los edificios altos de Puerto Madero a veces requieren trabajo en altura con equipo de seguridad.</p><h2>Qué incluye la instalación</h2><ul><li>✅ Fijación de la unidad interior y exterior</li><li>✅ Cañerías de cobre y cableado eléctrico dedicado</li><li>✅ Vacío del sistema y carga de gas refrigerante inicial</li></ul><h2>¿Hace falta un punto eléctrico aparte para el split?</h2><p>Sí, en la mayoría de los departamentos de Puerto Madero conviene un circuito eléctrico dedicado con su propia protección térmica, sobre todo para equipos de mayor potencia.</p><h2>Cuánto dura la instalación</h2><p>Un instalador suele completar el montaje de un split estándar en cuatro a seis horas, siempre que no haga falta trabajo en altura o adaptaciones especiales en la fachada.</p><h2>¿El consorcio puede poner condiciones para instalar la unidad exterior?</h2><p>Sí, muchos edificios de Puerto Madero regulan dónde se puede ubicar la unidad exterior por una cuestión estética de fachada, algo que conviene chequear con la administración antes de instalar.</p>""" + cta("instalador", "Instalaciones", "Buenos Aires (CABA)")
)

# 6. Monte Castro - instalaciones - limpieza y mantenimiento AC
add(
    "instalaciones", "🔧",
    "https://images.pexels.com/photos/27134985/pexels-photo-27134985.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Instalaciones",
    "Limpieza y mantenimiento de aire acondicionado en tu casa de Monte Castro: cuánto cuesta y cada cuánto hacerlo",
    "La limpieza y el mantenimiento de un aire acondicionado en una casa de Monte Castro cuesta en 2026 entre $47.000 y $128.000, según si incluye carga de gas refrigerante o solo limpieza de filtros.",
    """<p>La limpieza y el mantenimiento de un aire acondicionado en una casa de Monte Castro cuesta en 2026 entre <strong>$47.000 y $128.000</strong>, según si el servicio incluye carga de gas refrigerante o es solo una limpieza de filtros y unidad.</p><h2>¿Cada cuánto conviene hacer el mantenimiento?</h2><p>Lo recomendable es una limpieza al año, idealmente antes del verano, para que el equipo enfríe bien y no fuerce el compresor por filtros o serpentinas sucias.</p><h2>Qué incluye el servicio de mantenimiento</h2><ul><li>✅ Limpieza de filtros y serpentina de la unidad interior</li><li>✅ Revisión del desagüe de condensado</li><li>✅ Chequeo de presión de gas refrigerante</li></ul><h2>¿Qué pasa si no se hace el mantenimiento?</h2><p>Un aire acondicionado sin mantenimiento en una casa de Monte Castro consume más energía para enfriar lo mismo, y con el tiempo puede perder eficiencia o largar olor a humedad por acumulación de suciedad.</p><h2>¿Cómo saber si hace falta cargar gas?</h2><p>Si el equipo tarda mucho en enfriar o hace ruido raro al arrancar, puede ser una señal de que el gas refrigerante bajó y conviene que lo revise un técnico antes de seguir usándolo así.</p><h2>Cuánto dura el servicio</h2><p>Una limpieza estándar de un split suele resolverse en una hora, mientras que si hace falta carga de gas o hay una falla puntual el trabajo se extiende según el diagnóstico.</p>""" + cta("instalador", "Instalaciones", "Buenos Aires (CABA)")
)

# 7. Velez Sarsfield - pintura - pintar el frente de la casa
add(
    "pintura", "🎨",
    "https://images.pexels.com/photos/34896778/pexels-photo-34896778.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Pintura",
    "Pintar el frente de tu casa en Vélez Sarsfield: cuánto cuesta y qué conviene saber antes de empezar",
    "Pintar el frente de una casa en Vélez Sarsfield cuesta en 2026 entre $5.600 y $11.500 por m², según la altura, el estado de la superficie y si hace falta trabajar con andamio.",
    """<p>Pintar el frente de una casa en Vélez Sarsfield cuesta en 2026 entre <strong>$5.600 y $11.500 por m²</strong>, según la altura del frente, el estado de la superficie y si hace falta trabajar con andamio o silleta.</p><h2>¿Por qué pintar un frente cuesta más que un ambiente interior?</h2><p>El trabajo en exterior requiere pintura resistente a la intemperie, más manos de protección y en muchos casos equipo de altura, además de estar sujeto al clima para poder avanzar sin lluvia.</p><h2>Qué incluye el trabajo de pintura de frente</h2><ul><li>✅ Lavado a presión e hidrolavado de la superficie</li><li>✅ Reparación de grietas o desprendimientos previos</li><li>✅ Aplicación de fijador y dos manos de pintura para exterior</li></ul><h2>¿Cuánto dura pintar el frente de una casa?</h2><p>En una casa de Vélez Sarsfield de un piso, el trabajo suele resolverse en tres a cinco días si el clima acompaña, y se extiende si hace falta reparar revoques antes de pintar.</p><h2>¿Hace falta permiso para pintar el frente de la casa?</h2><p>En general no, salvo que se trate de un edificio catalogado o esté dentro de una zona con normativa especial de fachadas, algo poco común en una vivienda unifamiliar estándar.</p><h2>¿Conviene pintura sintética o al agua para el frente?</h2><p>La pintura al agua para exterior es más transpirable y ayuda a que la pared no retenga humedad, mientras que la sintética da más cobertura pero conviene evaluarla según el estado del revoque.</p>""" + cta("pintor", "Pintor", "Buenos Aires (CABA)")
)

# 8. Parque Avellaneda - pintura - cielorraso con humedad
add(
    "pintura", "🎨",
    "https://images.unsplash.com/photo-1559322575-2f4e66131d55?q=80&w=987&auto=format&fit=crop",
    "Pintura",
    "Pintar el cielorraso con manchas de humedad en tu departamento de Parque Avellaneda: cuánto cuesta solucionarlo en 2026",
    "Pintar el cielorraso con manchas de humedad en un departamento de Parque Avellaneda cuesta en 2026 entre $5.000 y $13.000 por m², y puede sumar un tratamiento antihumedad previo según el caso.",
    """<p>Pintar el cielorraso con manchas de humedad en un departamento de Parque Avellaneda cuesta en 2026 entre <strong>$5.000 y $13.000 por m²</strong>, y puede sumar el costo de un tratamiento antihumedad previo si la mancha vuelve a aparecer.</p><h2>¿Alcanza con pintar o hay que tratar la humedad primero?</h2><p>Si la mancha es vieja y ya no crece, alcanza con un sellador antimanchas antes de pintar; pero si la humedad sigue activa, conviene resolver el origen (filtración, condensación) antes de repintar, porque la mancha vuelve a marcarse.</p><h2>Qué incluye el trabajo del pintor</h2><ul><li>✅ Lijado y limpieza de la zona con mancha</li><li>✅ Aplicación de sellador antimanchas o antihumedad</li><li>✅ Dos manos de pintura para cielorraso en toda la superficie</li></ul><h2>¿Por qué conviene pintar todo el cielorraso y no solo la mancha?</h2><p>Pintar solo el sector manchado suele dejar una diferencia de tono visible con el resto del cielorraso, sobre todo si la pintura original ya tiene un tiempo, por eso conviene una mano pareja en todo el ambiente.</p><h2>Cuánto dura el trabajo</h2><p>En un departamento de Parque Avellaneda, pintar un cielorraso con tratamiento antimanchas incluido suele resolverse en uno a dos días, según la cantidad de ambientes afectados.</p><h2>¿La mancha puede volver después de pintar?</h2><p>Sí, si el origen de la humedad no se resuelve (una filtración de la terraza o cañería, por ejemplo), la mancha suele reaparecer aunque se haya pintado con sellador antihumedad.</p>""" + cta("pintor", "Pintor", "Buenos Aires (CABA)")
)

# 9. Villa Luro - plomeria - termotanque nuevo
add(
    "plomeria", "🚿",
    "https://images.pexels.com/photos/27928762/pexels-photo-27928762.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Plomería",
    "Instalar un termotanque nuevo en tu casa de Villa Luro: cuánto cuesta un plomero en 2026",
    "Instalar un termotanque nuevo en una casa de Villa Luro cuesta en 2026 entre $125.000 y $183.000, sin contar el valor del equipo, según el tipo de conexión y si hay que adaptar la cañería existente.",
    """<p>Instalar un termotanque nuevo en una casa de Villa Luro cuesta en 2026 entre <strong>$125.000 y $183.000</strong>, un valor que no incluye el equipo y varía según el tipo de conexión y si hay que adaptar la cañería existente.</p><h2>¿Termotanque eléctrico o a gas?</h2><p>El termotanque eléctrico es más simple de instalar porque no depende de una cañería de gas, mientras que el termotanque a gas suele calentar más rápido pero necesita conexión a la instalación de gas y su propio venteo.</p><h2>Qué incluye la instalación</h2><ul><li>✅ Fijación del equipo y conexión a la cañería de agua fría y caliente</li><li>✅ Válvula de seguridad y llave de corte propia</li><li>✅ Prueba de funcionamiento y verificación de fugas</li></ul><h2>¿Hace falta sacar el termotanque viejo antes?</h2><p>Sí, en la mayoría de los casos el plomero retira el equipo anterior como parte del trabajo, algo que conviene confirmar en el presupuesto para que no sea un costo aparte.</p><h2>Cuánto dura la instalación</h2><p>Un plomero suele instalar un termotanque nuevo en una casa de Villa Luro en dos a cuatro horas, siempre que la cañería existente no necesite modificaciones grandes.</p><h2>¿Qué litraje conviene para una casa de 3 o 4 personas?</h2><p>Para una familia de tres a cuatro personas suele alcanzar con un termotanque de 80 a 100 litros, aunque conviene confirmarlo según la cantidad de baños y el uso simultáneo de agua caliente.</p>""" + cta("plomero", "Plomero", "Buenos Aires (CABA)")
)

# 10. Congreso - plomeria - destape de cañeria urgente
add(
    "plomeria", "🚿",
    "https://images.pexels.com/photos/6195894/pexels-photo-6195894.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Plomería",
    "Destape de cañería tapada en tu departamento de Congreso: cuánto cuesta y cuándo es urgente",
    "Destapar una cañería tapada en un departamento de Congreso cuesta en 2026 entre $90.000 y $140.000, y se vuelve urgente cuando el agua empieza a rebalsar en vez de solo drenar lento.",
    """<p>Destapar una cañería tapada en un departamento de Congreso cuesta en 2026 entre <strong>$90.000 y $140.000</strong>, y se vuelve urgente cuando el agua empieza a rebalsar en vez de solo drenar lento.</p><h2>¿Cuándo un desagüe lento se convierte en una urgencia?</h2><p>Mientras el agua drena, aunque sea despacio, hay margen para pedir turno; pero si el agua deja de bajar por completo o empieza a rebalsar por otra bocha de desagüe, conviene llamar a un plomero de urgencia.</p><h2>Qué incluye el destape</h2><ul><li>✅ Diagnóstico del punto exacto de la obstrucción</li><li>✅ Destape con sondas mecánicas o hidrojet según el caso</li><li>✅ Prueba de que el agua vuelve a drenar con normalidad</li></ul><h2>¿Por qué se tapan las cañerías en un departamento de Congreso?</h2><p>En edificios con años, la acumulación de grasa, restos de jabón y sarro en cañerías antiguas suele ser la causa más común, sobre todo en desagües de cocina y baño que se usan a diario.</p><h2>¿Sirve usar productos químicos antes de llamar al plomero?</h2><p>Puede destapar obstrucciones chicas y recientes, pero en cañerías viejas o con una obstrucción más profunda no suele alcanzar, y además puede dañar cañerías de metal si se usa seguido.</p><h2>¿El destape garantiza que no se vuelva a tapar?</h2><p>Depende de la causa: si es acumulación de grasa puede repetirse con el tiempo, mientras que si hay una raíz o una rotura en la cañería, conviene una revisión con cámara para confirmar el estado real del caño.</p>""" + cta("plomero", "Plomero", "Buenos Aires (CABA)")
)

# Verification
assert len(new_posts) == 10, len(new_posts)
ids = [p["id"] for p in new_posts]
assert len(set(ids)) == 10
existing_ids = set(p["id"] for p in posts)
assert not (existing_ids & set(ids)), "ID collision!"

for p in new_posts:
    wc = len(p["content"].replace("<", " <").split())
    print(p["id"], p["cat"], wc, "words(approx incl tags)", "-", p["title"][:60])

posts.extend(new_posts)

with open(posts_path, "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print("TOTAL POSTS NOW:", len(posts))
print("OK - posts.json updated")
