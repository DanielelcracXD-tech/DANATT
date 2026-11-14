"""Apolo 13 | Regreso a casa  (versión mejorada)

Novedades respecto a la versión original:
  * Tres dificultades (tiempo por misión, dureza de los cambios y desgaste de recursos).
  * Sonidos sintetizados (sin archivos externos) y tecla M para silenciar.
  * Navegación con teclado (flechas + Enter), pausa (P / Esc) y pantalla completa (F11).
  * Mapa de ruta Tierra-Luna-Tierra, barra de tiempo, alarma y viñeta de peligro.
  * Barras de recursos animadas, cifras flotantes con el efecto de cada decisión.
  * Revisión con efectos exactos de tu decisión y un dato histórico por misión.
  * Los recursos ya no se consumen mientras lees la revisión.
  * Récord guardado por dificultad, rango final y estadísticas de la partida.
"""
import array
import copy
import json
import math
import os
import random
import sys

import pygame


pygame.init()

AUDIO = False
try:
    pygame.mixer.init(22050, -16, 1, 512)
    _formato = pygame.mixer.get_init()
    AUDIO = bool(_formato) and _formato[1] == -16 and _formato[2] == 1
except pygame.error:
    AUDIO = False

ANCHO = 1100
ALTO = 720
FPS = 60
ESPERA_REVISION = 18.0

# (nombre, segundos por misión, multiplicador de cambios, factor de desgaste)
DIFICULTADES = [
    ("FÁCIL", 45.0, 1.0, 0.7),
    ("NORMAL", 35.0, 1.3, 1.0),
    ("DIFÍCIL", 25.0, 1.6, 1.3),
]
ajustes = {"dif": 1, "sonido": True}

try:
    ventana = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED | pygame.RESIZABLE)
except pygame.error:
    ventana = pygame.display.set_mode((ANCHO, ALTO))
pantalla = pygame.Surface((ANCHO, ALTO))
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
    ("salud", "Salud tripulación", (255, 112, 120), False),
    ("integridad", "Integridad", (108, 200, 255), False),
    ("moral", "Moral", (255, 132, 169), False),
    ("trayectoria", "Trayectoria", (117, 222, 186), False),
)
NOMBRES = {clave: nombre for clave, nombre, _, _ in RECURSOS}
INVERSOS = {clave: inverso for clave, _, _, inverso in RECURSOS}
INDICE_RECURSO = {clave: i for i, (clave, _, _, _) in enumerate(RECURSOS)}
CRITICOS = ("oxigeno", "energia", "salud", "integridad")

# Posición de la nave (0 = Tierra, 0.5 = Luna, 1 = Tierra) por misión.
RUTA = [0.28, 0.36, 0.44, 0.52, 0.58, 0.62, 0.76, 0.81, 0.88, 0.93, 0.97]

DATOS = [
    "La explosión del tanque de oxígeno 2 ocurrió unas 56 horas después del lanzamiento, tras agitar los tanques criogénicos.",
    "La nave estaba a más de 320 000 km de la Tierra cuando ocurrió la explosión.",
    "Aquarius estaba diseñado para dos astronautas durante unos dos días; tuvo que sostener a tres durante cerca de cuatro.",
    "El adaptador del filtro de CO₂ fue diseñado en tierra y apodado «el buzón»; la tripulación lo montó con material de a bordo.",
    "La cabina bajó hasta unos 4 °C y la tripulación racionó el agua a menos de 200 ml por persona al día.",
    "Durante el regreso, la tripulación redujo el consumo eléctrico del LM para conservar energía y agua para las maniobras finales.",
    "La corrección de rumbo se hizo encendiendo manualmente el motor de descenso de Aquarius, usando la Tierra como referencia.",
    "La orientación manual dependía de referencias visibles y de los tiempos de maniobra calculados por Houston.",
    "El procedimiento para reactivar Odyssey se escribió y probó en simuladores en tierra antes de dictarlo a la tripulación.",
    "La separación del módulo de servicio permitió observar el daño exterior antes de la reentrada.",
    "El 17 de abril de 1970 la cápsula amerizó en el Pacífico Sur; el apagón de comunicaciones duró más de lo habitual.",
]

MISIONES = [
    {
        "titulo": "Operaciones antes de la crisis",
        "fase": "11 DE ABRIL · RUMBO A LA LUNA",
        "texto": "La nave vuela con normalidad. Houston solicita agitar los tanques criogénicos y revisar la telemetría antes de continuar.",
        "telemetria": ["Bus principal: NOMINAL", "Celdas de combustible: 3", "Tanques: lectura estable"],
        "correcta": 0,
        "explicaciones": [
            "Era el procedimiento programado: comprobar los tanques ahora evita dejar una lectura anómala sin investigar.",
            "La segunda revisión confirma lo mismo, pero consume tiempo y energía sin aportar información nueva.",
            "El descanso ayuda al ánimo, pero aplazar una comprobación programada deja una tarea importante pendiente.",
            "Ahorrar energía no compensa perder telemetría y continuar sin saber si los tanques están bien.",
        ],
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
        "correcta": 0,
        "explicaciones": [
            "Reducir cargas conserva la única celda disponible y estabiliza los sistemas mientras Houston prepara el regreso.",
            "Las celdas dañadas no se pueden recuperar con un reinicio; intentarlo puede sobrecargar la que sigue funcionando.",
            "Esperar deja que el oxígeno siga escapando. Primero hay que limitar el consumo y estabilizar la nave.",
            "El plan de alunizaje ya no es seguro: ignorar las alarmas agrava la pérdida de recursos críticos.",
        ],
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
        "correcta": 0,
        "explicaciones": [
            "Aquarius puede mantener con vida a la tripulación. Apagar lo innecesario conserva sus limitados recursos.",
            "El módulo de mando perdió sus fuentes principales de energía y ya no puede sostener a la tripulación.",
            "La demora consume el poco aire y energía restantes; el módulo lunar debe activarse cuanto antes.",
        ],
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
        "correcta": 0,
        "explicaciones": [
            "La adaptación conecta el filtro disponible al sistema del módulo y elimina el CO₂, que es el peligro inmediato.",
            "Apagar la ventilación dificulta retirar el CO₂ y puede intoxicar a la tripulación aunque ahorre energía.",
            "Racionar agua no resuelve el problema del aire: el CO₂ seguirá acumulándose sin un filtro funcional.",
            "Mantener el filtro desconectado deja a la tripulación expuesta al aumento de dióxido de carbono.",
        ],
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
        "titulo": "Racionamiento y control térmico",
        "fase": "MÓDULO LUNAR · AGUA Y TEMPERATURA",
        "texto": "Aquarius está frío y el agua restante también sostiene sistemas críticos. Hay que mantener lo indispensable sin agotar las reservas.",
        "telemetria": ["Agua: reserva limitada", "Calefacción: consumo alto", "Cabina: temperatura baja"],
        "correcta": 0,
        "explicaciones": [
            "Apagar cargas no esenciales y racionar agua conserva energía y soporte vital sin dejar la cabina totalmente fría.",
            "Mantener todos los equipos encendidos consume energía y agua que la tripulación necesitará para el regreso.",
            "Apagar toda la calefacción ahorra energía, pero el frío extremo perjudica a la tripulación y sus operaciones.",
            "El agua no es ilimitada: gastarla sin un plan pone en riesgo los sistemas que dependen de ella.",
        ],
        "opciones": [
            {
                "texto": "Apagar cargas no esenciales y racionar agua",
                "resultado": "La tripulación conserva consumibles y mantiene solo los sistemas necesarios.",
                "cambios": {"energia": 5, "agua": -3, "comida": -2, "integridad": 1, "moral": -2},
            },
            {
                "texto": "Mantener todos los sistemas a potencia normal",
                "resultado": "La cabina está más cómoda, pero las reservas caen con rapidez.",
                "cambios": {"energia": -14, "agua": -10, "comida": -3, "moral": 2, "errores": 1},
            },
            {
                "texto": "Apagar toda la calefacción para conservar energía",
                "resultado": "El ahorro no compensa el frío extremo que afecta a la tripulación y al equipo.",
                "cambios": {"energia": 8, "salud": -12, "moral": -10, "integridad": -4, "errores": 1},
            },
            {
                "texto": "Usar el agua sin racionamiento",
                "resultado": "El consumo innecesario deja a la nave sin el margen previsto para el regreso.",
                "cambios": {"agua": -22, "energia": -5, "salud": -5, "moral": -4, "errores": 2},
            },
        ],
    },
    {
        "titulo": "Turnos de descanso y vigilancia médica",
        "fase": "SUPERVIVENCIA · FATIGA DE LA TRIPULACIÓN",
        "texto": "La tripulación lleva días durmiendo poco y trabajando en una cabina fría. Houston necesita que sigan alerta sin gastar los recursos que quedan.",
        "telemetria": ["Salud: bajo estrés", "Cabina: fría", "Regreso: aún en curso"],
        "correcta": 0,
        "explicaciones": [
            "Los turnos permiten descansar sin dejar la nave sin vigilancia y ayudan a detectar pronto un deterioro de salud.",
            "Trabajar sin dormir aumenta los errores humanos y empeora la salud justo cuando se necesitan maniobras precisas.",
            "Si todos duermen a la vez nadie vigila los sistemas ni puede responder rápidamente a una alarma.",
            "La calefacción máxima mejora el confort, pero consume agua y energía necesarias para el soporte vital.",
        ],
        "opciones": [
            {
                "texto": "Alternar descansos y revisar los signos vitales por turnos",
                "resultado": "La tripulación recupera fuerzas mientras alguien permanece atento a los sistemas.",
                "cambios": {"salud": 7, "moral": 5, "agua": -2, "comida": -2, "energia": -2},
            },
            {
                "texto": "Mantener a todos trabajando para adelantar el regreso",
                "resultado": "La falta de descanso aumenta el agotamiento y el riesgo de error.",
                "cambios": {"salud": -12, "moral": -12, "errores": 1},
            },
            {
                "texto": "Dejar que los tres duerman al mismo tiempo",
                "resultado": "La tripulación descansa, pero no queda nadie supervisando la nave.",
                "cambios": {"salud": -8, "moral": 3, "integridad": -5, "errores": 1},
            },
            {
                "texto": "Mantener la calefacción al máximo durante todo el descanso",
                "resultado": "El calor ayuda, pero el consumo agota recursos esenciales.",
                "cambios": {"salud": 3, "energia": -12, "agua": -5, "errores": 1},
            },
        ],
    },
    {
        "titulo": "Corregir la trayectoria hacia la Tierra",
        "fase": "REGRESO · PREPARACIÓN PARA EL AMERIZAJE",
        "texto": "La nave rodeó la Luna, pero la trayectoria debe apuntar con precisión al corredor de reentrada. La guía automática tiene poca energía.",
        "telemetria": ["Retorno libre: activo", "Guía automática: baja energía", "Corrección: pendiente"],
        "correcta": 0,
        "explicaciones": [
            "La maniobra manual guiada por Houston corrige el rumbo y permite preparar la reentrada con datos y pasos verificados.",
            "Una corrección corta ahorra energía, pero puede no corregir lo suficiente la trayectoria para una reentrada segura.",
            "Confiar en un rumbo no confirmado deja poco margen para corregir antes de llegar a la Tierra.",
            "Omitir la corrección aumenta el riesgo de entrar con un ángulo de reentrada peligroso.",
        ],
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
    {
        "titulo": "Confirmar la orientación manual",
        "fase": "NAVEGACIÓN · REFERENCIAS VISUALES",
        "texto": "La computadora guía está apagada para ahorrar energía. Antes de continuar, la tripulación debe comprobar la orientación de la nave con referencias visibles.",
        "telemetria": ["Guía: apagada", "Tierra: visible", "Actitud: por confirmar"],
        "correcta": 0,
        "explicaciones": [
            "Comparar la Tierra y las referencias acordadas con Houston permite confirmar que la nave apunta al corredor correcto.",
            "La guía automática está apagada y no puede confirmar una maniobra; intentar encenderla también gasta batería.",
            "Girar con los propulsores sin una referencia clara consume combustible y puede desestabilizar la nave.",
            "Continuar sin verificar la actitud deja que un pequeño error se convierta en una desviación peligrosa.",
        ],
        "opciones": [
            {
                "texto": "Alinear la nave con la Tierra y confirmar los datos con Houston",
                "resultado": "La referencia visual confirma la actitud y Houston valida el siguiente paso.",
                "cambios": {"trayectoria": 12, "energia": -3, "integridad": 2, "moral": 1},
            },
            {
                "texto": "Encender la guía automática aunque tenga poca batería",
                "resultado": "El sistema consume energía sin completar una lectura fiable.",
                "cambios": {"energia": -8, "trayectoria": -7, "errores": 1},
            },
            {
                "texto": "Girar rápidamente con los propulsores de actitud",
                "resultado": "La nave cambia de orientación, pero queda fuera del punto de referencia.",
                "cambios": {"energia": -7, "trayectoria": -5, "integridad": -6, "errores": 1},
            },
            {
                "texto": "Seguir sin comprobar la orientación",
                "resultado": "La incertidumbre de rumbo se mantiene durante la aproximación.",
                "cambios": {"trayectoria": -16, "moral": -5, "errores": 2},
            },
        ],
    },
    {
        "titulo": "Reactivar el módulo de mando",
        "fase": "PREPARACIÓN · CAMBIO AL MÓDULO DE MANDO",
        "texto": "Antes de regresar a la atmósfera, la tripulación debe reactivar Odyssey con las baterías limitadas y comprobar los sistemas esenciales.",
        "telemetria": ["Baterías: carga limitada", "Escudo térmico: por verificar", "Módulo lunar: aún acoplado"],
        "correcta": 0,
        "explicaciones": [
            "La lista de Houston prioriza los sistemas vitales y evita una sobrecarga antes de abandonar Aquarius.",
            "Encender todo simultáneamente agota las baterías y puede provocar fallos justo antes de la reentrada.",
            "Separar Aquarius antes de confirmar el módulo de mando elimina el soporte vital de respaldo demasiado pronto.",
            "Sin verificar el escudo térmico no se sabe si la cápsula puede soportar el calor de la reentrada.",
        ],
        "opciones": [
            {
                "texto": "Seguir la lista de Houston y activar los sistemas por etapas",
                "resultado": "Odyssey vuelve a estar operativo sin gastar de golpe sus baterías.",
                "cambios": {"energia": -5, "integridad": 5, "trayectoria": 3, "oxigeno": -1},
            },
            {
                "texto": "Encender todos los sistemas al mismo tiempo",
                "resultado": "La demanda supera el margen de las baterías y aparecen fallos eléctricos.",
                "cambios": {"energia": -18, "integridad": -12, "moral": -4, "errores": 1},
            },
            {
                "texto": "Separar Aquarius antes de revisar Odyssey",
                "resultado": "La tripulación pierde el soporte vital de respaldo antes de confirmar la cápsula.",
                "cambios": {"oxigeno": -10, "integridad": -14, "salud": -8, "errores": 1},
            },
            {
                "texto": "Omitir la revisión del escudo térmico",
                "resultado": "La cápsula se prepara para entrar sin confirmar su protección térmica.",
                "cambios": {"integridad": -22, "salud": -10, "trayectoria": -5, "errores": 2},
            },
        ],
    },
    {
        "titulo": "Separación de los módulos",
        "fase": "LISTA DE REENTRADA · SECUENCIA DE SEPARACIÓN",
        "texto": "Odyssey ya está reactivado. Houston pide separar el módulo de servicio y comprobar la cápsula antes de soltar Aquarius y comenzar la reentrada.",
        "telemetria": ["Odyssey: operativo", "Módulo de servicio: dañado", "Aquarius: soporte vital activo"],
        "correcta": 0,
        "explicaciones": [
            "Separar primero el módulo de servicio permite observar los daños; Aquarius se mantiene como respaldo hasta completar la lista.",
            "Soltar Aquarius antes de confirmar Odyssey elimina el soporte vital de reserva demasiado pronto.",
            "El módulo de servicio no debe permanecer unido durante la reentrada; su daño compromete la secuencia.",
            "Separar varios módulos sin confirmar cada paso puede afectar la orientación y la seguridad de la cápsula.",
        ],
        "opciones": [
            {
                "texto": "Separar el módulo de servicio y verificar Odyssey antes de soltar Aquarius",
                "resultado": "La tripulación confirma el daño y completa la secuencia de separación de forma controlada.",
                "cambios": {"integridad": 6, "trayectoria": 3, "energia": -2, "salud": 1},
            },
            {
                "texto": "Soltar Aquarius antes de comprobar el módulo de mando",
                "resultado": "La tripulación pierde su último soporte vital de respaldo antes de estar lista.",
                "cambios": {"oxigeno": -12, "salud": -10, "integridad": -8, "errores": 1},
            },
            {
                "texto": "Mantener el módulo de servicio unido durante la reentrada",
                "resultado": "La masa y los daños del módulo comprometen la configuración de entrada.",
                "cambios": {"integridad": -20, "trayectoria": -12, "salud": -6, "errores": 1},
            },
            {
                "texto": "Separar ambos módulos a la vez sin confirmar la secuencia",
                "resultado": "La cápsula pierde estabilidad y Houston no puede verificar el resultado a tiempo.",
                "cambios": {"integridad": -18, "trayectoria": -10, "moral": -8, "errores": 2},
            },
        ],
    },
    {
        "titulo": "Reentrada y amerizaje",
        "fase": "ÚLTIMA FASE · REGRESO A LA TIERRA",
        "texto": "Odyssey está listo para separarse de Aquarius. La tripulación debe ejecutar la secuencia de reentrada y desplegar los paracaídas en el momento correcto.",
        "telemetria": ["Escudo térmico: confirmado", "Ángulo de reentrada: crítico", "Recuperación: en espera"],
        "correcta": 0,
        "explicaciones": [
            "La secuencia verificada mantiene el escudo térmico orientado y reserva los paracaídas para el descenso.",
            "Separar los módulos fuera de secuencia puede dejar la cápsula sin soporte o interferir con su orientación.",
            "Un ángulo demasiado pronunciado eleva el calentamiento y las fuerzas sobre la cápsula.",
            "Sin desplegar los paracaídas la cápsula impactaría el océano a una velocidad peligrosa.",
        ],
        "opciones": [
            {
                "texto": "Confirmar orientación y seguir la secuencia de reentrada",
                "resultado": "La cápsula mantiene el rumbo, atraviesa la atmósfera y despliega los paracaídas.",
                "cambios": {"trayectoria": 8, "integridad": 5, "energia": -2, "salud": 2},
            },
            {
                "texto": "Separar los módulos sin confirmar la orientación",
                "resultado": "La cápsula pierde estabilidad y queda con poco margen de corrección.",
                "cambios": {"trayectoria": -12, "integridad": -12, "salud": -5, "errores": 1},
            },
            {
                "texto": "Entrar con un ángulo demasiado pronunciado",
                "resultado": "El calor y la aceleración comprometen la estructura y el escudo térmico.",
                "cambios": {"integridad": -28, "salud": -20, "trayectoria": -18, "errores": 2},
            },
            {
                "texto": "Omitir la secuencia de paracaídas",
                "resultado": "La cápsula llega al océano sin la desaceleración necesaria para un amerizaje seguro.",
                "cambios": {"integridad": -30, "salud": -25, "trayectoria": -20, "errores": 2},
            },
        ],
    },
]


# ----------------------------------------------------------------------------
# Sonido (sintetizado)
# ----------------------------------------------------------------------------
def crear_tono(frecuencias, duracion, volumen=0.25, cuadrada=False):
    tasa = pygame.mixer.get_init()[0]
    total = int(tasa * duracion)
    tramo = max(1, total // len(frecuencias))
    muestras = array.array("h")
    for frecuencia in frecuencias:
        for i in range(tramo):
            onda = math.sin(2 * math.pi * frecuencia * i / tasa)
            if cuadrada:
                onda = 1.0 if onda >= 0 else -1.0
            envolvente = max(0.0, min(1.0, i / 200.0, (tramo - i) / (tasa * 0.02)))
            muestras.append(int(32767 * volumen * onda * envolvente))
    return pygame.mixer.Sound(buffer=muestras.tobytes())


SONIDOS = {}
if AUDIO:
    try:
        SONIDOS = {
            "clic": crear_tono([660], 0.05, 0.18),
            "bien": crear_tono([523, 659, 784], 0.32, 0.22),
            "neutro": crear_tono([440, 494], 0.2, 0.18),
            "mal": crear_tono([196, 147], 0.4, 0.13, True),
            "alarma": crear_tono([880, 660], 0.3, 0.10, True),
            "tick": crear_tono([1200], 0.04, 0.12),
            "exito": crear_tono([523, 659, 784, 1047], 0.8, 0.22),
            "fallo": crear_tono([220, 185, 147, 110], 0.9, 0.13, True),
        }
    except (pygame.error, ValueError):
        SONIDOS = {}


def sonar(nombre):
    if ajustes["sonido"] and nombre in SONIDOS:
        SONIDOS[nombre].play()


# ----------------------------------------------------------------------------
# Récords
# ----------------------------------------------------------------------------
try:
    RUTA_RECORD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apolo13_record.json")
except NameError:
    RUTA_RECORD = "apolo13_record.json"


def cargar_records():
    try:
        with open(RUTA_RECORD, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return datos if isinstance(datos, dict) else {}
    except (OSError, ValueError):
        return {}


RECORDS = cargar_records()


def guardar_record(nombre, puntaje):
    anterior = RECORDS.get(nombre, 0)
    if puntaje <= anterior:
        return False
    RECORDS[nombre] = puntaje
    try:
        with open(RUTA_RECORD, "w", encoding="utf-8") as archivo:
            json.dump(RECORDS, archivo)
    except OSError:
        pass
    return True


# ----------------------------------------------------------------------------
# Lógica
# ----------------------------------------------------------------------------
def crear_misiones_partida():
    misiones = copy.deepcopy(MISIONES)
    posicion_anterior = None
    for numero, mision in enumerate(misiones):
        opciones = mision["opciones"]
        explicaciones = mision["explicaciones"]
        correcta_original = mision["correcta"]
        emergencia_original = mision.get("emergencia", len(opciones) - 1)
        posiciones = [i for i in range(len(opciones)) if i != posicion_anterior]
        posicion_correcta = random.choice(posiciones)
        orden = [i for i in range(len(opciones)) if i != correcta_original]
        random.shuffle(orden)
        orden.insert(posicion_correcta, correcta_original)
        mision["opciones"] = [opciones[i] for i in orden]
        mision["explicaciones"] = [explicaciones[i] for i in orden]
        mision["correcta"] = posicion_correcta
        mision["emergencia"] = orden.index(emergencia_original)
        mision["dato"] = DATOS[numero] if numero < len(DATOS) else ""
        posicion_anterior = posicion_correcta
    return misiones


def nuevo_estado():
    return {
        "oxigeno": 78, "energia": 72, "agua": 70, "comida": 74, "co2": 20,
        "salud": 92, "integridad": 84, "moral": 72, "trayectoria": 38, "errores": 0,
    }


def tiempo_mision():
    return DIFICULTADES[ajustes["dif"]][1]


def reiniciar():
    recursos = nuevo_estado()
    return {
        "pantalla": "menu",
        "recursos": recursos,
        "visibles": dict(recursos),
        "nave": RUTA[0],
        "misiones": crear_misiones_partida(),
        "mision": 0,
        "respuesta": None,
        "indice_elegido": None,
        "mensaje": "Houston conectado. Esperando al director de misión.",
        "revision_restante": None,
        "fallo_pendiente": False,
        "tiempo_restante": tiempo_mision(),
        "tiempo_agotado": False,
        "filtro_adaptado": False,
        "deltas": [],
        "flotantes": [],
        "foco": None,
        "pausa": False,
        "correctas": 0,
        "agotados": 0,
        "tiempo_juego": 0.0,
        "shake": 0.0,
        "ultimo_tick": None,
        "ultima_alarma": 0.0,
        "nuevo_record": False,
    }


def nueva_partida():
    partida = reiniciar()
    partida["pantalla"] = "mision"
    sonar("clic")
    return partida


def hay_critico(datos):
    return any(datos[c] < 15 for c in CRITICOS) or datos["co2"] > 85


def calcular_resultado(datos):
    valores = [
        datos["oxigeno"], datos["energia"], datos["agua"], datos["comida"],
        100 - datos["co2"], datos["salud"], datos["integridad"], datos["moral"], datos["trayectoria"],
    ]
    puntaje = max(0, min(100, round(sum(valores) / len(valores) - datos["errores"] * 4)))
    sobrevivio = all(datos[clave] > 0 for clave in CRITICOS)
    if not sobrevivio or datos["trayectoria"] < 25 or datos["integridad"] < 20 or puntaje < 38:
        return puntaje, "MISIÓN FALLIDA", "La nave no logró sostener a la tripulación ni asegurar una reentrada viable.", ROJO
    if puntaje >= 78:
        return puntaje, "AMERIZAJE EXITOSO", "La tripulación regresa a casa con sistemas y recursos en buen estado.", VERDE
    if puntaje >= 55:
        return puntaje, "REGRESO CON DIFICULTADES", "La tripulación vuelve a la Tierra tras superar daños y recursos limitados.", NARANJA
    return puntaje, "SUPERVIVENCIA AL LÍMITE", "La tripulación logra regresar, pero la misión termina con muy poco margen.", NARANJA


def rango(puntaje, exito):
    if not exito:
        return "Aspirante"
    if puntaje >= 90:
        return "Director de vuelo"
    if puntaje >= 78:
        return "Comandante"
    if puntaje >= 55:
        return "Piloto"
    return "Cadete"


def registrar_final(partida):
    puntaje, titulo, _, _ = calcular_resultado(partida["recursos"])
    if titulo != "MISIÓN FALLIDA":
        partida["nuevo_record"] = guardar_record(DIFICULTADES[ajustes["dif"]][0], puntaje)
        sonar("exito")
    else:
        sonar("fallo")


def aplicar_opcion(partida, opcion, indice, por_tiempo=False):
    datos = partida["recursos"]
    multiplicador = DIFICULTADES[ajustes["dif"]][2]
    deltas = []
    for clave, cambio in opcion["cambios"].items():
        if clave == "errores":
            datos["errores"] += cambio
            deltas.append((clave, cambio))
        else:
            antes = datos[clave]
            datos[clave] = max(0, min(100, antes + cambio * multiplicador))
            deltas.append((clave, datos[clave] - antes))
    mision = partida["misiones"][partida["mision"]]
    partida["deltas"] = deltas
    partida["respuesta"] = opcion["resultado"]
    partida["mensaje"] = opcion["resultado"]
    partida["indice_elegido"] = indice
    partida["revision_restante"] = ESPERA_REVISION
    partida["tiempo_agotado"] = por_tiempo
    partida["foco"] = None
    if partida["mision"] == 3 and indice == mision["correcta"]:
        partida["filtro_adaptado"] = True
    if por_tiempo:
        partida["agotados"] += 1
    elif indice == mision["correcta"]:
        partida["correctas"] += 1
    partida["fallo_pendiente"] = any(datos[clave] <= 0 for clave in CRITICOS)
    if partida["fallo_pendiente"]:
        partida["mensaje"] = "La misión se interrumpió: un recurso crítico llegó a cero."

    if "errores" in opcion["cambios"] or por_tiempo:
        sonar("mal")
        partida["shake"] = 0.45
    elif indice == mision["correcta"]:
        sonar("bien")
    else:
        sonar("neutro")


def continuar_revision(partida):
    if partida["fallo_pendiente"]:
        partida["pantalla"] = "fallo"
        sonar("fallo")
    elif partida["mision"] == len(partida["misiones"]) - 1:
        partida["pantalla"] = "final"
        registrar_final(partida)
    else:
        partida["mision"] += 1
        partida["respuesta"] = None
        partida["indice_elegido"] = None
        partida["mensaje"] = "Houston: " + partida["misiones"][partida["mision"]]["titulo"] + "."
        partida["tiempo_restante"] = tiempo_mision()
        partida["tiempo_agotado"] = False
        partida["ultimo_tick"] = None
        for clave, valor in partida["deltas"]:
            if clave in INDICE_RECURSO and abs(valor) >= 1:
                bueno = (valor > 0) != INVERSOS[clave]
                partida["flotantes"].append({
                    "txt": "%+d" % round(valor),
                    "color": VERDE if bueno else ROJO,
                    "x": 710 + 328 - 82,
                    "y": 151 + INDICE_RECURSO[clave] * 39,
                    "vida": 1.8,
                })
    partida["revision_restante"] = None
    partida["fallo_pendiente"] = False


def actualizar_reloj_mision(partida, dt):
    if partida["pantalla"] != "mision" or partida["pausa"]:
        return

    datos = partida["recursos"]
    visibles = partida["visibles"]

    # Animación suave de barras, flotantes y nave (solo fuera de la revisión).
    if partida["respuesta"] is None:
        suavizado = min(1.0, dt * 5)
        for clave in visibles:
            visibles[clave] += (datos[clave] - visibles[clave]) * suavizado
        destino = RUTA[min(partida["mision"], len(RUTA) - 1)]
        partida["nave"] += (destino - partida["nave"]) * min(1.0, dt * 2.5)
    for flotante in partida["flotantes"]:
        flotante["vida"] -= dt
    partida["flotantes"] = [f for f in partida["flotantes"] if f["vida"] > 0]
    partida["shake"] = max(0.0, partida["shake"] - dt)

    if partida["respuesta"] is not None:
        return  # Durante la revisión los recursos no se consumen.

    fase = partida["mision"]
    if fase == 0:
        tasas = {"oxigeno": 0.045, "energia": 0.06, "agua": 0.027, "comida": 0.015, "co2": 0.008}
    elif fase == 1:
        tasas = {"oxigeno": 0.20, "energia": 0.28, "agua": 0.06, "comida": 0.035, "co2": 0.09}
    elif fase <= 3:
        tasas = {"oxigeno": 0.14, "energia": 0.19, "agua": 0.08, "comida": 0.055, "co2": 0.22}
    else:
        tasas = {"oxigeno": 0.12, "energia": 0.16, "agua": 0.07, "comida": 0.05, "co2": 0.18}
    if partida["filtro_adaptado"] and fase >= 3:
        tasas["co2"] = 0.02
    desgaste = DIFICULTADES[ajustes["dif"]][3]
    tasas = {clave: valor * desgaste for clave, valor in tasas.items()}

    for recurso in ("oxigeno", "energia", "agua", "comida"):
        datos[recurso] = max(0, datos[recurso] - dt * tasas[recurso])
    datos["co2"] = min(100, datos["co2"] + dt * tasas["co2"])

    if datos["co2"] > 55:
        datos["salud"] = max(0, datos["salud"] - dt * (0.015 + (datos["co2"] - 55) * 0.004))
    if datos["oxigeno"] < 20:
        datos["salud"] = max(0, datos["salud"] - dt * 0.12)
    if datos["agua"] <= 0:
        datos["salud"] = max(0, datos["salud"] - dt * 0.08)
    if datos["comida"] <= 0 or datos["salud"] < 35:
        datos["moral"] = max(0, datos["moral"] - dt * 0.08)
    if datos["energia"] < 12:
        datos["integridad"] = max(0, datos["integridad"] - dt * 0.05)

    partida["tiempo_restante"] = max(0.0, partida["tiempo_restante"] - dt)
    partida["tiempo_juego"] += dt

    if any(datos[clave] <= 0 for clave in CRITICOS):
        partida["pantalla"] = "fallo"
        partida["mensaje"] = "La tripulación perdió un sistema crítico mientras esperaba una decisión."
        sonar("fallo")
        return

    partida["ultima_alarma"] -= dt
    if hay_critico(datos) and partida["ultima_alarma"] <= 0:
        sonar("alarma")
        partida["ultima_alarma"] = 2.5
    entero = math.ceil(partida["tiempo_restante"])
    if 0 < entero <= 5 and entero != partida["ultimo_tick"]:
        sonar("tick")
    partida["ultimo_tick"] = entero

    if partida["tiempo_restante"] <= 0:
        mision = partida["misiones"][partida["mision"]]
        indice = mision["emergencia"]
        aplicar_opcion(partida, mision["opciones"][indice], indice, por_tiempo=True)


def actualizar_revision(partida, dt):
    if partida["pantalla"] != "mision" or partida["respuesta"] is None or partida["pausa"]:
        return
    restante = partida["revision_restante"]
    if restante is None:
        return
    partida["revision_restante"] = max(0.0, restante - dt)
    if partida["revision_restante"] <= 0:
        continuar_revision(partida)


# ----------------------------------------------------------------------------
# Dibujo
# ----------------------------------------------------------------------------
class Boton:
    def __init__(self, rect, texto, indice=None):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.indice = indice
        self.activo = True

    def dibujar(self, superficie, mouse, foco=False):
        encima = self.activo and (foco or self.rect.collidepoint(mouse))
        fondo = (34, 62, 94) if encima else PANEL_CLARO
        borde = NARANJA if encima else BORDE
        pygame.draw.rect(superficie, fondo, self.rect, border_radius=9)
        pygame.draw.rect(superficie, borde, self.rect, 2, border_radius=9)
        color = BLANCO if self.activo else SUAVE
        margen = 15 + (40 if self.indice is not None else 15)
        lineas = texto_envuelto(self.texto, fuente_pequena, self.rect.width - margen)[:2]
        alto_linea = fuente_pequena.get_linesize()
        y = self.rect.centery - (len(lineas) * alto_linea) // 2
        for linea in lineas:
            etiqueta = fuente_pequena.render(linea, True, color)
            superficie.blit(etiqueta, (self.rect.x + 15, y))
            y += alto_linea
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


def color_recurso(valor, inverso=False):
    nivel = 100 - valor if inverso else valor
    if nivel <= 24:
        return ROJO
    if nivel <= 48:
        return NARANJA
    return VERDE


def dibujar_recursos(datos, x, y, ancho, compacto=False, recursos=RECURSOS):
    alto_fila = 39 if compacto else 45
    alto_barra = 9
    pulso = 0.78 + 0.22 * math.sin(pygame.time.get_ticks() / 1000.0 * 8)
    for clave, nombre, tono, inverso in recursos:
        valor = int(max(0, min(100, datos[clave])))
        color = color_recurso(valor, inverso)
        if color == ROJO:
            color = tuple(int(c * pulso) for c in color)
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


def crear_vineta():
    superficie = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    for i in range(40):
        alfa = int(160 * (1 - i / 40) ** 2)
        pygame.draw.rect(superficie, (255, 40, 40, alfa), (i, i, ANCHO - 2 * i, ALTO - 2 * i), 1)
    return superficie


VINETA = crear_vineta()


def texto_deltas(deltas):
    partes = []
    for clave, valor in deltas:
        if clave == "errores":
            partes.append("Error crítico +%d" % valor)
        else:
            entero = int(round(valor))
            if entero:
                partes.append("%s %+d" % (NOMBRES[clave], entero))
    return " · ".join(partes) if partes else "Sin cambios relevantes"


def dibujar_revision(partida):
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((2, 6, 14, 235))
    pantalla.blit(overlay, (0, 0))

    ventana_rect = pygame.Rect(48, 34, 1004, 652)
    panel(ventana_rect)
    mision = partida["misiones"][partida["mision"]]
    recomendada = mision["correcta"]
    seleccionada = partida["indice_elegido"]
    encabezado = fuente_subtitulo.render(
        "REVISIÓN DE MISIÓN %d / %d" % (partida["mision"] + 1, len(partida["misiones"])), True, NARANJA)
    pantalla.blit(encabezado, (78, 55))

    if partida["tiempo_agotado"]:
        estado = "TIEMPO AGOTADO · SE APLICÓ UNA ACCIÓN DE EMERGENCIA"
        color_estado = ROJO
    elif seleccionada == recomendada:
        estado = "ELEGISTE LA RESPUESTA RECOMENDADA"
        color_estado = VERDE
    else:
        estado = "TU ELECCIÓN FUE OTRA; REVISA POR QUÉ"
        color_estado = NARANJA
    pantalla.blit(fuente_pequena.render(estado, True, color_estado), (78, 88))

    caja_correcta = pygame.Rect(75, 118, 950, 108)
    pygame.draw.rect(pantalla, (13, 51, 47), caja_correcta, border_radius=9)
    pygame.draw.rect(pantalla, VERDE, caja_correcta, 2, border_radius=9)
    pantalla.blit(fuente_mini.render("RESPUESTA RECOMENDADA", True, VERDE), (92, 128))
    correcta = mision["opciones"][recomendada]
    y = dibujar_texto(pantalla, correcta["texto"], fuente_pequena, BLANCO, 92, 151, 915, 3, 1)
    dibujar_texto(pantalla, "Por qué: " + mision["explicaciones"][recomendada],
                  fuente_mini, SUAVE, 92, y + 2, 915, 2, 2)

    pantalla.blit(fuente_pequena.render("POR QUÉ LAS DEMÁS OPCIONES NO SON RECOMENDABLES", True, SUAVE), (78, 242))
    y = 270
    for indice, opcion in enumerate(mision["opciones"]):
        if indice == recomendada:
            continue
        alto = 92
        rect = pygame.Rect(75, y, 950, alto)
        elegido = indice == seleccionada
        tono = NARANJA if elegido else BORDE
        pygame.draw.rect(pantalla, (17, 31, 51), rect, border_radius=8)
        pygame.draw.rect(pantalla, tono, rect, 1, border_radius=8)
        etiqueta = "TU ELECCIÓN" if elegido else "ALTERNATIVA %d" % (indice + 1)
        pantalla.blit(fuente_mini.render(etiqueta, True, tono), (92, y + 7))
        texto_y = dibujar_texto(pantalla, opcion["texto"], fuente_mini, BLANCO, 92, y + 26, 915, 2, 1)
        dibujar_texto(pantalla, "Por qué no es la mejor: " + mision["explicaciones"][indice],
                      fuente_mini, SUAVE, 92, texto_y + 1, 915, 2, 2)
        y += alto + 8

    efectos = "EFECTOS DE TU DECISIÓN:  " + texto_deltas(partida["deltas"])
    dibujar_texto(pantalla, efectos, fuente_mini, AZUL, 78, 574, 940, 0, 1)

    caja_dato = pygame.Rect(75, 596, 950, 48)
    pygame.draw.rect(pantalla, (14, 30, 52), caja_dato, border_radius=8)
    pygame.draw.rect(pantalla, AZUL, caja_dato, 1, border_radius=8)
    dibujar_texto(pantalla, "DATO HISTÓRICO: " + mision.get("dato", ""), fuente_mini, SUAVE, 90, 603, 920, 2, 2)

    restante = max(0, math.ceil(partida["revision_restante"] or 0))
    instruccion = "Enter, espacio o clic para continuar · el análisis se cierra en %d s" % restante
    pantalla.blit(fuente_mini.render(instruccion, True, SUAVE), (78, 656))


def dibujar_ruta(partida, tiempo):
    x0, x1, y = 82, 640, 281
    pygame.draw.line(pantalla, BORDE, (x0, y), (x1, y), 2)
    nave_x = x0 + (x1 - x0) * partida["nave"]
    pygame.draw.line(pantalla, NARANJA, (x0, y), (int(nave_x), y), 2)
    pygame.draw.circle(pantalla, AZUL, (x0, y), 8)
    pygame.draw.circle(pantalla, AZUL, (x1, y), 8)
    luna_x = x0 + (x1 - x0) * 0.5
    pygame.draw.circle(pantalla, (164, 196, 220), (int(luna_x), y), 6)
    radio = 5 + int(2 * (0.5 + 0.5 * math.sin(tiempo * 5)))
    pygame.draw.circle(pantalla, BLANCO, (int(nave_x), y), radio)
    pygame.draw.circle(pantalla, NARANJA, (int(nave_x), y), radio, 2)


def dibujar_menu(mouse, botones, tiempo):
    pygame.draw.circle(pantalla, (17, 47, 81), (860, 565), 205)
    pygame.draw.circle(pantalla, (26, 69, 108), (860, 565), 190)
    pygame.draw.arc(pantalla, (67, 144, 196), (660, 365, 400, 400), math.pi, 2 * math.pi, 3)
    luna_y = 205 + int(5 * math.sin(tiempo * 1.2))
    pygame.draw.circle(pantalla, (164, 196, 220), (780, luna_y), 33)
    pygame.draw.circle(pantalla, (135, 165, 190), (770, luna_y - 8), 7)
    pygame.draw.circle(pantalla, (135, 165, 190), (795, luna_y + 6), 5)

    pantalla.blit(fuente_titulo.render("APOLO 13", True, BLANCO), (72, 118))
    pantalla.blit(fuente_subtitulo.render("REGRESO A CASA", True, NARANJA), (76, 174))
    dibujar_texto(
        pantalla,
        "Una misión de decisiones, recursos limitados y trabajo en equipo. Eres Houston: cada elección puede acercar a la tripulación a casa.",
        fuente_texto, SUAVE, 78, 235, 470, 8)
    panel(pygame.Rect(76, 345, 460, 92), "Controles")
    dif = DIFICULTADES[ajustes["dif"]]
    dibujar_texto(
        pantalla,
        "Decide con clic, 1–4 o flechas + Enter. Tienes %d s por misión; esperar consume recursos. P pausa · M sonido · F11 pantalla completa." % dif[1],
        fuente_pequena, BLANCO, 94, 376, 425, 4, 3)
    botones[1].texto = "DIFICULTAD: " + dif[0]
    botones[2].texto = "SONIDO: " + ("SÍ" if ajustes["sonido"] and SONIDOS else "NO")
    for boton in botones:
        boton.dibujar(pantalla, mouse)
    mejor = RECORDS.get(dif[0])
    texto_record = "Mejor puntuación en %s: %s" % (dif[0], mejor if mejor is not None else "—")
    dibujar_texto(pantalla, texto_record, fuente_pequena, SUAVE, 410, 478, 250, 4)
    dibujar_texto(pantalla, "Flechas ← → cambian la dificultad.", fuente_mini, SUAVE, 410, 522, 250, 4)
    pantalla.blit(fuente_mini.render("CENTRO DE CONTROL DE MISIÓN · HOUSTON", True, SUAVE), (76, 670))


def dibujar_mision(partida, mouse, botones, tiempo):
    numero = partida["mision"]
    misiones = partida["misiones"]
    mision = misiones[numero]

    pygame.draw.rect(pantalla, PANEL, (0, 0, ANCHO, 82))
    pygame.draw.line(pantalla, BORDE, (0, 81), (ANCHO, 81), 1)
    pantalla.blit(fuente_subtitulo.render("APOLO 13", True, BLANCO), (44, 18))
    pantalla.blit(fuente_mini.render(mision["fase"], True, NARANJA), (45, 50))
    estado = fuente_pequena.render("MISIÓN %d / %d" % (numero + 1, len(misiones)), True, SUAVE)
    pantalla.blit(estado, (ANCHO - estado.get_width() - 45, 31))
    segundos = max(0, math.ceil(partida["tiempo_restante"]))
    reloj_color = ROJO if segundos <= 10 else NARANJA
    reloj_imagen = fuente_mini.render("TIEMPO %02d:%02d" % (segundos // 60, segundos % 60), True, reloj_color)
    pantalla.blit(reloj_imagen, (ANCHO - reloj_imagen.get_width() - 45, 54))
    pygame.draw.rect(pantalla, (23, 42, 66), (0, 80, ANCHO, 3))
    pygame.draw.rect(pantalla, NARANJA, (0, 80, int((numero / len(misiones)) * ANCHO), 3))

    panel(pygame.Rect(42, 108, 625, 190))
    panel(pygame.Rect(42, 312, 625, 350), "Elige la respuesta de Houston")
    panel(pygame.Rect(690, 108, 368, 410), "Estado de la nave")
    panel(pygame.Rect(690, 532, 368, 130), "Telemetría")

    pantalla.blit(fuente_subtitulo.render(mision["titulo"], True, BLANCO), (62, 125))
    dibujar_texto(pantalla, mision["texto"], fuente_pequena, SUAVE, 62, 165, 585, 6, 4)
    dibujar_ruta(partida, tiempo)
    dibujar_recursos(partida["visibles"], 710, 151, 328, compacto=True)

    for flotante in partida["flotantes"]:
        imagen = fuente_pequena.render(flotante["txt"], True, flotante["color"])
        imagen.set_alpha(int(255 * min(1.0, flotante["vida"] / 1.0)))
        subida = (1.8 - flotante["vida"]) * 14
        pantalla.blit(imagen, (flotante["x"], flotante["y"] - subida))

    if partida["respuesta"] is None:
        fraccion = max(0.0, min(1.0, partida["tiempo_restante"] / tiempo_mision()))
        color_tiempo = ROJO if fraccion < 0.3 else NARANJA if fraccion < 0.6 else VERDE
        pygame.draw.rect(pantalla, (5, 12, 24), (62, 340, 585, 5), border_radius=3)
        pygame.draw.rect(pantalla, color_tiempo, (62, 340, int(585 * fraccion), 5), border_radius=3)
        for indice, boton in enumerate(botones):
            boton.dibujar(pantalla, mouse, foco=(partida["foco"] == indice))
        pantalla.blit(fuente_mini.render("ATAJOS: 1-4 · flechas + Enter · P pausa · M sonido", True, SUAVE), (62, 640))
    else:
        dibujar_texto(pantalla, "REPORTE DE HOUSTON", fuente_pequena, VERDE, 64, 350, 560, 5)
        dibujar_texto(pantalla, partida["respuesta"], fuente_texto, BLANCO, 64, 384, 560, 8, 5)

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
    exito = titulo != "MISIÓN FALLIDA"
    panel(pygame.Rect(70, 54, 960, 160))
    pantalla.blit(fuente_mini.render("INFORME FINAL DE LA MISIÓN · " + DIFICULTADES[ajustes["dif"]][0], True, NARANJA), (105, 78))
    pantalla.blit(fuente_titulo.render(titulo, True, tono), (102, 110))
    pantalla.blit(fuente_subtitulo.render("PUNTUACIÓN  %d / 100" % puntaje, True, BLANCO), (750, 143))
    dibujar_texto(pantalla, descripcion, fuente_pequena, SUAVE, 105, 177, 830, 4, 1)

    panel(pygame.Rect(70, 237, 610, 394), "Recursos al cierre")
    dibujar_recursos(datos, 100, 281, 545, compacto=True)
    panel(pygame.Rect(710, 237, 320, 190), "Resumen")
    minutos, segundos = divmod(int(partida["tiempo_juego"]), 60)
    lineas = [
        "Decisiones óptimas: %d / %d" % (partida["correctas"], len(partida["misiones"])),
        "Errores críticos: %d" % datos["errores"],
        "Acciones por tiempo agotado: %d" % partida["agotados"],
        "Tiempo de decisión: %02d:%02d" % (minutos, segundos),
        "Rango: " + rango(puntaje, exito),
    ]
    for indice, linea in enumerate(lineas):
        pantalla.blit(fuente_pequena.render(linea, True, BLANCO), (735, 282 + indice * 31))
    panel(pygame.Rect(710, 448, 320, 196), "Siguiente paso")
    dibujar_texto(pantalla, "¿Quieres mejorar tu resultado?", fuente_pequena, SUAVE, 735, 484, 268, 5)
    if partida["nuevo_record"]:
        pantalla.blit(fuente_mini.render("¡NUEVO RÉCORD!", True, VERDE), (735, 504))
    else:
        mejor = RECORDS.get(DIFICULTADES[ajustes["dif"]][0])
        if mejor is not None:
            pantalla.blit(fuente_mini.render("Récord: %d" % mejor, True, SUAVE), (735, 504))
    for boton in botones:
        boton.dibujar(pantalla, mouse)


def dibujar_fallo(partida, mouse, botones):
    panel(pygame.Rect(100, 70, 900, 625))
    pantalla.blit(fuente_mini.render("CENTRO DE CONTROL · SEÑAL PERDIDA", True, ROJO), (145, 145))
    pantalla.blit(fuente_titulo.render("MISIÓN INTERRUMPIDA", True, BLANCO), (145, 190))
    dibujar_texto(pantalla, partida["mensaje"], fuente_texto, SUAVE, 147, 265, 790, 8, 4)
    panel(pygame.Rect(145, 350, 800, 255), "Última telemetría")
    dibujar_recursos(partida["recursos"], 170, 389, 340, compacto=True, recursos=RECURSOS[:5])
    dibujar_recursos(partida["recursos"], 550, 389, 340, compacto=True, recursos=RECURSOS[5:])
    for boton in botones:
        boton.dibujar(pantalla, mouse)


def dibujar_pausa():
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((2, 6, 14, 215))
    pantalla.blit(overlay, (0, 0))
    titulo = fuente_titulo.render("PAUSA", True, BLANCO)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 290))
    for i, linea in enumerate(("P, Esc o clic: continuar", "Q: volver al menú principal")):
        imagen = fuente_texto.render(linea, True, SUAVE)
        pantalla.blit(imagen, (ANCHO // 2 - imagen.get_width() // 2, 360 + i * 34))


def crear_botones_eleccion(mision):
    return [Boton((61, 354 + i * 63, 586, 54), opcion["texto"], i) for i, opcion in enumerate(mision["opciones"])]


def cambiar_dificultad(paso):
    ajustes["dif"] = (ajustes["dif"] + paso) % len(DIFICULTADES)
    sonar("clic")


# ----------------------------------------------------------------------------
# Bucle principal
# ----------------------------------------------------------------------------
def main():
    partida = reiniciar()
    estrellas = [
        (random.randrange(ANCHO), random.randrange(ALTO), random.choice((1, 1, 2)), random.random() * 6.28)
        for _ in range(95)
    ]
    botones_menu = [
        Boton((78, 460, 300, 50), "INICIAR MISIÓN"),
        Boton((78, 518, 300, 44), "DIFICULTAD"),
        Boton((78, 570, 145, 42), "SONIDO"),
        Boton((233, 570, 145, 42), "SALIR"),
    ]
    boton_reiniciar = Boton((735, 520, 270, 34), "JUGAR DE NUEVO")
    boton_menu = Boton((735, 560, 270, 34), "VOLVER AL MENÚ")
    boton_salir_final = Boton((735, 600, 270, 34), "SALIR")
    boton_fallo = Boton((400, 625, 300, 52), "INTENTAR DE NUEVO")
    corriendo = True
    tiempo = 0.0
    fundido = 0.0
    clave_anterior = None

    while corriendo:
        dt = min(reloj.tick(FPS) / 1000.0, 0.05)
        tiempo += dt
        mouse = pygame.mouse.get_pos()

        botones_eleccion = []
        if partida["pantalla"] == "mision" and partida["respuesta"] is None:
            botones_eleccion = crear_botones_eleccion(partida["misiones"][partida["mision"]])

        for evento in pygame.event.get():
            pant = partida["pantalla"]
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEMOTION:
                partida["foco"] = None
            elif evento.type == pygame.KEYDOWN:
                k = evento.key
                if k == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif k == pygame.K_m:
                    ajustes["sonido"] = not ajustes["sonido"]
                elif pant == "menu":
                    if k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        partida = nueva_partida()
                    elif k == pygame.K_LEFT:
                        cambiar_dificultad(-1)
                    elif k == pygame.K_RIGHT:
                        cambiar_dificultad(1)
                    elif k == pygame.K_ESCAPE:
                        corriendo = False
                elif pant == "mision":
                    if partida["pausa"]:
                        if k in (pygame.K_p, pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                            partida["pausa"] = False
                        elif k == pygame.K_q:
                            partida = reiniciar()
                    elif partida["respuesta"] is not None:
                        if k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                            continuar_revision(partida)
                        elif k in (pygame.K_p, pygame.K_ESCAPE):
                            partida["pausa"] = True
                    else:
                        opciones = partida["misiones"][partida["mision"]]["opciones"]
                        total = len(opciones)
                        if k in (pygame.K_p, pygame.K_ESCAPE):
                            partida["pausa"] = True
                        elif k == pygame.K_UP:
                            foco = partida["foco"]
                            partida["foco"] = total - 1 if foco is None else (foco - 1) % total
                            sonar("clic")
                        elif k == pygame.K_DOWN:
                            foco = partida["foco"]
                            partida["foco"] = 0 if foco is None else (foco + 1) % total
                            sonar("clic")
                        elif k in (pygame.K_RETURN, pygame.K_KP_ENTER) and partida["foco"] is not None:
                            aplicar_opcion(partida, opciones[partida["foco"]], partida["foco"])
                        elif pygame.K_1 <= k <= pygame.K_4 and k - pygame.K_1 < total:
                            aplicar_opcion(partida, opciones[k - pygame.K_1], k - pygame.K_1)
                else:  # final / fallo
                    if k == pygame.K_r or (pant == "fallo" and k in (pygame.K_RETURN, pygame.K_KP_ENTER)):
                        partida = nueva_partida()
                    elif k == pygame.K_ESCAPE:
                        partida = reiniciar()
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if pant == "menu":
                    if botones_menu[0].contiene(evento.pos):
                        partida = nueva_partida()
                    elif botones_menu[1].contiene(evento.pos):
                        cambiar_dificultad(1)
                    elif botones_menu[2].contiene(evento.pos):
                        ajustes["sonido"] = not ajustes["sonido"]
                        sonar("clic")
                    elif botones_menu[3].contiene(evento.pos):
                        corriendo = False
                elif pant == "mision":
                    if partida["pausa"]:
                        partida["pausa"] = False
                    elif partida["respuesta"] is None:
                        for boton in botones_eleccion:
                            if boton.contiene(evento.pos):
                                opciones = partida["misiones"][partida["mision"]]["opciones"]
                                aplicar_opcion(partida, opciones[boton.indice], boton.indice)
                                break
                    elif pygame.Rect(48, 34, 1004, 652).collidepoint(evento.pos):
                        continuar_revision(partida)
                elif pant == "final":
                    if boton_reiniciar.contiene(evento.pos):
                        partida = nueva_partida()
                    elif boton_menu.contiene(evento.pos):
                        partida = reiniciar()
                    elif boton_salir_final.contiene(evento.pos):
                        corriendo = False
                elif pant == "fallo" and boton_fallo.contiene(evento.pos):
                    partida = nueva_partida()

        actualizar_revision(partida, dt)
        actualizar_reloj_mision(partida, dt)

        clave = (partida["pantalla"], partida["mision"])
        if clave != clave_anterior:
            fundido = 1.0
            clave_anterior = clave
        fundido = max(0.0, fundido - dt * 3.5)

        dibujar_fondo(tiempo, estrellas)
        pant = partida["pantalla"]
        if pant == "menu":
            dibujar_menu(mouse, botones_menu, tiempo)
        elif pant == "mision":
            if partida["respuesta"] is None:
                botones_eleccion = crear_botones_eleccion(partida["misiones"][partida["mision"]])
            dibujar_mision(partida, mouse, botones_eleccion, tiempo)
            if partida["respuesta"] is None and not partida["pausa"] and hay_critico(partida["recursos"]):
                VINETA.set_alpha(int(60 + 150 * (0.5 + 0.5 * math.sin(tiempo * 6))))
                pantalla.blit(VINETA, (0, 0))
            if partida["respuesta"] is not None:
                dibujar_revision(partida)
            if partida["pausa"]:
                dibujar_pausa()
        elif pant == "final":
            dibujar_final(partida, mouse, [boton_reiniciar, boton_menu, boton_salir_final])
        else:
            dibujar_fallo(partida, mouse, [boton_fallo])

        if fundido > 0:
            velo = pygame.Surface((ANCHO, ALTO))
            velo.set_alpha(int(255 * fundido))
            pantalla.blit(velo, (0, 0))

        desplazamiento = (0, 0)
        if partida["shake"] > 0:
            amplitud = max(1, int(9 * partida["shake"] / 0.45))
            desplazamiento = (random.randint(-amplitud, amplitud), random.randint(-amplitud, amplitud))
        ventana.fill((0, 0, 0))
        ventana.blit(pantalla, desplazamiento)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
