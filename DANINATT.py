import math
import random
import sys

import pygame


pygame.init()

ANCHO = 1100
ALTO = 720
FPS = 60
ESPERA_TRANSICION = 0.6
DURACION_FUNDIDO = 0.55

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Apolo 13 | Regreso a casa")
reloj = pygame.time.Clock()

FONDO = (5, 10, 23)
PANEL = (13, 25, 45)
PANEL_CLARO = (19, 38, 65)
BORDE = (42, 70, 105)
NARANJA = (255, 158, 66)
AZUL = (84, 177, 255)
VERDE = (75, 220, 160)
ROJO = (255, 93, 93)
BLANCO = (239, 245, 255)
SUAVE = (157, 177, 201)

fuente_titulo = pygame.font.SysFont("arial", 46, bold=True)
fuente_subtitulo = pygame.font.SysFont("arial", 25, bold=True)
fuente_texto = pygame.font.SysFont("arial", 20)
fuente_pequena = pygame.font.SysFont("arial", 16)
fuente_mini = pygame.font.SysFont("arial", 14)

RECURSOS = (
    ("oxigeno", "Oxígeno", VERDE, False),
    ("energia", "Energía", NARANJA, False),
    ("agua", "Agua", AZUL, False),
    ("comida", "Comida", (222, 190, 105), False),
    ("co2", "CO₂ acumulado", (193, 128, 255), True),
    ("integridad", "Integridad", (108, 200, 255), False),
    ("moral", "Moral", (255, 132, 169), False),
    ("trayectoria", "Trayectoria", (117, 222, 186), False),
)

MISIONES = [
    {
        "titulo": "Operaciones antes de la crisis",
        "fase": "11 DE ABRIL · RUMBO A LA LUNA",
        "texto": "La nave vuela con normalidad. Houston solicita agitar los tanques criogénicos y revisar la telemetría antes de continuar.",
        "telemetria": ["Bus principal: NOMINAL", "Celdas de combustible: 3", "Tanques: lectura estable"],
        "opciones": [
            {
                "texto": "Agitar los tanques y confirmar telemetría",
                "resultado": "La lectura queda verificada. La tripulación continúa con el plan de vuelo.",
                "cambios": {"energia": -3, "trayectoria": 6, "integridad": 2, "moral": 2},
            },
            {
                "texto": "Pedir una segunda revisión desde Houston",
                "resultado": "Houston confirma los datos. La comprobación extra consume tiempo y energía.",
                "cambios": {"energia": -5, "trayectoria": 4, "integridad": 1, "moral": -1},
            },
            {
                "texto": "Aplazar el mantenimiento para que la tripulación descanse",
                "resultado": "La tripulación recupera el ánimo, pero el mantenimiento queda pendiente.",
                "cambios": {"moral": 7, "trayectoria": -8, "integridad": -4, "oxigeno": -3},
            },
            {
                "texto": "Omitir la comprobación para ahorrar recursos",
                "resultado": "Se pierde información importante y queda una anomalía sin investigar.",
                "cambios": {"energia": 2, "trayectoria": -11, "integridad": -8, "errores": 1},
            },
        ],
    },
    {
        "titulo": "Explosión y pérdida de energía",
        "fase": "ALERTA · SISTEMAS DAÑADOS",
        "texto": "Una explosión sacude la nave. Dos celdas de combustible fallan, el Bus B queda sin voltaje y el oxígeno empieza a escapar.",
        "telemetria": ["Bus B: 0 V", "Celdas 1 y 3: FUERA", "Oxígeno: presión descendente"],
        "opciones": [
            {
                "texto": "Apagar cargas no esenciales y estabilizar el Bus B",
                "resultado": "La tripulación reduce el consumo. La celda restante se estabiliza y Houston coordina el rescate.",
                "cambios": {"energia": -5, "oxigeno": -3, "integridad": 5, "moral": -2},
            },
            {
                "texto": "Intentar reiniciar las celdas de combustible",
                "resultado": "El reinicio sobrecarga el sistema. Se pierde energía y aumentan los daños.",
                "cambios": {"energia": -17, "oxigeno": -8, "integridad": -14, "errores": 1},
            },
            {
                "texto": "Esperar un diagnóstico completo antes de actuar",
                "resultado": "El diagnóstico ayuda, pero la fuga continúa mientras la tripulación espera.",
                "cambios": {"energia": -8, "oxigeno": -12, "integridad": -5, "moral": -4, "errores": 1},
            },
            {
                "texto": "Ignorar las alarmas y continuar el plan original",
                "resultado": "La nave sigue perdiendo oxígeno y energía. Houston advierte que el plan ya no es viable.",
                "cambios": {"energia": -2, "oxigeno": -18, "integridad": -10, "moral": -10, "errores": 2},
            },
        ],
    },
    {
        "titulo": "El módulo lunar como bote salvavidas",
        "fase": "DECISIÓN CRÍTICA · CAMBIO DE MÓDULO",
        "texto": "El módulo de mando ya no puede sostener a la tripulación. El módulo lunar Aquarius puede ofrecer aire y energía, pero sus recursos son limitados.",
        "telemetria": ["Módulo de mando: energía crítica", "Aquarius: disponible", "Tripulación: 3 personas"],
        "opciones": [
            {
                "texto": "Trasladarse al módulo lunar y apagar lo innecesario",
                "resultado": "Aquarius queda activo como bote salvavidas. La tripulación gana soporte vital, aunque debe racionar.",
                "cambios": {"energia": 12, "oxigeno": 8, "agua": -4, "comida": -4, "integridad": 3, "moral": 6},
            },
            {
                "texto": "Permanecer en el módulo de mando",
                "resultado": "El módulo de mando pierde energía y aire. La tripulación queda en una situación muy peligrosa.",
                "cambios": {"energia": -24, "oxigeno": -15, "integridad": -13, "moral": -8, "errores": 1},
            },
            {
                "texto": "Esperar antes de activar Aquarius",
                "resultado": "La demora consume los recursos que todavía quedaban en el módulo de mando.",
                "cambios": {"energia": -9, "oxigeno": -8, "integridad": -3, "moral": -4},
            },
        ],
    },
    {
        "titulo": "Contener el dióxido de carbono",
        "fase": "SOPORTE VITAL · FILTROS INCOMPATIBLES",
        "texto": "El CO₂ sube dentro de Aquarius. Los filtros disponibles no encajan en el sistema del módulo lunar; hay que improvisar con el material a bordo.",
        "telemetria": ["CO₂: aumentando", "Filtros: incompatibles", "Energía: racionada"],
        "opciones": [
            {
                "texto": "Adaptar un filtro con cinta, bolsas y mangueras",
                "resultado": "La solución improvisada funciona. Houston guía a la tripulación paso a paso.",
                "cambios": {"co2": -28, "energia": -5, "integridad": 2, "moral": 4},
            },
            {
                "texto": "Apagar la ventilación para ahorrar energía",
                "resultado": "El ahorro eléctrico no compensa: el dióxido de carbono se acumula rápidamente.",
                "cambios": {"co2": 22, "energia": 5, "moral": -12, "integridad": -5, "errores": 1},
            },
            {
                "texto": "Racionar agua y esperar a que baje el CO₂",
                "resultado": "El racionamiento ahorra algo de energía, pero no resuelve el problema del filtro.",
                "cambios": {"co2": -10, "agua": -10, "energia": -3, "moral": -3},
            },
            {
                "texto": "Mantener la ventilación al mínimo sin adaptar el filtro",
                "resultado": "El CO₂ se vuelve peligroso y la tripulación empieza a sufrir sus efectos.",
                "cambios": {"co2": 30, "moral": -16, "integridad": -8, "errores": 2},
            },
        ],
    },
    {
        "titulo": "Corregir la trayectoria y volver a casa",
        "fase": "REGRESO · PREPARACIÓN PARA EL AMERIZAJE",
        "texto": "La nave rodeó la Luna y se dirige a la Tierra. La guía automática tiene poca energía: Houston y la tripulación deben ajustar el rumbo manualmente.",
        "telemetria": ["Motor principal: limitado", "Guía automática: baja energía", "Reentrada: por confirmar"],
        "opciones": [
            {
                "texto": "Hacer la maniobra manual con guía de Houston",
                "resultado": "La tripulación corrige el rumbo y prepara la reentrada con el procedimiento indicado.",
                "cambios": {"trayectoria": 20, "energia": -8, "integridad": -3, "oxigeno": -2},
            },
            {
                "texto": "Usar una corrección corta para conservar energía",
                "resultado": "La nave queda en rumbo de retorno con un margen de energía razonable.",
                "cambios": {"trayectoria": 12, "energia": -4, "integridad": 1, "moral": -1},
            },
            {
                "texto": "Confiar en la trayectoria actual y hacer ajustes menores",
                "resultado": "Se ahorra energía, pero la trayectoria queda con poco margen para la reentrada.",
                "cambios": {"trayectoria": 5, "energia": -2, "integridad": -1},
            },
            {
                "texto": "Omitir la corrección y entrar sin revisar el rumbo",
                "resultado": "La nave se desvía y el amerizaje queda en grave riesgo.",
                "cambios": {"trayectoria": -25, "integridad": -15, "moral": -10, "errores": 2},
            },
        ],
    },
]


class Boton:
    def __init__(self, rect, texto, indice=None):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.indice = indice
        self.activo = True

    def dibujar(self, superficie, mouse):
        encima = self.activo and self.rect.collidepoint(mouse)
        fondo = PANEL_CLARO if not encima else (34, 62, 94)
        borde = NARANJA if encima else BORDE
        pygame.draw.rect(superficie, fondo, self.rect, border_radius=9)
        pygame.draw.rect(superficie, borde, self.rect, 2, border_radius=9)
        color = BLANCO if self.activo else SUAVE
        etiqueta = fuente_pequena.render(self.texto, True, color)
        superficie.blit(etiqueta, (self.rect.x + 15, self.rect.centery - etiqueta.get_height() // 2))
        if self.indice is not None:
            tecla = fuente_mini.render(str(self.indice + 1), True, NARANJA)
            superficie.blit(tecla, (self.rect.right - 28, self.rect.centery - tecla.get_height() // 2))

    def contiene(self, posicion):
        return self.activo and self.rect.collidepoint(posicion)


def texto_envuelto(texto, fuente, ancho):
    lineas = []
    actual = ""
    for palabra in texto.split():
        prueba = palabra if not actual else actual + " " + palabra
        if fuente.size(prueba)[0] <= ancho:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def dibujar_texto(superficie, texto, fuente, color, x, y, ancho, interlineado=5, max_lineas=None):
    lineas = texto_envuelto(texto, fuente, ancho)
    if max_lineas:
        lineas = lineas[:max_lineas]
    alto = fuente.get_linesize()
    for numero, linea in enumerate(lineas):
        imagen = fuente.render(linea, True, color)
        superficie.blit(imagen, (x, y + numero * (alto + interlineado)))
    return y + len(lineas) * (alto + interlineado)


def panel(rect, titulo=None):
    pygame.draw.rect(pantalla, PANEL, rect, border_radius=13)
    pygame.draw.rect(pantalla, BORDE, rect, 1, border_radius=13)
    if titulo:
        imagen = fuente_pequena.render(titulo.upper(), True, SUAVE)
        pantalla.blit(imagen, (rect.x + 18, rect.y + 14))


def nuevo_estado():
    return {
        "oxigeno": 94,
        "energia": 92,
        "agua": 88,
        "comida": 88,
        "co2": 10,
        "integridad": 96,
        "moral": 84,
        "trayectoria": 54,
        "errores": 0,
    }


def color_recurso(valor, inverso=False):
    nivel = 100 - valor if inverso else valor
    if nivel <= 24:
        return ROJO
    if nivel <= 48:
        return NARANJA
    return VERDE


def dibujar_recursos(datos, x, y, ancho, compacto=False):
    alto_fila = 39 if compacto else 45
    alto_barra = 9
    for clave, nombre, tono, inverso in RECURSOS:
        valor = int(max(0, min(100, datos[clave])))
        color = color_recurso(valor, inverso)
        etiqueta = fuente_mini.render(nombre, True, SUAVE)
        cifra = fuente_mini.render(str(valor) + "%", True, BLANCO)
        pantalla.blit(etiqueta, (x, y))
        pantalla.blit(cifra, (x + ancho - cifra.get_width(), y))
        barra_y = y + 20
        pygame.draw.rect(pantalla, (5, 12, 24), (x, barra_y, ancho, alto_barra), border_radius=5)
        ancho_valor = int(ancho * valor / 100)
        if ancho_valor:
            pygame.draw.rect(pantalla, color, (x, barra_y, ancho_valor, alto_barra), border_radius=5)
        y += alto_fila


def dibujar_fondo(tiempo, estrellas):
    pantalla.fill(FONDO)
    pygame.draw.circle(pantalla, (8, 24, 45), (850, 90), 300)
    for x, y, radio, fase in estrellas:
        brillo = int(95 + 100 * (0.5 + 0.5 * math.sin(tiempo * 1.7 + fase)))
        pygame.draw.circle(pantalla, (brillo, min(255, brillo + 8), 255), (x, y), radio)


def reiniciar():
    return {
        "pantalla": "menu",
        "recursos": nuevo_estado(),
        "mision": 0,
        "respuesta": None,
        "mensaje": "Houston conectado. Esperando al director de misión.",
        "transicion_restante": None,
        "entrada_restante": 0.0,
    }


def avanzar_transicion(partida, dt):
    if partida["entrada_restante"] > 0:
        partida["entrada_restante"] = max(0.0, partida["entrada_restante"] - dt)

    if partida["pantalla"] != "mision" or partida["respuesta"] is None:
        return

    restante = partida["transicion_restante"]
    if restante is None:
        return

    partida["transicion_restante"] = max(0.0, restante - dt)
    if partida["transicion_restante"] > 0:
        return

    if partida["mision"] == len(MISIONES) - 1:
        partida["pantalla"] = "final"
    else:
        partida["mision"] += 1
        partida["respuesta"] = None
    partida["transicion_restante"] = None
    partida["entrada_restante"] = DURACION_FUNDIDO


def dibujar_animacion_transicion(partida):
    alpha = 0
    if partida["entrada_restante"] > 0:
        alpha = int(255 * partida["entrada_restante"] / DURACION_FUNDIDO)
    elif partida["pantalla"] == "mision" and partida["transicion_restante"] is not None:
        transcurrido = ESPERA_TRANSICION - partida["transicion_restante"]
        alpha = int(255 * min(1.0, max(0.0, transcurrido / DURACION_FUNDIDO)))

    if alpha > 0:
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((2, 6, 14, alpha))
        pantalla.blit(capa, (0, 0))


def aplicar_opcion(partida, opcion):
    datos = partida["recursos"]
    for clave, cambio in opcion["cambios"].items():
        if clave == "errores":
            datos["errores"] += cambio
        else:
            datos[clave] = max(0, min(100, datos[clave] + cambio))
    partida["respuesta"] = opcion["resultado"]
    partida["mensaje"] = opcion["resultado"]
    if any(datos[clave] <= 0 for clave in ("oxigeno", "energia", "integridad", "moral")):
        partida["pantalla"] = "fallo"
    else:
        partida["transicion_restante"] = ESPERA_TRANSICION


def calcular_resultado(datos):
    valores = [
        datos["oxigeno"],
        datos["energia"],
        datos["agua"],
        datos["comida"],
        100 - datos["co2"],
        datos["integridad"],
        datos["moral"],
        datos["trayectoria"],
    ]
    puntaje = max(0, min(100, round(sum(valores) / len(valores) - datos["errores"] * 4)))
    sobrevivio = all(datos[clave] > 0 for clave in ("oxigeno", "energia", "integridad", "moral"))
    if not sobrevivio:
        return puntaje, "MISIÓN FALLIDA", "Un sistema crítico llegó a cero antes de completar el regreso.", ROJO
    if datos["trayectoria"] < 25 or datos["integridad"] < 20:
        return puntaje, "REGRESO EN RIESGO", "La tripulación sobrevivió, pero la nave no aseguró un amerizaje controlado.", NARANJA
    if puntaje >= 78:
        return puntaje, "AMERIZAJE EXITOSO", "La tripulación regresa a casa con sistemas y recursos en buen estado.", VERDE
    if puntaje >= 55:
        return puntaje, "REGRESO CON DIFICULTADES", "La tripulación vuelve a la Tierra tras superar daños y recursos limitados.", NARANJA
    return puntaje, "SUPERVIVENCIA AL LÍMITE", "La tripulación logra regresar, pero la misión termina con muy poco margen.", NARANJA


def dibujar_menu(mouse, botones, tiempo):
    pygame.draw.circle(pantalla, (17, 47, 81), (860, 565), 205)
    pygame.draw.circle(pantalla, (26, 69, 108), (860, 565), 190)
    pygame.draw.arc(pantalla, (67, 144, 196), (660, 365, 400, 400), math.pi, 2 * math.pi, 3)
    pygame.draw.circle(pantalla, (164, 196, 220), (780, 205), 33)
    pygame.draw.circle(pantalla, (135, 165, 190), (770, 197), 7)
    pygame.draw.circle(pantalla, (135, 165, 190), (795, 211), 5)

    titulo = fuente_titulo.render("APOLO 13", True, BLANCO)
    pantalla.blit(titulo, (72, 118))
    subtitulo = fuente_subtitulo.render("REGRESO A CASA", True, NARANJA)
    pantalla.blit(subtitulo, (76, 174))
    dibujar_texto(
        pantalla,
        "Una misión de decisiones, recursos limitados y trabajo en equipo. Eres Houston: cada elección puede acercar a la tripulación a casa.",
        fuente_texto,
        SUAVE,
        78,
        235,
        470,
        8,
    )
    panel(pygame.Rect(76, 345, 460, 92), "Controles")
    dibujar_texto(
        pantalla,
        "Haz clic en una opción o usa las teclas 1–4. En el informe final, pulsa R para volver a jugar.",
        fuente_pequena,
        BLANCO,
        94,
        380,
        420,
        5,
    )
    for boton in botones:
        boton.dibujar(pantalla, mouse)
    marca = fuente_mini.render("CENTRO DE CONTROL DE MISIÓN · HOUSTON", True, SUAVE)
    pantalla.blit(marca, (76, 650))


def dibujar_mision(partida, mouse, botones):
    numero = partida["mision"]
    mision = MISIONES[numero]
    datos = partida["recursos"]

    pygame.draw.rect(pantalla, PANEL, (0, 0, ANCHO, 82))
    pygame.draw.line(pantalla, BORDE, (0, 81), (ANCHO, 81), 1)
    nombre = fuente_subtitulo.render("APOLO 13", True, BLANCO)
    pantalla.blit(nombre, (44, 18))
    fase = fuente_mini.render(mision["fase"], True, NARANJA)
    pantalla.blit(fase, (45, 50))
    estado = fuente_pequena.render("MISIÓN %d / %d" % (numero + 1, len(MISIONES)), True, SUAVE)
    pantalla.blit(estado, (ANCHO - estado.get_width() - 45, 31))
    pygame.draw.rect(pantalla, (23, 42, 66), (0, 80, ANCHO, 3))
    ancho_progreso = int((numero / len(MISIONES)) * ANCHO)
    pygame.draw.rect(pantalla, NARANJA, (0, 80, ancho_progreso, 3))

    historia = pygame.Rect(42, 108, 625, 190)
    opciones_panel = pygame.Rect(42, 312, 625, 350)
    recursos_panel = pygame.Rect(690, 108, 368, 410)
    telemetria_panel = pygame.Rect(690, 532, 368, 130)
    panel(historia)
    panel(opciones_panel, "Elige la respuesta de Houston")
    panel(recursos_panel, "Estado de la nave")
    panel(telemetria_panel, "Telemetría")

    titulo = fuente_subtitulo.render(mision["titulo"], True, BLANCO)
    pantalla.blit(titulo, (62, 125))
    dibujar_texto(pantalla, mision["texto"], fuente_pequena, SUAVE, 62, 165, 585, 6, 4)
    dibujar_recursos(datos, 710, 151, 328, compacto=True)

    if partida["respuesta"] is None and partida["pantalla"] == "mision":
        for boton in botones:
            boton.dibujar(pantalla, mouse)
        teclado = fuente_mini.render("ATAJOS: 1  2  3  4", True, SUAVE)
        pantalla.blit(teclado, (62, 627))
    else:
        respuesta = partida["respuesta"] or partida["mensaje"]
        dibujar_texto(pantalla, "REPORTE DE HOUSTON", fuente_pequena, VERDE, 64, 350, 560, 5)
        dibujar_texto(pantalla, respuesta, fuente_texto, BLANCO, 64, 384, 560, 8, 5)
        if partida["transicion_restante"] is not None:
            if partida["mision"] == len(MISIONES) - 1:
                siguiente = "INFORME FINAL"
            else:
                siguiente = "SIGUIENTE: " + MISIONES[partida["mision"] + 1]["titulo"].upper()
            restante = partida["transicion_restante"]
            progreso = 1.0 - restante / ESPERA_TRANSICION
            pantalla.blit(fuente_mini.render(siguiente, True, NARANJA), (64, 555))
            pantalla.blit(
                fuente_mini.render("CONTINUANDO EN %.1f S..." % restante, True, SUAVE),
                (64, 584),
            )
            pygame.draw.rect(pantalla, (5, 12, 24), (64, 612, 555, 8), border_radius=4)
            pygame.draw.rect(
                pantalla,
                NARANJA,
                (64, 612, int(555 * max(0.0, min(1.0, progreso))), 8),
                border_radius=4,
            )

    for indice, lectura in enumerate(mision["telemetria"]):
        y = 566 + indice * 25
        pygame.draw.circle(pantalla, VERDE if indice == 0 else NARANJA, (710, y + 7), 4)
        pantalla.blit(fuente_mini.render(lectura, True, BLANCO), (724, y))

    pygame.draw.rect(pantalla, (9, 19, 35), (0, 680, ANCHO, 40))
    pygame.draw.circle(pantalla, VERDE, (49, 700), 5)
    dibujar_texto(pantalla, partida["mensaje"], fuente_mini, SUAVE, 64, 690, 990, 0, 1)


def dibujar_final(partida, mouse, botones):
    datos = partida["recursos"]
    puntaje, titulo, descripcion, tono = calcular_resultado(datos)
    panel(pygame.Rect(70, 54, 960, 160))
    encabezado = fuente_mini.render("INFORME FINAL DE LA MISIÓN", True, NARANJA)
    pantalla.blit(encabezado, (105, 78))
    resultado = fuente_titulo.render(titulo, True, tono)
    pantalla.blit(resultado, (102, 110))
    puntuacion = fuente_subtitulo.render("PUNTUACIÓN  %d / 100" % puntaje, True, BLANCO)
    pantalla.blit(puntuacion, (750, 143))
    dibujar_texto(pantalla, descripcion, fuente_pequena, SUAVE, 105, 177, 830, 4, 1)

    panel(pygame.Rect(70, 237, 610, 394), "Recursos al cierre")
    dibujar_recursos(datos, 100, 281, 545, compacto=False)
    panel(pygame.Rect(710, 237, 320, 190), "Resumen")
    lineas = [
        "Misiones completadas: %d / %d" % (len(MISIONES), len(MISIONES)),
        "Errores críticos: %d" % datos["errores"],
        "Oxígeno restante: %d%%" % datos["oxigeno"],
        "Integridad de la nave: %d%%" % datos["integridad"],
    ]
    for indice, linea in enumerate(lineas):
        pantalla.blit(fuente_pequena.render(linea, True, BLANCO), (735, 282 + indice * 31))
    panel(pygame.Rect(710, 448, 320, 196), "Siguiente paso")
    dibujar_texto(pantalla, "¿Quieres mejorar tu resultado?", fuente_pequena, SUAVE, 735, 493, 268, 5)
    for boton in botones:
        boton.dibujar(pantalla, mouse)


def dibujar_fallo(partida, mouse, botones):
    panel(pygame.Rect(100, 105, 900, 490))
    etiqueta = fuente_mini.render("CENTRO DE CONTROL · SEÑAL PERDIDA", True, ROJO)
    pantalla.blit(etiqueta, (145, 145))
    titulo = fuente_titulo.render("MISIÓN INTERRUMPIDA", True, BLANCO)
    pantalla.blit(titulo, (145, 190))
    dibujar_texto(
        pantalla,
        partida["mensaje"],
        fuente_texto,
        SUAVE,
        147,
        265,
        790,
        8,
        4,
    )
    panel(pygame.Rect(145, 365, 800, 150), "Última telemetría")
    dibujar_recursos(partida["recursos"], 170, 403, 740, compacto=True)
    for boton in botones:
        boton.dibujar(pantalla, mouse)


def main():
    partida = reiniciar()
    estrellas = [
        (random.randrange(ANCHO), random.randrange(ALTO), random.choice((1, 1, 2)), random.random() * 6.28)
        for _ in range(95)
    ]
    botones_menu = [
        Boton((78, 476, 300, 54), "INICIAR MISIÓN"),
        Boton((78, 542, 300, 48), "SALIR"),
    ]
    botones_eleccion = []
    for indice, opcion in enumerate(MISIONES[0]["opciones"]):
        botones_eleccion.append(Boton((61, 354 + indice * 63, 586, 54), opcion["texto"], indice))
    boton_reiniciar = Boton((735, 520, 270, 34), "JUGAR DE NUEVO")
    boton_menu = Boton((735, 560, 270, 34), "VOLVER AL MENÚ")
    boton_fallo = Boton((400, 540, 300, 52), "INTENTAR DE NUEVO")
    boton_salir_final = Boton((735, 600, 270, 34), "SALIR")
    corriendo = True
    tiempo = 0.0

    while corriendo:
        dt = reloj.tick(FPS) / 1000.0
        tiempo += dt
        avanzar_transicion(partida, dt)
        mouse = pygame.mouse.get_pos()
        dibujar_fondo(tiempo, estrellas)

        if partida["pantalla"] == "menu":
            dibujar_menu(mouse, botones_menu, tiempo)
        elif partida["pantalla"] == "mision":
            mision = MISIONES[partida["mision"]]
            if partida["respuesta"] is None:
                botones_eleccion = [
                    Boton((61, 354 + indice * 63, 586, 54), opcion["texto"], indice)
                    for indice, opcion in enumerate(mision["opciones"])
                ]
                botones = botones_eleccion
            else:
                botones = []
            dibujar_mision(partida, mouse, botones)
        elif partida["pantalla"] == "final":
            dibujar_final(partida, mouse, [boton_reiniciar, boton_menu, boton_salir_final])
        else:
            dibujar_fallo(partida, mouse, [boton_fallo])

        dibujar_animacion_transicion(partida)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if partida["pantalla"] == "menu":
                        corriendo = False
                    elif partida["pantalla"] in ("final", "fallo"):
                        partida = reiniciar()
                elif partida["pantalla"] == "menu" and evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    partida = reiniciar()
                    partida["pantalla"] = "mision"
                elif partida["pantalla"] == "mision" and partida["respuesta"] is None:
                    if pygame.K_1 <= evento.key <= pygame.K_4:
                        indice = evento.key - pygame.K_1
                        opciones = MISIONES[partida["mision"]]["opciones"]
                        if indice < len(opciones):
                            aplicar_opcion(partida, opciones[indice])
                elif partida["pantalla"] == "final" and evento.key == pygame.K_r:
                    partida = reiniciar()
                    partida["pantalla"] = "mision"
                elif partida["pantalla"] == "fallo" and evento.key in (pygame.K_r, pygame.K_RETURN):
                    partida = reiniciar()
                    partida["pantalla"] = "mision"
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if partida["pantalla"] == "menu":
                    if botones_menu[0].contiene(evento.pos):
                        partida = reiniciar()
                        partida["pantalla"] = "mision"
                    elif botones_menu[1].contiene(evento.pos):
                        corriendo = False
                elif partida["pantalla"] == "mision":
                    if partida["respuesta"] is None:
                        for boton in botones_eleccion:
                            if boton.contiene(evento.pos):
                                opciones = MISIONES[partida["mision"]]["opciones"]
                                aplicar_opcion(partida, opciones[boton.indice])
                                break
                elif partida["pantalla"] == "final":
                    if boton_reiniciar.contiene(evento.pos):
                        partida = reiniciar()
                        partida["pantalla"] = "mision"
                    elif boton_menu.contiene(evento.pos):
                        partida = reiniciar()
                    elif boton_salir_final.contiene(evento.pos):
                        corriendo = False
                elif partida["pantalla"] == "fallo" and boton_fallo.contiene(evento.pos):
                    partida = reiniciar()
                    partida["pantalla"] = "mision"

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
