import json

posts_path = "blog/posts.json"
with open(posts_path, encoding="utf-8") as f:
    posts = json.load(f)

max_id = max(p["id"] for p in posts)
next_id = max_id + 1

new_posts = []

def add(cat, emoji, image, tag, title, excerpt, content, read_time="4 min"):
    global next_id
    new_posts.append({
        "id": next_id,
        "cat": cat,
        "emoji": emoji,
        "image": image,
        "tag": tag,
        "title": title,
        "excerpt": excerpt,
        "date": "Agosto 2026",
        "readTime": read_time,
        "content": content
    })
    next_id += 1

# 1. Palermo - electricidad - toma lavavajillas
add(
    "electricidad", "⚡",
    "https://images.pexels.com/photos/8186473/pexels-photo-8186473.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Electricidad",
    "Instalar un toma eléctrico para el lavavajillas en la cocina de tu departamento en Palermo: cuánto cuesta en 2026",
    "Instalar un toma eléctrico dedicado para el lavavajillas en una cocina de Palermo cuesta en 2026 entre $35.000 y $60.000, según la distancia al tablero y si hace falta abrir pared.",
    """<p>Instalar un toma eléctrico dedicado para el lavavajillas en una cocina de Palermo cuesta en 2026 entre <strong>$35.000 y $60.000</strong>, según la distancia hasta el tablero y si hace falta romper pared para pasar el cable.</p><h2>¿Por qué el lavavajillas necesita un toma aparte?</h2><p>El lavavajillas consume bastante corriente durante el ciclo de lavado, y compartir un tomacorriente con otros electrodomésticos de la cocina puede hacer saltar la térmica. Un electricista matriculado en CABA recomienda un circuito dedicado con su propia protección diferencial.</p><h2>Qué incluye la instalación</h2><ul><li>✅ Cableado desde el tablero hasta el mueble bajo mesada</li><li>✅ Toma con puesta a tierra específica para el electrodoméstico</li><li>✅ Protección térmica y diferencial propia en el tablero</li></ul><h2>Cuánto tarda el trabajo</h2><p>En un departamento de Palermo sin obra adicional, la instalación de este punto eléctrico suele resolverse en una sola visita de entre dos y cuatro horas.</p><h2>¿Se puede conectar el lavavajillas a un tomacorriente común?</h2><p>No es recomendable de forma permanente: un tomacorriente compartido no tiene la protección adecuada y aumenta el riesgo de sobrecarga en la instalación eléctrica de la cocina.</p><h2>¿Hay que pedir un electricista matriculado para este trabajo?</h2><p>Sí, porque implica modificar el tablero y agregar una nueva llave de protección, algo que en CABA debe hacer un electricista matriculado.</p><div class='modal-cta'><p>¿Necesitás un electricista verificado en CABA?</p><a href='https://hogarex.ar' class='btn-yellow'>Encontrá uno ahora →</a></div>"""
)

# 2. Belgrano - electricidad - tablero bifasico
add(
    "electricidad", "⚡",
    "https://images.pexels.com/photos/17842834/pexels-photo-17842834.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Electricidad",
    "Instalar un tablero eléctrico bifásico en tu PH de Belgrano: cuánto cuesta en 2026",
    "Instalar un tablero eléctrico bifásico en un PH de Belgrano cuesta en 2026 entre $180.000 y $350.000, según la cantidad de circuitos y si hay que ampliar la potencia contratada.",
    """<p>Instalar un tablero eléctrico bifásico en un PH de Belgrano cuesta en 2026 entre <strong>$180.000 y $350.000</strong>, según la cantidad de circuitos que se dividan y si hace falta ampliar la potencia contratada con la distribuidora.</p><h2>¿Cuándo conviene pasar a instalación bifásica?</h2><p>Conviene cuando la instalación monofásica de un PH de Belgrano ya no soporta la suma de aires acondicionados, termotanque eléctrico y otros electrodomésticos grandes sin que salte la térmica general seguido.</p><h2>Qué incluye el cambio de tablero</h2><ul><li>✅ Tablero nuevo con llaves térmicas por circuito</li><li>✅ Disyuntor diferencial de mayor capacidad</li><li>✅ Redistribución de circuitos entre las dos fases</li></ul><h2>Cuánto dura la obra</h2><p>Un electricista matriculado en CABA suele completar el cambio de tablero en un PH de Belgrano en una o dos jornadas, dependiendo de si hay que abrir pared para el nuevo cableado.</p><h2>¿Hace falta avisar a la distribuidora de luz?</h2><p>Sí, porque pasar a bifásica implica un cambio en la potencia contratada y en algunos casos en el medidor, un trámite que gestiona el electricista junto con el propietario.</p><h2>¿Sirve para toda la casa o solo para algunos ambientes?</h2><p>El tablero bifásico redistribuye toda la instalación eléctrica del PH, no solo un sector, para equilibrar la carga entre las dos fases.</p><div class='modal-cta'><p>¿Necesitás un electricista verificado en CABA?</p><a href='https://hogarex.ar' class='btn-yellow'>Encontrá uno ahora →</a></div>"""
)

# 3. Caballito - electricidad - cosquilleo heladera
add(
    "electricidad", "⚡",
    "https://images.pexels.com/photos/8583864/pexels-photo-8583864.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Electricidad",
    "Sentir cosquilleo al tocar la heladera en tu departamento de Caballito: qué lo causa y cuándo es urgente llamar a un electricista",
    "Sentir cosquilleo al tocar la heladera en un departamento de Caballito suele indicar una falla de puesta a tierra en el electrodoméstico o en el tomacorriente, y conviene revisarlo antes de seguir usándola.",
    """<p>Sentir cosquilleo al tocar la heladera en un departamento de Caballito suele indicar una <strong>falla de puesta a tierra</strong>, ya sea en el cable del electrodoméstico o en el tomacorriente donde está enchufada.</p><h2>¿Por qué pasa esto?</h2><p>Cuando la heladera no tiene una puesta a tierra correcta, una pequeña fuga de corriente puede circular por la carcasa metálica y sentirse como un cosquilleo al tocarla, especialmente con las manos húmedas.</p><h2>Cuándo es urgente llamar a un electricista</h2><p>Si el cosquilleo se siente de forma clara y repetida, hay que desenchufar la heladera y llamar a un electricista matriculado en CABA de inmediato: es una señal de riesgo de electrocución, no solo una molestia.</p><ul><li>✅ Revisar si el tomacorriente tiene puesta a tierra real</li><li>✅ Medir la fuga de corriente con un tester</li><li>✅ Verificar el cable de la heladera en el punto de conexión</li></ul><h2>¿Se puede seguir usando la heladera mientras tanto?</h2><p>No conviene: mientras no se confirme el origen de la falla eléctrica, lo más seguro en un departamento de Caballito es desenchufarla y usar otro tomacorriente para no perder la comida.</p><h2>¿El diferencial del tablero no debería cortar la luz en estos casos?</h2><p>Debería, pero si el diferencial está viejo o mal calibrado puede no saltar con fugas chicas, por eso el cosquilleo igual se siente aunque la luz no se corte.</p><div class='modal-cta'><p>¿Necesitás un electricista verificado en CABA?</p><a href='https://hogarex.ar' class='btn-yellow'>Encontrá uno ahora →</a></div>"""
)

# 4. Villa Urquiza - electricidad - elegir electricista sin que te estafen
add(
    "electricidad", "⚡",
    "https://images.pexels.com/photos/4312852/pexels-photo-4312852.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Guía",
    "Cómo elegir un electricista en Villa Urquiza sin que te estafen: qué preguntar antes de contratar",
    "Elegir un electricista en Villa Urquiza sin que te estafen implica pedir matrícula, presupuesto por escrito y garantía del trabajo antes de que empiece la obra.",
    """<p>Elegir un electricista en Villa Urquiza sin que te estafen implica pedir la <strong>matrícula habilitante</strong>, un presupuesto por escrito y la garantía del trabajo antes de que arranque la obra.</p><h2>¿Qué preguntar antes de contratar?</h2><p>Conviene preguntar el número de matrícula, si el presupuesto incluye materiales, cuánto tiempo va a demorar el trabajo y qué garantía da sobre la instalación una vez terminada.</p><h2>Señales de alerta al pedir presupuesto</h2><ul><li>✅ Presupuesto verbal sin ningún detalle por escrito</li><li>✅ Precio muy por debajo del resto sin explicación clara</li><li>✅ Pedir el pago completo antes de empezar el trabajo</li></ul><h2>Cuánto cuesta la visita de un electricista matriculado</h2><p>En Villa Urquiza, la visita de diagnóstico de un electricista matriculado ronda en 2026 entre <strong>$15.000 y $25.000</strong>, y ese valor suele descontarse del presupuesto final si se contrata el trabajo.</p><h2>¿Conviene pedir más de un presupuesto?</h2><p>Sí, pedir al menos dos o tres presupuestos en Villa Urquiza ayuda a comparar precios y detectar si alguno está fuera de rango para el trabajo eléctrico solicitado.</p><h2>¿La matrícula garantiza que el trabajo va a estar bien hecho?</h2><p>La matrícula certifica que el electricista está habilitado para trabajar en CABA, pero conviene igual pedir referencias de trabajos anteriores antes de contratar.</p><div class='modal-cta'><p>¿Necesitás un electricista verificado en CABA?</p><a href='https://hogarex.ar' class='btn-yellow'>Encontrá uno ahora →</a></div>"""
)

# 5. San Telmo - electricidad - matriculado cost
add(
    "electricidad", "⚡",
    "https://images.pexels.com/photos/1029243/pexels-photo-1029243.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Electricidad",
    "¿Cuánto cuesta un electricista matriculado en San Telmo en 2026?",
    "Un electricista matriculado en San Telmo cobra en 2026 entre $15.000 y $25.000 la visita de diagnóstico, más el costo de materiales y mano de obra según el trabajo.",
    """<p>Un electricista matriculado en San Telmo cobra en 2026 entre <strong>$15.000 y $25.000</strong> la visita de diagnóstico, un valor que no incluye materiales ni la mano de obra del arreglo en sí.</p><h2>¿Cuánto cuesta un electricista matriculado en San Telmo en 2026?</h2><p>Además de la visita, la hora adicional de trabajo de un electricista matriculado en San Telmo ronda entre <strong>$8.000 y $15.000</strong>, y los trabajos más grandes como cambios de tablero se cotizan aparte por el total del trabajo.</p><h2>Qué influye en el precio final</h2><ul><li>✅ La antigüedad de la instalación eléctrica del edificio</li><li>✅ Si hay que romper pared o pasar cañería nueva</li><li>✅ El horario: las urgencias fuera de horario suelen tener recargo</li></ul><h2>Por qué conviene un electricista matriculado y no uno sin habilitación</h2><p>En San Telmo, muchos edificios tienen instalaciones eléctricas antiguas, y un electricista matriculado sabe identificar riesgos como cableado de tela o falta de puesta a tierra antes de intervenir.</p><h2>¿El presupuesto incluye los materiales?</h2><p>No siempre: conviene confirmarlo antes de aceptar, porque algunos electricistas cotizan solo la mano de obra y los materiales se suman aparte.</p><h2>¿Hay recargo por trabajar en un edificio antiguo de San Telmo?</h2><p>Puede haberlo si la instalación requiere más tiempo de diagnóstico o adaptaciones especiales por la antigüedad del cableado original.</p><div class='modal-cta'><p>¿Necesitás un electricista verificado en CABA?</p><a href='https://hogarex.ar' class='btn-yellow'>Encontrá uno ahora →</a></div>"""
)

# 6. Boedo - electricidad - corte por sobrecarga
add(
    "electricidad", "⚡",
    "https://images.pexels.com/photos/17842843/pexels-photo-17842843.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Electricidad",
    "Cuánto tarda en resolverse un corte de luz por sobrecarga del tablero en tu casa de Boedo: qué hacer mientras esperás al electricista",
    "Un corte de luz por sobrecarga del tablero en una casa de Boedo suele resolverse en menos de una hora una vez que llega el electricista, bajando la carga y revisando la llave que saltó.",
    """<p>Un corte de luz por sobrecarga del tablero en una casa de Boedo suele resolverse en <strong>menos de una hora</strong> una vez que llega el electricista, identificando y bajando la carga que hizo saltar la llave térmica.</p><h2>¿Qué hacer mientras se espera al electricista?</h2><p>Lo primero es desenchufar los electrodomésticos de mayor consumo, como el aire acondicionado o el termotanque eléctrico, e intentar levantar la llave térmica del tablero una sola vez.</p><h2>Por qué se sobrecarga el tablero</h2><ul><li>✅ Demasiados electrodomésticos grandes conectados a la vez</li><li>✅ Una llave térmica vieja que ya no soporta la carga real de la casa</li><li>✅ Un cortocircuito puntual en algún artefacto</li></ul><h2>Cuándo el corte es más que una sobrecarga simple</h2><p>Si la llave térmica salta apenas se resetea, sin que haya electrodomésticos nuevos conectados, en una casa de Boedo eso suele indicar un problema en la instalación y no solo un exceso de consumo puntual.</p><h2>¿Es seguro resetear la llave térmica varias veces?</h2><p>No: si salta más de dos veces seguidas sin causa clara, conviene dejarla bajada y llamar a un electricista matriculado en vez de insistir.</p><h2>¿El corte puede dañar los electrodomésticos?</h2><p>El corte en sí no, pero las subas de tensión al reconectar pueden afectar equipos sensibles si no se revisa antes la causa de la sobrecarga.</p><div class='modal-cta'><p>¿Necesitás un electricista verificado en CABA?</p><a href='https://hogarex.ar' class='btn-yellow'>Encontrá uno ahora →</a></div>"""
)

# 7. Villa Devoto - electricidad - circuito heladera y freezer
add(
    "electricidad", "⚡",
    "https://images.pexels.com/photos/7027993/pexels-photo-7027993.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Electricidad",
    "Instalar un circuito dedicado para la heladera y el freezer en tu casa de Villa Devoto: cuánto cuesta en 2026",
    "Instalar un circuito eléctrico dedicado para la heladera y el freezer en una casa de Villa Devoto cuesta en 2026 entre $45.000 y $80.000, según la distancia al tablero.",
    """<p>Instalar un circuito eléctrico dedicado para la heladera y el freezer en una casa de Villa Devoto cuesta en 2026 entre <strong>$45.000 y $80.000</strong>, según la distancia hasta el tablero y si hay que abrir pared.</p><h2>¿Por qué conviene un circuito aparte para estos dos equipos?</h2><p>La heladera y el freezer funcionan de forma continua, y si comparten circuito con otros electrodomésticos de la cocina, cualquier corte por sobrecarga puede hacer perder la cadena de frío de ambos a la vez.</p><h2>Qué incluye el trabajo</h2><ul><li>✅ Cableado independiente desde el tablero</li><li>✅ Llave térmica propia para ese circuito</li><li>✅ Tomas con puesta a tierra para heladera y freezer</li></ul><h2>Cuánto dura la instalación</h2><p>En una casa de Villa Devoto sin obra adicional, un electricista matriculado suele resolver este circuito dedicado en una sola visita de medio día.</p><h2>¿Vale la pena si solo tengo heladera y no freezer aparte?</h2><p>Igual conviene, porque el objetivo principal es que la heladera no comparta circuito con el microondas o la pava eléctrica, que consumen mucho en el momento de uso.</p><h2>¿Este trabajo requiere modificar el tablero eléctrico completo?</h2><p>No necesariamente: si el tablero de la casa de Villa Devoto tiene lugar disponible, alcanza con sumar una llave térmica nueva sin cambiar el resto de la instalación.</p><div class='modal-cta'><p>¿Necesitás un electricista verificado en CABA?</p><a href='https://hogarex.ar' class='btn-yellow'>Encontrá uno ahora →</a></div>"""
)

# 8. Flores - plomeria - elegir plomero sin que te estafen
add(
    "plomeria", "🔧",
    "https://images.pexels.com/photos/8486975/pexels-photo-8486975.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Guía",
    "Cómo elegir un plomero en Flores sin que te estafen: qué preguntar antes de contratar",
    "Elegir un plomero en Flores sin que te estafen implica pedir presupuesto por escrito, preguntar si el precio incluye materiales y confirmar la garantía del trabajo antes de empezar.",
    """<p>Elegir un plomero en Flores sin que te estafen implica pedir el <strong>presupuesto por escrito</strong>, confirmar si incluye materiales y preguntar qué garantía cubre el trabajo una vez terminado.</p><h2>¿Qué preguntar antes de contratar un plomero?</h2><p>Conviene preguntar cuánto tiempo va a demorar el trabajo, si el precio es cerrado o puede variar según lo que encuentre al abrir la cañería, y qué garantía da sobre pérdidas futuras en el mismo punto.</p><h2>Señales de alerta al pedir presupuesto</h2><ul><li>✅ Presupuesto verbal sin ningún detalle por escrito</li><li>✅ Pedir el pago completo antes de empezar el trabajo</li><li>✅ No poder mostrar trabajos anteriores ni referencias</li></ul><h2>Cuánto cuesta la visita de un plomero en Flores</h2><p>En Flores, la visita de diagnóstico de un plomero ronda en 2026 entre <strong>$15.000 y $25.000</strong>, y ese monto suele descontarse del presupuesto final si se contrata la reparación completa.</p><h2>¿Conviene pedir más de un presupuesto antes de decidir?</h2><p>Sí, comparar al menos dos presupuestos en Flores ayuda a detectar si alguno está fuera de rango para el trabajo de plomería solicitado.</p><h2>¿Hay que pagar la visita si al final no se contrata el trabajo?</h2><p>En la mayoría de los casos sí, porque la visita cubre el tiempo y el diagnóstico del plomero, aunque el cliente decida no seguir adelante con la reparación.</p><div class='modal-cta'><p>¿Necesitás un plomero verificado en CABA?</p><a href='https://hogarex.ar' class='btn-yellow'>Encontrá uno ahora →</a></div>"""
)

# 9. Nunez - carpinteria - vestidor a medida
add(
    "carpinteria", "🔨",
    "https://images.pexels.com/photos/6782348/pexels-photo-6782348.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Carpintería",
    "Instalar un vestidor a medida en tu dormitorio de Núñez: cuánto cuesta un carpintero en 2026",
    "Instalar un vestidor a medida en un dormitorio de Núñez cuesta en 2026 entre $200.000 y $450.000, según los metros de estantería y el tipo de material elegido.",
    """<p>Instalar un vestidor a medida en un dormitorio de Núñez cuesta en 2026 entre <strong>$200.000 y $450.000</strong>, según los metros de estantería, la cantidad de cajones y el material elegido.</p><h2>¿Qué diferencia hay entre un vestidor a medida y un placard estándar?</h2><p>Un vestidor a medida se diseña según el espacio real del dormitorio, con la altura y distribución de baulera, cajonera y perchero pensada para ese ambiente puntual, mientras que un placard estándar viene en medidas fijas.</p><h2>Qué incluye el trabajo de un carpintero</h2><ul><li>✅ Medición y diseño a medida del espacio disponible</li><li>✅ Estructura en melamina o MDF según el presupuesto</li><li>✅ Herrajes, correderas y sistema de iluminación interior opcional</li></ul><h2>Cuánto dura la obra</h2><p>Un carpintero en Núñez suele tardar entre una y dos semanas desde la toma de medidas hasta la instalación final del vestidor, dependiendo de la complejidad del diseño.</p><h2>¿Conviene melamina o MDF para un vestidor?</h2><p>La melamina es más económica y resistente a la humedad, mientras que el MDF permite terminaciones más prolijas pero tiene un costo mayor por metro cuadrado.</p><h2>¿Hay que sacar el placard viejo antes de empezar?</h2><p>Sí, en la mayoría de los casos el carpintero retira el mueble anterior como parte del trabajo, aunque conviene confirmarlo en el presupuesto inicial.</p><div class='modal-cta'><p>¿Necesitás un carpintero verificado en CABA?</p><a href='https://hogarex.ar' class='btn-yellow'>Encontrá uno ahora →</a></div>"""
)

# 10. Villa Crespo - pintura - depto recien alquilado
add(
    "pintura", "🎨",
    "https://images.pexels.com/photos/18369835/pexels-photo-18369835.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Pintura",
    "Pintar un departamento recién alquilado en Villa Crespo antes de mudarte: cuánto cuesta y qué conviene priorizar en 2026",
    "Pintar un departamento recién alquilado en Villa Crespo antes de mudarte cuesta en 2026 entre $150.000 y $280.000 para dos ambientes, según el estado de las paredes y el tipo de pintura elegida.",
    """<p>Pintar un departamento recién alquilado en Villa Crespo antes de mudarte cuesta en 2026 entre <strong>$150.000 y $280.000</strong> para dos ambientes, según el estado de las paredes y el tipo de pintura elegida.</p><h2>¿Por qué conviene pintar antes de mudarse y no después?</h2><p>Pintar un departamento vacío en Villa Crespo es más rápido y económico que hacerlo con los muebles adentro, porque no hace falta cubrir ni mover nada durante el trabajo.</p><h2>Qué conviene priorizar con presupuesto limitado</h2><ul><li>✅ Living y dormitorio principal antes que ambientes secundarios</li><li>✅ Techos con manchas de humedad antes que paredes en buen estado</li><li>✅ Zócalos y marcos de puerta si están muy desgastados</li></ul><h2>Cuánto dura el trabajo</h2><p>Un pintor en Villa Crespo suele terminar un departamento de dos ambientes vacío en tres a cinco días, según la cantidad de manos de pintura necesarias.</p><h2>¿Conviene pedirle el trabajo al pintor de confianza del dueño o buscar uno propio?</h2><p>Conviene pedir presupuesto propio igual, porque el inquilino es quien paga el trabajo en la mayoría de los contratos y puede comparar precios antes de decidir.</p><h2>¿Hay que avisarle al propietario antes de pintar?</h2><p>Sí, conviene confirmarlo por escrito en el contrato de alquiler, sobre todo si se piensa cambiar el color original de las paredes.</p><div class='modal-cta'><p>¿Necesitás un pintor verificado en CABA?</p><a href='https://hogarex.ar' class='btn-yellow'>Encontrá uno ahora →</a></div>"""
)

# Verification
assert len(new_posts) == 10, len(new_posts)
cats = [p["cat"] for p in new_posts]
assert cats.count("electricidad") == 7, cats
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
