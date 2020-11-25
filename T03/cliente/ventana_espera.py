from PyQt5 import uic
from PyQt5.QtCore import (QObject, pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit)
import sys
import socket

window_name, base_class = uic.loadUiType("ventana_de_espera.ui")

class Ventana_espera(window_name, base_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Espera")
        self.labels_disponibles = [self.usuario1, self.usuario2, self.usuario3, self.usuario4]
        self.labels_usados = []

    def iniciar_ventana(self):
        self.show()

    def agregar_nombre(self, nombre):
        self.labels_disponibles[0].setText(nombre)
        self.labels_usados.append(self.labels_disponibles[0])
        self.labels_disponibles.pop(0)

    def sacar_jugador(self, nombre):
        for u in self.labels_usados:
            if u.text() == nombre:
                u.setText("Esperando")
                self.labels_disponibles.append(u)
                self.labels_usados.remove(u)
    def cerrar_ventana(self):
        self.hide()
