# -*- coding: utf-8 -*-
"""
Finanzas Spa · Calculadora de costos de la jornada para cualquier spa
Proyecto final ADMI 1301 · Introducción a la Programación · Universidad de los Andes

Este archivo contiene TODO el cálculo de la aplicación, escrito en Python.
La pantalla (index.html) solo recoge los datos y dibuja lo que este archivo devuelve.

IDEA DEL PROYECTO: el código no es de un spa en particular. La app empieza VACÍA:
cada spa escribe sus propios datos (personal, cabinas, tratamientos, precios, insumos y
cuántos clientes espera) y obtiene el cálculo de su jornada.
"Sunny Side Luxury Spa" es un spa FICTICIO que se incluye solo como EJEMPLO.

IMPORTANTE: las cifras del ejemplo son SUPUESTOS DE SIMULACIÓN propuestos por el grupo.
No son datos reales de ninguna empresa.
"""

import json

# =====================================================================
# 1. DATOS
# =====================================================================

# Spa de ejemplo (ficticio). Solo se usa si el usuario pulsa "Cargar ejemplo".
# El PRIMER tratamiento recibe el resto de los clientes, por eso su porcentaje se calcula solo.
EJEMPLO = {
    "nombre": "Sunny Side Luxury Spa",
    "clientes_por_terapeuta": 3,
    "clientes_por_recepcion": 10,
    "costo_turno_terapeuta": 200000,     # COP por turno
    "costo_turno_recepcion": 120000,     # COP por turno
    "cabinas": 8,
    "tratamientos": [
        {"nombre": "Masaje relajante", "precio": 200000, "insumos": 30000, "porcentaje": 50},
        {"nombre": "Facial hidratante premium", "precio": 260000, "insumos": 50000, "porcentaje": 30},
        {"nombre": "Ritual corporal", "precio": 360000, "insumos": 90000, "porcentaje": 20},
    ],
}
EJEMPLO_CLIENTES = 15

# El spa con el que se calcula ahora. Al empezar no hay ninguno (None = vacío).
spa = None

MAX_TRATAMIENTOS = 6
MAXIMO_DINERO = 100000000
NOMBRES_ESCENARIOS = ["Baja afluencia", "Ocupación media", "Agenda llena"]


# =====================================================================
# 2. VALIDACIÓN DE LOS DATOS QUE ESCRIBE EL SPA
# =====================================================================

# Convierte un texto en número entero. Si no es un número válido devuelve None.
# En los campos de dinero acepta "$200.000" o "200 000" (quita $, puntos y espacios).
def leer_entero(texto, es_dinero):
    texto = str(texto).strip()
    if es_dinero:
        texto = texto.replace("$", "").replace(".", "").replace(" ", "")
    # isdecimal() es True solo si son únicamente dígitos (rechaza letras, negativos y decimales)
    if texto.isdecimal() == False or len(texto) > 12:
        return None
    return int(texto)


# Revisa los datos del formulario. Devuelve (errores, datos limpios, advertencias).
# Si la lista de errores está vacía, los datos se pueden usar.
def validar_configuracion(datos):
    errores = []
    advertencias = []
    limpio = {}

    # Nombre del spa
    nombre = str(datos.get("nombre", "")).strip()
    if nombre == "":
        errores.append("Escriba el nombre del spa.")
    elif len(nombre) > 40:
        errores.append("El nombre del spa es muy largo (máximo 40 letras).")
    limpio["nombre"] = nombre

    # Personal, costos y cabinas: (clave, nombre en pantalla, mínimo, máximo, es dinero)
    campos = [
        ("clientes_por_terapeuta", "Clientes por terapeuta por turno", 1, 20, False),
        ("clientes_por_recepcion", "Clientes por persona de recepción/apoyo", 1, 200, False),
        ("costo_turno_terapeuta", "Costo del turno de un terapeuta", 1, MAXIMO_DINERO, True),
        ("costo_turno_recepcion", "Costo del turno de recepción/apoyo", 1, MAXIMO_DINERO, True),
        ("cabinas", "Cabinas del spa", 1, 100, False),
    ]
    for clave, etiqueta, minimo, maximo, es_dinero in campos:
        valor = leer_entero(datos.get(clave, ""), es_dinero)
        if valor == None or valor < minimo or valor > maximo:
            errores.append(f"{etiqueta}: escriba un número entero entre {minimo} y {maximo}"
                           + (" (en pesos, sin decimales)." if es_dinero else "."))
            valor = minimo
        limpio[clave] = valor

    # Tratamientos
    lista = datos.get("tratamientos", [])
    if type(lista) != list or len(lista) < 1:
        errores.append("Agregue al menos un tratamiento.")
        lista = []
    if len(lista) > MAX_TRATAMIENTOS:
        errores.append(f"La app admite hasta {MAX_TRATAMIENTOS} tratamientos.")
        lista = lista[:MAX_TRATAMIENTOS]

    tratamientos = []
    nombres_usados = []
    suma_resto = 0                      # suma de los porcentajes del tratamiento 2 en adelante
    for i in range(len(lista)):
        t = lista[i]
        if type(t) != dict:
            errores.append(f"Tratamiento {i + 1}: los datos no se pudieron leer.")
            continue
        titulo = f"Tratamiento {i + 1}"

        nombre_t = str(t.get("nombre", "")).strip()
        if nombre_t == "":
            errores.append(f"{titulo}: escriba el nombre.")
        elif len(nombre_t) > 40:
            errores.append(f"{titulo}: el nombre es muy largo (máximo 40 letras).")
        elif nombre_t.lower() in nombres_usados:
            errores.append(f"{titulo}: el nombre «{nombre_t}» está repetido.")
        nombres_usados.append(nombre_t.lower())
        if nombre_t != "":
            titulo = f"{titulo} ({nombre_t})"

        precio = leer_entero(t.get("precio", ""), True)
        if precio == None or precio < 1 or precio > MAXIMO_DINERO:
            errores.append(f"{titulo}: el precio debe ser un número entero de pesos mayor que 0.")
            precio = 1
        insumos = leer_entero(t.get("insumos", ""), True)
        if insumos == None or insumos > MAXIMO_DINERO:
            errores.append(f"{titulo}: el costo de insumos debe ser un número entero de pesos (puede ser 0).")
            insumos = 0

        # El primer tratamiento recibe el resto; los demás indican su porcentaje
        if i == 0:
            porcentaje = 0
        else:
            porcentaje = leer_entero(t.get("porcentaje", ""), False)
            if porcentaje == None or porcentaje > 100:
                errores.append(f"{titulo}: el porcentaje de clientes debe ser un entero entre 0 y 100.")
                porcentaje = 0
            suma_resto = suma_resto + porcentaje

        if insumos >= precio and precio > 1:
            advertencias.append(f"{titulo}: el costo de insumos es igual o mayor que el precio; "
                                "cada cliente de ese tratamiento genera pérdida.")
        tratamientos.append({"nombre": nombre_t, "precio": precio, "insumos": insumos, "porcentaje": porcentaje})

    if suma_resto > 100:
        errores.append(f"Los porcentajes de los tratamientos 2 en adelante suman {suma_resto} %. "
                       "No pueden pasar de 100 %.")
    elif len(tratamientos) > 0:
        tratamientos[0]["porcentaje"] = 100 - suma_resto     # el primero recibe el resto
    limpio["tratamientos"] = tratamientos

    # Hace falta capacidad para armar los tres escenarios
    if limpio["cabinas"] * limpio["clientes_por_terapeuta"] < 3:
        errores.append("La capacidad máxima (cabinas × clientes por terapeuta) debe ser de al menos 3 clientes.")

    return errores, limpio, advertencias


# Recibe los datos del formulario (en texto JSON), los valida y, si están bien, los activa
def configurar_spa(texto_json):
    global spa
    try:
        datos = json.loads(texto_json)
    except ValueError:
        return {"estado": "error", "mensajes": ["Los datos del spa no se pudieron leer."]}
    if type(datos) != dict:
        return {"estado": "error", "mensajes": ["Los datos del spa no se pudieron leer."]}

    errores, limpio, advertencias = validar_configuracion(datos)
    if len(errores) > 0:
        return {"estado": "error", "mensajes": errores}

    spa = limpio
    resultado = estado_spa()
    resultado["estado"] = "ok"
    resultado["advertencias"] = advertencias
    return resultado


# Borra los datos del spa (la app vuelve a quedar vacía)
def borrar_datos():
    global spa
    spa = None
    return estado_spa()


# Estado del spa activo, para que la pantalla lo muestre
def estado_spa():
    if spa == None:
        return {"hay_datos": False, "nombre": "", "es_ejemplo": False, "capacidad": 0}
    return {
        "hay_datos": True,
        "nombre": spa["nombre"],
        "es_ejemplo": spa == EJEMPLO,
        "capacidad": capacidad_maxima(spa),
    }


# Datos del spa activo y del ejemplo, para llenar el formulario
def datos_del_spa():
    return spa


def datos_del_ejemplo():
    datos = dict(EJEMPLO)
    datos["clientes"] = EJEMPLO_CLIENTES
    return datos


# =====================================================================
# 3. FUNCIONES DE CÁLCULO (reciben los datos del spa como parámetro)
# =====================================================================

# Convierte un número en pesos colombianos. Ejemplo: formato_cop(2040000) -> "$2.040.000"
def formato_cop(valor):
    texto = f"{abs(valor):,.0f}"       # separa los miles con coma: 2,040,000
    texto = texto.replace(",", ".")    # cambia la coma por punto: 2.040.000
    if valor < 0:
        return "-$" + texto
    return "$" + texto


# Igual que formato_cop, pero con signo + cuando es positivo. Ejemplo: "+$50.000"
def formato_cambio(valor):
    if valor > 0:
        return "+" + formato_cop(valor)
    return formato_cop(valor)


# Convierte un porcentaje en texto con coma decimal. Ejemplo: formato_porcentaje(45.07) -> "45,1 %"
def formato_porcentaje(valor):
    texto = f"{valor:.1f}"
    texto = texto.replace(".", ",")
    return texto + " %"


# Qué porcentaje es "parte" de "total" (0 si el total es 0, para no dividir por cero)
def porcentaje_de(parte, total):
    if total > 0:
        return parte / total * 100
    return 0


# Capacidad máxima planificada: una cabina por terapeuta
def capacidad_maxima(datos):
    return datos["cabinas"] * datos["clientes_por_terapeuta"]


# Los tres escenarios: un tercio, dos tercios y el total de la capacidad máxima
def clientes_escenarios(datos):
    capacidad = capacidad_maxima(datos)
    return [capacidad // 3, capacidad * 2 // 3, capacidad]


# Cuántos trabajadores se necesitan (siempre redondeando hacia arriba)
def personal_necesario(clientes, capacidad):
    personal = clientes // capacidad          # división entera: cuántos grupos completos hay
    if clientes % capacidad > 0:              # % da el resto: si sobran clientes...
        personal = personal + 1               # ...hace falta un trabajador más
    return personal


# Reparte los clientes entre los tratamientos del spa
def repartir_clientes(clientes, datos):
    tratamientos = datos["tratamientos"]
    reparto = [0] * len(tratamientos)
    restantes = clientes
    for i in range(1, len(tratamientos)):
        # (2 * clientes * porcentaje + 100) // 200 es "clientes * porcentaje / 100" redondeado
        # al entero más cercano (los .5 suben), usando solo números enteros
        cantidad = (2 * clientes * tratamientos[i]["porcentaje"] + 100) // 200
        if cantidad > restantes:                 # nunca repartir más clientes de los que hay
            cantidad = restantes
        reparto[i] = cantidad
        restantes = restantes - cantidad
    reparto[0] = restantes                       # el primer tratamiento recibe el resto
    return reparto                               # mismo orden que datos["tratamientos"]


# Calcula todos los resultados de una jornada y los devuelve en un diccionario
def calcular_jornada(clientes, datos):
    # Si la demanda supera la capacidad, la operación no es viable: no se calcula nada más
    if clientes > capacidad_maxima(datos):
        return {
            "clientes": clientes,
            "viable": False,
            "clientes_sin_atender": clientes - capacidad_maxima(datos),
        }

    # Personal
    terapeutas = personal_necesario(clientes, datos["clientes_por_terapeuta"])
    recepcion = personal_necesario(clientes, datos["clientes_por_recepcion"])
    costo_personal = terapeutas * datos["costo_turno_terapeuta"] + recepcion * datos["costo_turno_recepcion"]

    # Ingresos e insumos, tratamiento por tratamiento
    clientes_servicio = repartir_clientes(clientes, datos)
    ingresos_servicio = []
    ingresos_total = 0
    costo_insumos_total = 0
    for i in range(len(datos["tratamientos"])):
        t = datos["tratamientos"][i]
        ingreso = clientes_servicio[i] * t["precio"]
        insumos = clientes_servicio[i] * t["insumos"]
        ingresos_servicio.append(ingreso)
        ingresos_total = ingresos_total + ingreso
        costo_insumos_total = costo_insumos_total + insumos

    # Costos totales y ganancia
    costos_totales = costo_personal + costo_insumos_total
    ganancia = ingresos_total - costos_totales

    # Margen y utilización (evitan dividir por cero)
    margen = porcentaje_de(ganancia, ingresos_total)
    utilizacion = porcentaje_de(clientes, terapeutas * datos["clientes_por_terapeuta"])

    return {
        "clientes": clientes,
        "viable": True,
        "clientes_sin_atender": 0,
        "terapeutas": terapeutas,
        "recepcion": recepcion,
        "clientes_servicio": clientes_servicio,
        "ingresos_servicio": ingresos_servicio,
        "costo_personal": costo_personal,
        "costo_insumos": costo_insumos_total,
        "costos_totales": costos_totales,
        "ingresos_total": ingresos_total,
        "ganancia": ganancia,
        "margen": margen,
        "utilizacion": utilizacion,
    }


# =====================================================================
# 4. ANÁLISIS: PUNTO DE EQUILIBRIO, CURVA DE GANANCIA Y ESCENARIO "¿Y SI…?"
# =====================================================================

# Primer número de clientes desde el cual TODAS las jornadas hasta la capacidad dejan ganancia.
# Devuelve 0 si ni con la agenda llena hay ganancia.
def punto_de_equilibrio(datos):
    capacidad = capacidad_maxima(datos)
    n = capacidad
    while n >= 1 and calcular_jornada(n, datos)["ganancia"] >= 0:
        n = n - 1
    if n == capacidad:
        return 0                 # con la agenda llena todavía hay pérdida
    return n + 1


# Frase lista para mostrar sobre el punto de equilibrio
def texto_equilibrio(datos):
    n = punto_de_equilibrio(datos)
    if n == 0:
        return "Con estos datos la jornada no deja ganancia operativa ni con la agenda llena."
    if n == 1:
        return "Con estos datos la jornada deja ganancia operativa desde el primer cliente."
    return f"Con estos datos la jornada deja ganancia operativa a partir de {n} clientes."


# Ganancia para distintos números de clientes (para dibujar la gráfica)
def curva_ganancia(datos):
    capacidad = capacidad_maxima(datos)
    paso = (capacidad + 59) // 60          # como máximo ~60 barras
    puntos = []
    n = paso
    while n < capacidad:
        puntos.append(n)
        n = n + paso
    puntos.append(capacidad)
    curva = []
    for n in puntos:
        g = calcular_jornada(n, datos)["ganancia"]
        curva.append({"clientes": n, "ganancia": g, "ganancia_texto": formato_cop(g)})
    return curva


# Cambia un valor un cierto porcentaje (ej: variacion = 10 sube 10 %, -5 baja 5 %)
# y lo redondea al peso entero más cercano, usando solo números enteros
def aplicar_variacion(valor, variacion):
    return (2 * valor * (100 + variacion) + 100) // 200


# Copia de los datos del spa con precios, insumos y turnos modificados (para el simulador)
def ajustar_datos(datos, var_precios, var_insumos, var_turnos):
    nuevo = dict(datos)
    nuevo["costo_turno_terapeuta"] = aplicar_variacion(datos["costo_turno_terapeuta"], var_turnos)
    nuevo["costo_turno_recepcion"] = aplicar_variacion(datos["costo_turno_recepcion"], var_turnos)
    nuevo["tratamientos"] = []
    for t in datos["tratamientos"]:
        nuevo["tratamientos"].append({
            "nombre": t["nombre"],
            "precio": aplicar_variacion(t["precio"], var_precios),
            "insumos": aplicar_variacion(t["insumos"], var_insumos),
            "porcentaje": t["porcentaje"],
        })
    return nuevo


# =====================================================================
# 5. FUNCIONES QUE PREPARAN LO QUE MUESTRA LA PANTALLA
# =====================================================================

# Convierte el resultado de una jornada viable en textos listos para mostrar
def preparar_resultado(r, datos):
    tratamientos = []
    for i in range(len(datos["tratamientos"])):
        parte = porcentaje_de(r["ingresos_servicio"][i], r["ingresos_total"])
        tratamientos.append({
            "nombre": datos["tratamientos"][i]["nombre"],
            "clientes": r["clientes_servicio"][i],
            "ingresos": formato_cop(r["ingresos_servicio"][i]),
            "ingresos_num": r["ingresos_servicio"][i],
            "participacion": formato_porcentaje(parte),
            "participacion_num": parte,
        })

    # Barra de costos: ingresos, costos y ganancia medidos contra el mayor de los dos
    escala = max(r["ingresos_total"], r["costos_totales"])
    barra = {
        "personal": porcentaje_de(r["costo_personal"], escala),
        "insumos": porcentaje_de(r["costo_insumos"], escala),
        "ganancia": porcentaje_de(max(r["ganancia"], 0), escala),
    }

    return {
        "estado": "ok",
        "clientes": r["clientes"],
        "terapeutas": r["terapeutas"],
        "recepcion": r["recepcion"],
        "utilizacion": formato_porcentaje(r["utilizacion"]),
        "tratamientos": tratamientos,
        "ingresos_total": formato_cop(r["ingresos_total"]),
        "ingresos_total_num": r["ingresos_total"],
        "costo_personal": formato_cop(r["costo_personal"]),
        "costo_personal_num": r["costo_personal"],
        "costo_insumos": formato_cop(r["costo_insumos"]),
        "costo_insumos_num": r["costo_insumos"],
        "costos_totales": formato_cop(r["costos_totales"]),
        "costos_totales_num": r["costos_totales"],
        "ganancia": formato_cop(r["ganancia"]),
        "ganancia_num": r["ganancia"],
        "margen": formato_porcentaje(r["margen"]),
        "barra_costos": barra,
    }


# Lo que usa el administrador: recibe los clientes escritos en pantalla, los valida y calcula
def consultar_jornada(texto):
    if spa == None:
        return {"estado": "sin_datos"}
    texto = str(texto).strip()

    if texto == "":
        return {"estado": "error", "mensaje": "Escriba cuántos clientes espera para la jornada."}
    clientes = leer_entero(texto, False)
    if clientes == None or clientes > 1000000:
        return {"estado": "error", "mensaje": "Escriba un número entero positivo de clientes (por ejemplo: 10)."}
    if clientes == 0:
        return {"estado": "error", "mensaje": "Sin clientes no hace falta abrir turnos: no hay ingresos ni costos de la jornada."}

    r = calcular_jornada(clientes, spa)
    if r["viable"] == False:
        return {
            "estado": "no_viable",
            "clientes": clientes,
            "capacidad_maxima": capacidad_maxima(spa),
            "cabinas": spa["cabinas"],
            "clientes_por_terapeuta": spa["clientes_por_terapeuta"],
            "sin_atender": r["clientes_sin_atender"],
        }
    return preparar_resultado(r, spa)


# Punto de equilibrio y curva de ganancia del spa activo
def analisis_spa():
    if spa == None:
        return {"estado": "sin_datos"}
    return {
        "estado": "ok",
        "equilibrio": punto_de_equilibrio(spa),
        "texto_equilibrio": texto_equilibrio(spa),
        "curva": curva_ganancia(spa),
    }


# Calcula los tres escenarios con la misma función
def comparar_escenarios():
    if spa == None:
        return {"estado": "sin_datos"}
    lista = []
    escenarios = clientes_escenarios(spa)
    for i in range(len(NOMBRES_ESCENARIOS)):
        datos = preparar_resultado(calcular_jornada(escenarios[i], spa), spa)
        datos["escenario"] = NOMBRES_ESCENARIOS[i]
        lista.append(datos)
    return {"estado": "ok", "escenarios": lista}


# Simulador "¿y si…?": compara la jornada actual con una versión con precios, insumos o turnos distintos
def simular(clientes, var_precios, var_insumos, var_turnos):
    if spa == None:
        return {"estado": "sin_datos"}
    clientes = int(clientes)
    var_precios = int(round(var_precios))
    var_insumos = int(round(var_insumos))
    var_turnos = int(round(var_turnos))
    if clientes < 1 or clientes > capacidad_maxima(spa):
        return {"estado": "error", "mensaje": "Elija un número de clientes entre 1 y " + str(capacidad_maxima(spa)) + "."}
    if min(var_precios, var_insumos, var_turnos) < -50 or max(var_precios, var_insumos, var_turnos) > 100:
        return {"estado": "error", "mensaje": "Las variaciones deben estar entre -50 % y +100 %."}

    base = calcular_jornada(clientes, spa)
    otros = ajustar_datos(spa, var_precios, var_insumos, var_turnos)
    nuevo = calcular_jornada(clientes, otros)
    diferencia = nuevo["ganancia"] - base["ganancia"]
    return {
        "estado": "ok",
        "base": preparar_resultado(base, spa),
        "ajustado": preparar_resultado(nuevo, otros),
        "diferencia": formato_cambio(diferencia),
        "diferencia_num": diferencia,
        "equilibrio_base": texto_equilibrio(spa),
        "equilibrio_ajustado": texto_equilibrio(otros),
    }


# Resumen en texto plano de una jornada (para copiar y pegar en un mensaje o documento)
def texto_resumen(texto):
    d = consultar_jornada(texto)
    if d["estado"] != "ok":
        return ""
    lineas = [
        f"{spa['nombre']} · Jornada con {d['clientes']} clientes",
        f"Terapeutas: {d['terapeutas']} · Recepción/apoyo: {d['recepcion']}",
    ]
    for t in d["tratamientos"]:
        lineas.append(f"- {t['nombre']}: {t['clientes']} clientes, {t['ingresos']}")
    lineas.append(f"Ingresos totales: {d['ingresos_total']}")
    lineas.append(f"Costo de personal: {d['costo_personal']}")
    lineas.append(f"Costo de insumos: {d['costo_insumos']}")
    lineas.append(f"Ganancia operativa: {d['ganancia']} (margen {d['margen']})")
    lineas.append("Estimación hecha con los datos escritos por el spa; no incluye arriendo, servicios públicos ni impuestos.")
    return "\n".join(lineas)
