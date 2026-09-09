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

# 1. Villa Riachuelo - plomeria - bomba presurizadora
add(
    "plomeria", "🚿",
    "https://images.pexels.com/photos/17556197/pexels-photo-17556197.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Plomería",
    "Instalar una bomba presurizadora en tu casa de Villa Riachuelo: cuánto cuesta en 2026",
    "Instalar una bomba presurizadora en una casa de Villa Riachuelo cuesta en 2026 entre $109.000 y $240.000, sin contar el valor del equipo, según la potencia necesaria y la distancia hasta el tanque.",
    """<p>Instalar una bomba presurizadora en una casa de Villa Riachuelo cuesta en 2026 entre <strong>$109.000 y $240.000</strong>, un valor que no incluye el equipo y varía según la potencia necesaria y la distancia hasta el tanque de agua.</p><h2>¿Cuándo hace falta una bomba presurizadora?</h2><p>Conviene instalarla cuando la presión de agua es baja en los pisos altos o en las canillas más alejadas del tanque, algo frecuente en casas de Villa Riachuelo con el tanque a poca altura sobre el techo.</p><h2>Qué incluye la instalación</h2><ul><li>✅ Conexión de la bomba a la cañería de entrada del tanque</li><li>✅ Instalación eléctrica dedicada con su propia protección</li><li>✅ Calibración de la presión de salida</li></ul><h2>¿Qué potencia de bomba conviene para una casa?</h2><p>Depende de la cantidad de baños y de si hay uso simultáneo de varias canillas o la ducha con el lavarropas, algo que el plomero evalúa antes de recomendar el equipo.</p><h2>Cuánto dura la instalación</h2><p>Un plomero suele instalar una bomba presurizadora en una casa de Villa Riachuelo en tres a cinco horas, si la cañería de entrada ya está en condiciones.</p><h2>¿La bomba hace ruido?</h2><p>Las bombas presurizadoras modernas son bastante silenciosas, aunque conviene instalarlas sobre una base que amortigüe la vibración para que no se transmita a la estructura de la casa.</p>""" + cta("plomero", "Plomero", "Buenos Aires (CABA)")
)

# 2. San Cristobal - plomeria - cambiar cañeria vieja de un baño
add(
    "plomeria", "🚿",
    "https://destapacor.com.ar/wp-content/uploads/2020/05/Destapa-ca%C3%B1erias.jpg",
    "Plomería",
    "Cambiar la cañería vieja de agua fría y caliente en el baño de tu departamento en San Cristóbal: cuánto cuesta en 2026",
    "Cambiar la cañería vieja de agua fría y caliente en el baño de un departamento en San Cristóbal cuesta en 2026 entre $550.000 y $650.000 para los cuatro artefactos, sin contar la reposición de revestimientos.",
    """<p>Cambiar la cañería vieja de agua fría y caliente en el baño de un departamento en San Cristóbal cuesta en 2026 entre <strong>$550.000 y $650.000</strong> para los cuatro artefactos del baño, sin contar la reposición de cerámicos o revestimientos que haya que romper.</p><h2>¿Cómo saber si conviene cambiar toda la cañería?</h2><p>Si el edificio es antiguo y la cañería es de plomo o hierro galvanizado, con manchas de óxido en el agua o pérdidas frecuentes, suele convenir más el cambio completo que ir parchando reparaciones puntuales.</p><h2>Qué incluye el trabajo</h2><ul><li>✅ Retiro de la cañería vieja hasta cada artefacto</li><li>✅ Cañería nueva de fusión o similar, con prueba hidráulica</li><li>✅ Reconexión de inodoro, bacha, ducha y bidé</li></ul><h2>¿Hay que romper la pared para hacer este trabajo?</h2><p>En la mayoría de los departamentos de San Cristóbal con cañería embutida, sí hace falta picar parte de la pared, por eso conviene coordinar con un albañil la reposición de revoque y cerámica después.</p><h2>Cuánto dura la obra</h2><p>El cambio completo de cañería de un baño suele resolverse en tres a cinco días, entre la rotura, el tendido nuevo y la prueba de hermeticidad antes de cerrar la pared.</p><h2>¿Conviene aprovechar y cambiar los artefactos también?</h2><p>Si de todos modos se va a romper la pared, muchas familias en San Cristóbal aprovechan para cambiar grifería o el inodoro, aunque no es obligatorio para el cambio de cañería en sí.</p>""" + cta("plomero", "Plomero", "Buenos Aires (CABA)"),
    image_credit="Foto: Destapacor"
)

# 3. Monserrat - carpinteria - piso flotante
add(
    "carpinteria", "🔨",
    "https://images.pexels.com/photos/5691493/pexels-photo-5691493.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Carpintería",
    "Colocar piso flotante en tu departamento de Monserrat: cuánto cuesta un carpintero en 2026",
    "Colocar piso flotante en un departamento de Monserrat cuesta en 2026 entre $5.300 y $8.200 por m², sin contar el valor de las tablas ni la manta acústica.",
    """<p>Colocar piso flotante en un departamento de Monserrat cuesta en 2026 entre <strong>$5.300 y $8.200 por m²</strong>, un valor que corresponde solo a la mano de obra, sin contar las tablas ni la manta acústica.</p><h2>¿Por qué elegir piso flotante en vez de piso de madera maciza?</h2><p>El piso flotante es más económico, se coloca más rápido porque no necesita clavado ni pegado a la base, y en un departamento de Monserrat con losa nivelada suele ser la opción más práctica para renovar sin obra pesada.</p><h2>Qué incluye la colocación</h2><ul><li>✅ Nivelación y manta acústica sobre el contrapiso</li><li>✅ Colocación de las tablas con sistema de encastre</li><li>✅ Zócalos perimetrales de terminación</li></ul><h2>¿Hace falta sacar el piso viejo antes?</h2><p>No siempre: si la superficie está firme y nivelada, el piso flotante se puede colocar encima del piso existente, lo que ahorra tiempo y costo de demolición.</p><h2>Cuánto dura la colocación</h2><p>Un carpintero suele colocar el piso flotante de un departamento de dos ambientes en Monserrat en dos a tres días, según la cantidad de cortes que requiera el diseño del ambiente.</p><h2>¿El piso flotante aguanta la humedad de una cocina o un baño?</h2><p>Depende del tipo: hay versiones con núcleo hidrófugo pensadas para ambientes húmedos, pero conviene confirmarlo antes de instalarlo en cocina o baño.</p>""" + cta("carpintero", "Carpintero", "Buenos Aires (CABA)")
)

# 4. Abasto - carpinteria - puerta que no cierra
add(
    "carpinteria", "🔨",
    "https://images.pexels.com/photos/16047683/pexels-photo-16047683.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Carpintería",
    "Arreglar una puerta que no cierra bien en tu departamento del Abasto: cuánto cuesta en 2026",
    "Arreglar una puerta que no cierra bien en un departamento del Abasto cuesta en 2026 entre $19.000 y $30.000, según si el problema es del marco, las bisagras o la hoja de la puerta.",
    """<p>Arreglar una puerta que no cierra bien en un departamento del Abasto cuesta en 2026 entre <strong>$19.000 y $30.000</strong>, según si el problema está en el marco, en las bisagras o en la hoja de la puerta que se combó con el tiempo.</p><h2>¿Por qué las puertas dejan de cerrar bien con el tiempo?</h2><p>En edificios antiguos del Abasto es común que el marco se mueva levemente por asentamiento del edificio, o que la madera de la hoja se hinche con la humedad y roce contra el marco.</p><h2>Qué revisa el carpintero</h2><ul><li>✅ Alineación del marco y las bisagras</li><li>✅ Estado de la hoja: si está combada o hinchada</li><li>✅ Ajuste de la cerradura y el pestillo</li></ul><h2>¿Se puede ajustar sin cambiar toda la puerta?</h2><p>En la mayoría de los casos sí: un carpintero puede lijar el borde que roza, recalzar las bisagras o ajustar el marco sin necesidad de reemplazar la puerta completa.</p><h2>Cuánto dura el ajuste</h2><p>Un ajuste estándar de puerta en un departamento del Abasto suele resolverse en una sola visita de una a dos horas.</p><h2>¿Cuándo conviene cambiar la puerta directamente?</h2><p>Si la hoja está muy deformada o dañada por humedad de forma permanente, puede salir más conveniente cambiarla que seguir ajustándola cada pocos meses.</p>""" + cta("carpintero", "Carpintero", "Buenos Aires (CABA)")
)

# 5. Chacabuco - pintura - pintar 2 ambientes + baño
add(
    "pintura", "🎨",
    "https://images.pexels.com/photos/7218683/pexels-photo-7218683.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Pintura",
    "Pintar dos ambientes y el baño de tu departamento en Chacabuco: cuánto cuesta en 2026",
    "Pintar dos ambientes y el baño de un departamento en Chacabuco cuesta en 2026 entre $105.000 y $230.000, según el estado de las paredes y el tipo de pintura elegida.",
    """<p>Pintar dos ambientes y el baño de un departamento en Chacabuco cuesta en 2026 entre <strong>$105.000 y $230.000</strong>, un valor que varía según el estado de las paredes y el tipo de pintura elegida para cada ambiente.</p><h2>¿Por qué el baño cuesta distinto que el resto de los ambientes?</h2><p>El baño necesita una pintura resistente a la humedad, con mayor cantidad de manos en algunos casos, lo que puede subir el costo por metro cuadrado en comparación con living o dormitorio.</p><h2>Qué incluye el trabajo de pintura</h2><ul><li>✅ Preparación de superficie: lijado y tapado de agujeros</li><li>✅ Protección de pisos, marcos y artefactos</li><li>✅ Dos manos de pintura en cada ambiente</li></ul><h2>Cuánto dura el trabajo</h2><p>Un pintor suele terminar dos ambientes y un baño en un departamento de Chacabuco en tres a cuatro días, según si hay que reparar grietas antes de pintar.</p><h2>¿Conviene pintar con los muebles adentro o vacío?</h2><p>Con el departamento vacío el trabajo es más rápido y prolijo, pero si hay que pintar con muebles, el pintor cubre y corre el mobiliario para poder trabajar cada pared.</p><h2>¿Qué tipo de pintura conviene para el baño?</h2><p>Una pintura antihumedad o esmalte sintético al agua resiste mejor la condensación de la ducha que una pintura látex común para interior.</p>""" + cta("pintor", "Pintor", "Buenos Aires (CABA)")
)

# 6. Parque Chas - pintura - impermeabilizar azotea
add(
    "pintura", "🎨",
    "https://images.pexels.com/photos/5493654/pexels-photo-5493654.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Pintura",
    "Impermeabilizar la azotea de tu casa en Parque Chas: cuánto cuesta en 2026",
    "Impermeabilizar la azotea de una casa en Parque Chas cuesta en 2026 entre $90.000 y $220.000, según el estado de la superficie y el tipo de membrana o pintura impermeabilizante elegida.",
    """<p>Impermeabilizar la azotea de una casa en Parque Chas cuesta en 2026 entre <strong>$90.000 y $220.000</strong>, según el estado de la superficie y si se usa membrana asfáltica o pintura impermeabilizante.</p><h2>¿Cuándo conviene impermeabilizar la azotea?</h2><p>Conviene hacerlo antes de que aparezcan manchas de humedad en el cielorraso del piso de abajo, y en general se recomienda revisar la azotea cada dos o tres años, sobre todo antes del verano.</p><h2>Qué incluye el trabajo</h2><ul><li>✅ Limpieza y reparación de grietas en la superficie</li><li>✅ Aplicación de membrana o pintura impermeabilizante</li><li>✅ Revisión de desagües y babetas</li></ul><h2>¿Membrana asfáltica o pintura impermeabilizante?</h2><p>La membrana asfáltica dura más tiempo y resiste mejor el pisoteo, mientras que la pintura impermeabilizante es más económica pero suele necesitar retoques cada uno o dos años.</p><h2>Cuánto dura el trabajo</h2><p>En una casa de Parque Chas, impermeabilizar una azotea estándar suele resolverse en dos a tres días, dependiendo del clima para que cada capa seque bien.</p><h2>¿Hace falta impermeabilizar toda la azotea o solo el sector con filtración?</h2><p>Aunque la filtración aparezca en un solo punto, conviene tratar toda la superficie, porque el agua puede filtrar desde otro sector y aparecer manchada en un lugar distinto.</p>""" + cta("pintor", "Pintor", "Buenos Aires (CABA)")
)

# 7. Agronomia - albanileria - colocar ceramica cocina
add(
    "albanileria", "🧱",
    "https://images.pexels.com/photos/10099318/pexels-photo-10099318.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Albañilería",
    "Colocar cerámica en la cocina de tu departamento en Agronomía: cuánto cuesta un albañil en 2026",
    "Colocar cerámica en el piso de la cocina de un departamento en Agronomía cuesta en 2026 entre $9.000 y $16.500 por m², sin contar el valor de las piezas ni el material de pegado.",
    """<p>Colocar cerámica en el piso de la cocina de un departamento en Agronomía cuesta en 2026 entre <strong>$9.000 y $16.500 por m²</strong>, un valor que corresponde solo a la mano de obra, sin contar las piezas ni el material de pegado.</p><h2>¿Qué hay que revisar antes de colocar la cerámica nueva?</h2><p>Conviene revisar que el contrapiso esté nivelado y sin humedad, sobre todo en cocinas de departamentos de Agronomía cerca de la zona de pileta, donde suele haber más humedad acumulada con el tiempo.</p><h2>Qué incluye el trabajo del albañil</h2><ul><li>✅ Retiro del piso anterior si hace falta</li><li>✅ Nivelación del contrapiso</li><li>✅ Colocación de la cerámica con juntas parejas</li></ul><h2>¿Se puede colocar cerámica nueva sobre la vieja?</h2><p>En algunos casos sí, si la superficie está firme y bien adherida, aunque en cocinas conviene evaluarlo caso por caso porque suma altura al piso y puede afectar el cierre de puertas bajomesada.</p><h2>Cuánto dura la colocación</h2><p>Un albañil suele colocar la cerámica del piso de una cocina en Agronomía en uno a dos días, más el tiempo de secado antes de pisar con normalidad.</p><h2>¿Conviene cerámica rectificada para la cocina?</h2><p>Da una terminación más prolija con juntas finas, aunque para una cocina cualquiera de las dos opciones funciona bien si la colocación está bien hecha.</p>""" + cta("albañil", "Alba%C3%B1il", "Buenos Aires (CABA)")
)

# 8. Paternal - albanileria - reforma completa de baño
add(
    "albanileria", "🧱",
    "https://images.pexels.com/photos/7534564/pexels-photo-7534564.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Albañilería",
    "Reforma completa del baño en tu casa de Paternal: cuánto cuesta en 2026",
    "Una reforma completa del baño en una casa de Paternal cuesta en 2026 entre $950.000 y $2.900.000 solo de mano de obra y demolición, sin contar sanitarios, grifería ni revestimientos.",
    """<p>Una reforma completa del baño en una casa de Paternal cuesta en 2026 entre <strong>$950.000 y $2.900.000</strong>, un valor que corresponde solo a la mano de obra y la demolición, sin contar sanitarios, grifería ni revestimientos nuevos.</p><h2>¿Por qué el rango de precios es tan amplio?</h2><p>Depende de si se cambia solo la terminación (revestimientos y sanitarios) o si también hay que mover cañerías y modificar la distribución del baño, que implica más demolición y trabajo de albañilería.</p><h2>Qué incluye una reforma completa</h2><ul><li>✅ Demolición de revestimientos y sanitarios existentes</li><li>✅ Adecuación o cambio de cañerías si hace falta</li><li>✅ Colocación de revestimientos, sanitarios y terminaciones nuevas</li></ul><h2>Cuánto dura una reforma de baño</h2><p>En una casa de Paternal, una reforma completa suele llevar entre dos y cuatro semanas, según la complejidad y si hay que esperar tiempos de secado entre etapas.</p><h2>¿Conviene coordinar albañil, plomero y electricista por separado?</h2><p>Muchas familias en Paternal prefieren un albañil que coordine todo el equipo, para evitar demoras entre un oficio y otro durante la obra.</p><h2>¿Se puede usar otro baño de la casa mientras se hace la reforma?</h2><p>Si la casa tiene más de un baño, conviene planificar la obra para no quedarse sin baño disponible durante las semanas de trabajo.</p>""" + cta("albañil", "Alba%C3%B1il", "Buenos Aires (CABA)")
)

# 9. Versalles - gas - instalar cocina a gas
add(
    "gas", "🔥",
    "https://images.pexels.com/photos/994164/pexels-photo-994164.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Gas",
    "Instalar una cocina a gas en tu departamento de Versalles: cuánto cuesta en 2026",
    "Instalar una cocina a gas en un departamento de Versalles cuesta en 2026 entre $120.000 y $155.000, sin contar el valor del artefacto, según el estado de la conexión existente.",
    """<p>Instalar una cocina a gas en un departamento de Versalles cuesta en 2026 entre <strong>$120.000 y $155.000</strong>, un valor que no incluye el artefacto y varía según el estado de la conexión de gas existente.</p><h2>¿Por qué hay que llamar a un gasista y no conectarla uno mismo?</h2><p>La conexión de un artefacto a gas debe hacerla un gasista matriculado, que verifica la hermeticidad de la conexión y deja la instalación en condiciones seguras según la normativa vigente.</p><h2>Qué incluye la instalación</h2><ul><li>✅ Conexión de la cocina a la llave de paso existente</li><li>✅ Prueba de hermeticidad de la conexión</li><li>✅ Verificación de nivelación y funcionamiento de las hornallas</li></ul><h2>¿Hace falta cambiar la cañería para instalar la cocina nueva?</h2><p>No siempre: si la llave de paso y la cañería existente están en buen estado, alcanza con conectar el artefacto nuevo, aunque conviene que el gasista lo confirme antes.</p><h2>Cuánto dura la instalación</h2><p>Un gasista suele instalar una cocina nueva en un departamento de Versalles en una hora, siempre que no haga falta modificar la cañería existente.</p><h2>¿La cocina viene con el caño de conexión incluido?</h2><p>Depende del modelo: conviene confirmarlo al comprar el artefacto, porque algunas cocinas requieren comprar el caño flexible de conexión por separado.</p>""" + cta("gasista", "Gasista", "Buenos Aires (CABA)")
)

# 10. Villa Real - gas - limpieza de calefactor
add(
    "gas", "🔥",
    "https://images.pexels.com/photos/10871737/pexels-photo-10871737.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Gas",
    "Limpieza de calefactor a gas en tu casa de Villa Real: cuánto cuesta y cada cuánto hacerla en 2026",
    "La limpieza de un calefactor a gas en una casa de Villa Real cuesta en 2026 entre $80.000 y $105.000, un servicio que conviene hacer al menos una vez al año antes de empezar a usarlo en invierno.",
    """<p>La limpieza de un calefactor a gas en una casa de Villa Real cuesta en 2026 entre <strong>$80.000 y $105.000</strong>, un servicio que conviene hacer al menos una vez al año, idealmente antes de empezar a usarlo en invierno.</p><h2>¿Por qué hay que limpiar el calefactor todos los años?</h2><p>Con el uso se acumula polvo y hollín en el quemador y la rejilla, lo que afecta la combustión y puede hacer que el artefacto consuma más gas del necesario para calentar lo mismo.</p><h2>Qué incluye el servicio de limpieza</h2><ul><li>✅ Desarmado y limpieza del quemador</li><li>✅ Revisión de la llama y el piloto</li><li>✅ Verificación de la salida de gases si tiene tiro balanceado</li></ul><h2>¿Cómo saber si el calefactor necesita limpieza?</h2><p>Si la llama se ve amarilla en vez de azul, si tarda en encender o si hay olor raro al prenderlo, son señales de que conviene una revisión antes de seguir usándolo.</p><h2>Cuánto dura el servicio</h2><p>Un gasista suele limpiar un calefactor de una casa de Villa Real en menos de una hora, salvo que encuentre alguna pieza que haya que reparar o cambiar.</p><h2>¿Se puede limpiar el calefactor uno mismo?</h2><p>Se puede pasar un paño por afuera, pero limpiar el quemador y revisar la combustión requiere un gasista matriculado, porque es un artefacto que trabaja con gas.</p>""" + cta("gasista", "Gasista", "Buenos Aires (CABA)")
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
