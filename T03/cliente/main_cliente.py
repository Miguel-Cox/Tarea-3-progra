import sys
import socket
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget)
from ventana_inicio import Ventana_inicio
from ventana_espera import Ventana_espera
from ventana_principal import Ventana_principal
from cliente import Client
import json

app = QApplication([])

with open("parametros_cliente.json", "r", encoding="utf-8") as json_file:
    parametros = json.load(json_file)

ventana_inicial = Ventana_inicio()
ventana_espera = Ventana_espera()
ventana_principal = Ventana_principal()
ventana_inicial.show()
cliente = Client(parametros["port"], parametros["host"])

ventana_inicial.senal_nombre.connect(cliente.send_str)
ventana_inicial.senal_nombre.connect(cliente.recibir_nombre)
cliente.senal_a_sala_espera.connect(ventana_espera.agregar_nombre)
cliente.senal_abrir_sala_espera.connect(ventana_espera.iniciar_ventana)
cliente.senal_abrir_sala_espera.connect(ventana_inicial.cerrar_ventana)
cliente.senal_usuario_desconectado_sala_espera.connect(ventana_espera.sacar_jugador)

cliente.senal_cerrar_ventana_espera.connect(ventana_espera.cerrar_ventana)
cliente.senal_abrir_ventana_principal.connect(ventana_principal.iniciar_ventana)
cliente.senal_jugadores_orden.connect(ventana_principal.orden_jugadores)
ventana_principal.senal_robar_carta.connect(cliente.pedir_carta)
cliente.senal_enviar_cartas.connect(ventana_principal.info_carta_robada)
cliente.senal_turno_inicial.connect(ventana_principal.turno_de)
ventana_principal.senal_pasar_turno.connect(cliente.pasar_turno)
ventana_principal.senal_evaluar_carta.connect(cliente.evaluar_carta)
cliente.senal_sacar_carta.connect(ventana_principal.sacar_carta_mano)
ventana_principal.senal_perdio.connect(cliente.perdio)
cliente.senal_ganador.connect(ventana_principal.ganador)
ventana_principal.senal_dccuatro.connect(cliente.dccuatro)

sys.exit(app.exec_())