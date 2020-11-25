from PyQt5 import uic
from PyQt5.QtCore import (QObject, pyqtSignal)
import sys
import socket

window_name, base_class = uic.loadUiType("ventana_inicio.ui")

class Ventana_inicio(window_name, base_class):

    senal_nombre = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Inicio")

    def ingresar_usuario(self):
        self.senal_nombre.emit({"nombre": self.texto_nombre.text()})

    def cerrar_ventana(self):
        self.hide()
