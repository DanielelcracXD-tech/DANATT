import pygame
import sys
import time

pygame.init()

# -----------------------------------
# CONFIGURACION
# -----------------------------------

ANCHO = 1200
ALTO = 700

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Apollo 13 - Return Home")

clock = pygame.time.Clock()

# -----------------------------------
# COLORES
# -----------------------------------

FONDO = (10, 15, 30)
AZUL = (30, 80, 180)
VERDE = (0, 200, 100)
ROJO = (210, 50, 50)
BLANCO = (255,255,255)
GRIS = (70,70,70)

# -----------------------------------
# FUENTES
# -----------------------------------

titulo_font = pygame.font.SysFont("arial", 50, True)
texto_font = pygame.font.SysFont("arial", 24)

# -----------------------------------
# DATOS DEL JUEGO
# -----------------------------------

estado = "menu"

oxigeno = 100
energia = 100
comida = 100
co2 = 0
moral = 100

mensaje_houston = "Bienvenido a Apollo 13"

# -----------------------------------
# BOTON
# -----------------------------------

class Boton:

    def __init__(self, x, y, w, h, texto):
        self.rect = pygame.Rect(x,y,w,h)
        self.texto = texto

    def dibujar(self):

        pygame.draw.rect(
            pantalla,
            AZUL,
            self.rect,
            border_radius=10
        )

        txt = texto_font.render(
            self.texto,
            True,
            BLANCO
        )

        pantalla.blit(
            txt,
            (self.rect.x+15,
             self.rect.y+15)
        )

    def click(self,pos):
        return self.rect.collidepoint(pos)

# -----------------------------------
# BOTONES MENU
# -----------------------------------

btn_inicio = Boton(
    450,
    350,
    300,
    60,
    "INICIAR MISION"
)

# -----------------------------------
# MISION 1
# -----------------------------------

btn_tanques = Boton(
    700,180,350,60,
    "Revisar Tanques"
)

btn_com = Boton(
    700,280,350,60,
    "Revisar Comunicaciones"
)

btn_descanso = Boton(
    700,380,350,60,
    "Tomar Descanso"
)

# -----------------------------------
# MISION 2
# -----------------------------------

btn_oxigeno = Boton(
    700,180,350,60,
    "Revisar Oxigeno"
)

btn_nav = Boton(
    700,280,350,60,
    "Revisar Navegacion"
)

btn_fc3 = Boton(
    700,380,350,60,
    "Reiniciar FC3"
)

# -----------------------------------
# MISION 3
# -----------------------------------

btn_lm = Boton(
    700,180,350,60,
    "Usar Modulo Lunar"
)

btn_cm = Boton(
    700,280,350,60,
    "Permanecer en Modulo"
)

# -----------------------------------
# FUNCIONES
# -----------------------------------

def barra(x,y,valor,color,nombre):

    pygame.draw.rect(
        pantalla,
        GRIS,
        (x,y,250,25)
    )

    pygame.draw.rect(
        pantalla,
        color,
        (x,y,valor*2.5,25)
    )

    txt = texto_font.render(
        f"{nombre}: {valor}",
        True,
        BLANCO
    )

    pantalla.blit(txt,(x,y-25))

# -----------------------------------

def interfaz_recursos():

    barra(40,500,oxigeno,VERDE,"Oxigeno")
    barra(40,550,energia,(255,180,0),"Energia")
    barra(40,600,comida,(0,200,255),"Comida")

# -----------------------------------

while True:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:

            pygame.quit()
            sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN:

            pos = evento.pos

            # MENU

            if estado == "menu":

                if btn_inicio.click(pos):

                    estado = "mision1"

            # MISION 1

            elif estado == "mision1":

                if btn_tanques.click(pos):

                    energia -= 5
                    mensaje_houston = (
                        "Houston: Tanques revisados."
                    )

                    estado = "mision2"

                elif btn_com.click(pos):

                    energia -= 10
                    if energia <= 0:
                        time.sleep(.5)
                        estado = "perdido"
                    mensaje_houston = (
                        "Houston: Comunicaciones OK."
                    )

                elif btn_descanso.click(pos):

                    moral += 5

                    mensaje_houston = (
                        "Houston: El mantenimiento sigue pendiente."
                    )

            # MISION 2

            elif estado == "mision2":

                if btn_oxigeno.click(pos):

                    oxigeno -= 15

                    mensaje_houston = (
                        "Tanque 2 sin oxigeno."
                    )

                    estado = "mision3"

                elif btn_nav.click(pos):

                    energia -= 20
                    if energia <= 0:
                        time.sleep(.5)
                        estado = "perdido"
                    mensaje_houston = (
                        "Perdiste tiempo valioso."
                    )

                elif btn_fc3.click(pos):

                    energia -= 10

                    if energia <= 0:
                        time.sleep(.5)
                        estado = "perdido"

                    mensaje_houston = (
                        "FC3 sigue fuera de servicio."
                    )

            # MISION 3

            elif estado == "mision3":

                if btn_lm.click(pos):

                    energia += 5

                    mensaje_houston = (
                        "Correcto. LM usado como bote salvavidas."
                    )

                    estado = "final"

                elif btn_cm.click(pos):

                    energia -= 40
                    if energia <= 0:
                        time.sleep(.5)
                        estado = "perdido"

                    mensaje_houston = (
                        "Error. El modulo de mando pierde energia."
                    )

    pantalla.fill(FONDO)

    # MENU

    if estado == "menu":

        titulo = titulo_font.render(
            "APOLLO 13",
            True,
            BLANCO
        )

        pantalla.blit(titulo,(450,180))

        btn_inicio.dibujar()

    # MISION 1

    elif estado == "mision1":

        titulo = titulo_font.render(
            "MISION 1",
            True,
            BLANCO
        )

        pantalla.blit(titulo,(40,40))

        texto = texto_font.render(
            "Houston solicita mantenimiento rutinario.",
            True,
            BLANCO
        )

        pantalla.blit(texto,(40,120))

        btn_tanques.dibujar()
        btn_com.dibujar()
        btn_descanso.dibujar()

        interfaz_recursos()

    # MISION 2

    elif estado == "mision2":

        titulo = titulo_font.render(
            "EXPLOSION",
            True,
            ROJO
        )

        pantalla.blit(titulo,(40,40))

        datos = [

            "Bus B = 0V",
            "Voltaje AC = 25.5V",
            "FC1 OFFLINE",
            "FC3 OFFLINE"

        ]

        y = 150

        for d in datos:

            txt = texto_font.render(
                d,
                True,
                BLANCO
            )

            pantalla.blit(txt,(60,y))

            y += 40

        btn_oxigeno.dibujar()
        btn_nav.dibujar()
        btn_fc3.dibujar()

        interfaz_recursos()

    # MISION 3

    elif estado == "mision3":

        titulo = titulo_font.render(
            "CRISIS",
            True,
            ROJO
        )

        pantalla.blit(titulo,(40,40))

        txt = texto_font.render(
            "¿Que desea hacer la tripulacion?",
            True,
            BLANCO
        )

        pantalla.blit(txt,(40,150))

        btn_lm.dibujar()
        btn_cm.dibujar()

        interfaz_recursos()

    # FINAL

    elif estado == "final":

        titulo = titulo_font.render(
            "FIN DE MISION",
            True,
            BLANCO
        )

        pantalla.blit(titulo,(400,150))

        if energia > 40:

            resultado = "AMERIZAJE EXITOSO"

        else:

            resultado = "MISION COMPROMETIDA"

        txt = titulo_font.render(
            resultado,
            True,
            VERDE
        )

        pantalla.blit(txt,(300,320))

    #Perdiste

    elif estado == "perdido":

        titulo = titulo_font.render(
            "FIN DE MISION",
            True,
            BLANCO
        )

        pantalla.blit(titulo,(400,150))

        if energia > 40:

            resultado = "AMERIZAJE EXITOSO"

        else:

            resultado = "MISION COMPROMETIDA"

        txt = titulo_font.render(
            resultado,
            True,
            VERDE
        )

        pantalla.blit(txt,(300,320))

    # MENSAJES HOUSTON

    pygame.draw.rect(
        pantalla,
        (20,30,60),
        (0,650,1200,50)
    )

    msg = texto_font.render(
        mensaje_houston,
        True,
        BLANCO
    )

    pantalla.blit(msg,(20,665))

    pygame.display.update()
    clock.tick(60)
