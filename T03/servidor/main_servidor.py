import sys
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget)
import socket
from servidor import Servidor
import json

with open("parametros_servidor.json", "r", encoding="utf-8") as json_file:
    parametros = json.load(json_file)


servidor = Servidor(parametros["host"], parametros["port"])
