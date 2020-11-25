from PyQt5 import uic
from PyQt5.QtCore import (QObject, pyqtSignal, Qt, QRect, QThread)
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit)
from PyQt5.QtGui import QPixmap, QTransform, QPainter
import threading

import sys
import socket
import time

window_name, base_class = uic.loadUiType("ventana_principal.ui")

class Ventana_principal(window_name, base_class):
    senal_robar_carta = pyqtSignal(str)
    senal_pasar_turno = pyqtSignal(str)
    senal_evaluar_carta = pyqtSignal(list)
    senal_perdio = pyqtSignal(dict)
    senal_dccuatro = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Principal")
        self.cartas_usuario1 = []
        self.cartas_usuario2 = []
        self.cartas_usuario3 = []
        self.cartas_usuario4 = []
        self.widget_colores.hide()
        self.widget_perdiste.hide()
        self.widget_ganaste.hide()
        self.posicion_carta_seleccionada = 0
        self.empezo = "no"
        self.boton_verde.clicked.connect(self.elegir_color_verde)
        self.boton_rojo.clicked.connect(self.elegir_color_rojo)
        self.boton_azul.clicked.connect(self.elegir_color_azul)
        self.boton_amarillo.clicked.connect(self.elegir_color_amarillo)
        self.boton_seguir_viendo.clicked.connect(self.seguir_viendo)
        self.boton_irse.clicked.connect(self.irse)
        self.dccuatro_button.clicked.connect(self.dccuatro)




    def iniciar_ventana(self):
        self.empezo = "si"
        self.show()


    def jugador_1_roba(self, pixmap, tipo, color):
        self.label_carta = QLabel("", self)
        self.label_carta.resize(70, 101)
        self.label_carta.setMaximumWidth(70)
        self.label_carta.setMaximumHeight(101)
        self.label_carta.setMinimumWidth(70)
        self.label_carta.setMinimumHeight(101)
        pixmap = pixmap
        self.label_carta.setPixmap(QPixmap(pixmap))
        self.label_carta.setScaledContents(True)

        self.horizontalLayout_1.addWidget(self.label_carta)

        self.cartas_usuario1.append([self.label_carta, tipo, color])
        if len(self.cartas_usuario1) >= 10:
            self.widget_perdiste.show()
            self.terminar_turno()


    def jugardor_2_roba(self, tipo, color):
        self.label_carta = QLabel("", self)
        self.label_carta.resize(101, 70)
        self.label_carta.setMaximumWidth(101)
        self.label_carta.setMaximumHeight(70)
        self.label_carta.setMinimumWidth(101)
        self.label_carta.setMinimumHeight(70)
        pixmap = QPixmap("sprites/simple/reverso.png")
        transform = QTransform().rotate(90)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.label_carta.setPixmap(pixmap)
        self.label_carta.setScaledContents(True)

        self.verticalLayout_2.addWidget(self.label_carta)

        self.cartas_usuario2.append([self.label_carta, tipo, color])


    def jugardor_3_roba(self, tipo, color):

        self.label_carta = QLabel("", self)
        self.label_carta.resize(70, 101)
        self.label_carta.setMaximumWidth(70)
        self.label_carta.setMaximumHeight(101)
        self.label_carta.setMinimumWidth(70)
        self.label_carta.setMinimumHeight(101)
        pixmap = QPixmap("sprites/simple/reverso.png")
        transform = QTransform().rotate(180)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.label_carta.setPixmap(pixmap)
        self.label_carta.setScaledContents(True)

        self.horizontalLayout_3.addWidget(self.label_carta)

        self.cartas_usuario3.append([self.label_carta, tipo, color])


    def jugardor_4_roba(self, tipo, color):

        self.label_carta = QLabel("", self)
        self.label_carta.resize(101, 70)
        self.label_carta.setMaximumWidth(101)
        self.label_carta.setMaximumHeight(70)
        self.label_carta.setMinimumWidth(101)
        self.label_carta.setMinimumHeight(70)
        pixmap = QPixmap("sprites/simple/reverso.png")
        transform = QTransform().rotate(-90)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.label_carta.setPixmap(pixmap)
        self.label_carta.setScaledContents(True)

        self.verticalLayout_4.addWidget(self.label_carta)

        self.cartas_usuario4.append([self.label_carta, tipo, color])

    def cambiar_carta_central(self, pixmap, tipo, color):
        pixmap = QPixmap(pixmap)
        self.carta_centro.setPixmap(pixmap)
        self.label_color_carta.setText(color)

        if color == "azul":
            color = "blue"
        elif color == "rojo":
            color = "red"
        elif color == "amarillo":
            color = "yellow"
        elif color == "verde":
            color = "green"

        self.label_color_carta.setStyleSheet(f"color: {color};")

    def orden_jugadores(self, dict):
        jugadores = dict["jugadores"]
        self.jugador1 = jugadores[0]
        self.jugador2 = jugadores[1]
        self.jugador3 = jugadores[2]
        self.jugador4 = jugadores[3]
        self.inicia_partida()

    def inicia_partida(self):
        for u in range(5):
            self.robar_carta()
            time.sleep(0.1) # Esto lo hago porque al cargar todas las cartas al mismo tiempo colapsaba

    def robar_carta(self):
        self.senal_robar_carta.emit(self.jugador1)

    def info_carta_robada(self, dict):
        if self.jugador1 == dict["nombre"]:
            self.jugador_1_roba(dict["pixmap"], dict["tipo"], dict["color"])

        elif self.jugador2 == dict["nombre"]:
            self.jugardor_2_roba(dict["tipo"], dict["color"])

        elif self.jugador3 == dict["nombre"]:
            self.jugardor_3_roba(dict["tipo"], dict["color"])

        elif self.jugador4 == dict["nombre"]:
            self.jugardor_4_roba(dict["tipo"], dict["color"])

        elif dict["nombre"] == "centro":
            self.cambiar_carta_central(dict["pixmap"], dict["tipo"], dict["color"])

    def sacar_carta_mano(self, dict):

        if dict["nombre"] == self.jugador1:
            for p in self.cartas_usuario1:
                if dict["tipo"] == p[1] and dict["color"] == p[2]:
                    p[0].hide()
                    self.cartas_usuario1.remove(p)
                    self.terminar_turno()
                    if len(self.cartas_usuario1) == 0:
                        self.ganaste()

        elif dict["nombre"] == self.jugador2:
            for u in self.cartas_usuario2:
                if u[1] == dict["tipo"] and u[2] == dict["color"]:
                    u[0].hide()
                    self.cartas_usuario2.remove(u)

        elif dict["nombre"] == self.jugador3:
            for u in self.cartas_usuario3:
                if u[1] == dict["tipo"] and u[2] == dict["color"]:
                    u[0].hide()
                    self.cartas_usuario3.remove(u)

        elif dict["nombre"] == self.jugador4:
            for u in self.cartas_usuario4:
                if u[1] == dict["tipo"] and u[2] == dict["color"]:
                    u[0].hide()
                    self.cartas_usuario4.remove(u)


    def mousePressEvent(self, ev):
        qrec_robar = QRect(750, 190, 151, 221)
        if ev.button() == Qt.LeftButton and ev.pos() in qrec_robar and self.turno_de == self.jugador1:
            self.robar_carta()
            self.terminar_turno()

        qrects = list()
        for u in self.cartas_usuario1:
            qrects.append(QRect(u[0].x() + 120, u[0].y() + 530, 70, 101))

        if ev.button() == Qt.LeftButton and self.turno_de == self.jugador1:
            for qrec in qrects:
                if ev.pos() in qrec:
                    self.posicion_carta_seleccionada = qrects.index(qrec)
                    if self.cartas_usuario1[self.posicion_carta_seleccionada][1] == "color":
                        self.widget_colores.show()

                    else:
                        self.senal_evaluar_carta.emit(self.cartas_usuario1[self.posicion_carta_seleccionada])


    def turno_de(self, nombre):
        self.turno_de = nombre
        self.label_turno.setText(nombre)

    def terminar_turno(self):
        self.senal_pasar_turno.emit(self.turno_de)

    def elegir_color_amarillo(self):
        if self.empezo == "si":
            self.cartas_usuario1[self.posicion_carta_seleccionada][2] = "amarillo"
            self.widget_colores.hide()
            self.senal_evaluar_carta.emit(self.cartas_usuario1[self.posicion_carta_seleccionada])

    def elegir_color_rojo(self):
        if self.empezo == "si":
            self.cartas_usuario1[self.posicion_carta_seleccionada][2] = "rojo"
            self.widget_colores.hide()
            self.senal_evaluar_carta.emit(self.cartas_usuario1[self.posicion_carta_seleccionada])

    def elegir_color_azul(self):
        if self.empezo == "si":
            self.cartas_usuario1[self.posicion_carta_seleccionada][2] = "azul"
            self.widget_colores.hide()
            self.senal_evaluar_carta.emit(self.cartas_usuario1[self.posicion_carta_seleccionada])

    def elegir_color_verde(self):
        if self.empezo == "si":
            self.cartas_usuario1[self.posicion_carta_seleccionada][2] = "verde"
            self.widget_colores.hide()
            self.senal_evaluar_carta.emit(self.cartas_usuario1[self.posicion_carta_seleccionada])

    def perdio(self, jugador):
        self.senal_perdio.emit({"perdio": jugador})

    def seguir_viendo(self):
        self.perdio(self.jugador1)
        self.widget_perdiste.hide()

    def irse(self):
        sys.exit()

    def ganaste(self):
        self.widget_ganaste.show()
        self.perdio(self.jugador2)
        time.sleep(0.1)
        self.perdio(self.jugador3)
        time.sleep(0.1)
        self.perdio(self.jugador4)

    def dccuatro(self):
        if len(self.cartas_usuario2) == 1:
            self.senal_dccuatro({"quien": self.jugador2, "dccuatro": ""})

        elif len(self.cartas_usuario3) == 1:
            self.senal_dccuatro({"quien": self.jugador3, "dccuatro": ""})

        elif len(self.cartas_usuario4) == 1:
            self.senal_dccuatro({"quien": self.jugador4, "dccuatro": ""})
        else:
            for p in range(4):
                self.robar_carta()
                time.sleep(0.1)

    def ganador(self, nombre):
        if self.jugador1 == nombre:
            self.ganaste()