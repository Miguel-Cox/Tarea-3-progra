import socket
import threading
import sys
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget)
from PyQt5.QtCore import (QObject, pyqtSignal, QThread)
import json


class Client(QThread):

    senal_a_sala_espera = pyqtSignal(str)
    senal_abrir_sala_espera = pyqtSignal()
    senal_usuario_desconectado_sala_espera = pyqtSignal(str)
    senal_cerrar_ventana_espera = pyqtSignal()
    senal_abrir_ventana_principal = pyqtSignal()
    senal_jugadores_orden = pyqtSignal(dict)
    senal_enviar_cartas = pyqtSignal(dict)
    senal_turno_inicial = pyqtSignal(str)
    senal_sacar_carta = pyqtSignal(dict)
    senal_ganador = pyqtSignal(str)

    def __init__(self, port, host):
        super().__init__()
        print("Inicializando cliente...")

        self.host = host
        self.port = port
        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.abierto = "no"
        self.nombre = ""

        try:
            self.connect_to_server()
            self.listen()
        except ConnectionError:
            print("Conexión terminada.")
            self.socket_client.close()
            exit()

    def connect_to_server(self):
        self.socket_client.connect((self.host, self.port))
        print("Cliente conectado exitosamente al servidor.")


    def listen(self):
        thread = threading.Thread(target=self.listen_thread, daemon=True)
        thread.start()

    def send_str(self, dict):
        msg = json.dumps(dict)
        msg_bytes = msg.encode()
        self.socket_client.sendall(msg_bytes)

    def listen_thread(self):
        while True:
            try:
                response_bytes_length = self.socket_client.recv(4)
                response_length = int.from_bytes(response_bytes_length, byteorder='big')
                response = bytearray()

                while len(response) < response_length:
                    read_length = min(4096, response_length - len(response))
                    response.extend(self.socket_client.recv(read_length))
                response = json.loads(response)

                if type(response) == dict:
                    for u in response.keys():
                        if u == "aceptado":
                            if response["aceptado"] == "si" and self.abierto == "si":
                                self.senal_a_sala_espera.emit(response["nombre"])

                        if u == "abrir":
                            if response["abrir"] == "si":
                                self.senal_abrir_sala_espera.emit()
                                self.abierto = "si"

                        if u == "sacar":
                            if response["sacar"] == "si" and self.abierto == "si":
                                self.sacar_jugador(response["nombre"])

                        if u == "jugadores":
                            posicion = response["jugadores"].index(self.nombre)

                            posicion += 1
                            if posicion > 3:
                                posicion = 0
                            self.jugador2 = response["jugadores"][posicion]
                            posicion += 1
                            if posicion > 3:
                                posicion = 0
                            self.jugador3 = response["jugadores"][posicion]
                            posicion += 1
                            if posicion > 3:
                                posicion = 0
                            self.jugador4 = response["jugadores"][posicion]

                            self.senal_jugadores_orden.emit({"jugadores": [self.nombre, self.jugador2, self.jugador3, self.jugador4]})

                        if u == "turno":
                            self.senal_turno_inicial.emit(response["turno"])
                        if u == "ganador":
                            self.senal_ganador.emit(response["ganador"])


                        if u == "carta":
                            if response["agregar"] == "si":
                                a = response["carta"]
                                code = bytearray(a)
                                n = 0
                                for u in range(3):
                                    indice = int.from_bytes(code[n:(n+4)], byteorder="big")

                                    n += 4
                                    largo_string = int.from_bytes(code[n:(n+4)], byteorder="little")

                                    n += 4
                                    string = code[n:(n+largo_string)].decode()
                                    n += largo_string

                                    if indice == 1:
                                        color = string
                                    elif indice == 2:
                                        tipo = string
                                    elif indice == 3:
                                        pixmap = string

                                if tipo == "color":
                                    pixmap = "sprites/simple/color.png"
                                datos = {"nombre": response["nombre"], "tipo": tipo, "color": color, "pixmap": pixmap}

                                self.senal_enviar_cartas.emit(datos)

                            elif response["agregar"] == "no":
                                a = response["carta"]
                                code = bytearray(a)
                                n = 0
                                for u in range(3):
                                    indice = int.from_bytes(code[n:(n + 4)], byteorder="big")

                                    n += 4
                                    largo_string = int.from_bytes(code[n:(n + 4)], byteorder="little")

                                    n += 4
                                    string = code[n:(n + largo_string)].decode()
                                    n += largo_string

                                    if indice == 1:
                                        color = string
                                    elif indice == 2:
                                        tipo = string
                                    elif indice == 3:
                                        pixmap = string

                                datos = {"nombre": response["nombre"], "tipo": tipo, "color": color, "pixmap": pixmap}

                                self.senal_sacar_carta.emit(datos)


                else:
                    if response == "empezar":
                        self.senal_cerrar_ventana_espera.emit()
                        self.senal_abrir_ventana_principal.emit()


            except (ConnectionResetError, json.JSONDecodeError):
                print("¡Se perdió la conexión al servidor!, lo sentimos")
                sys.exit()


    def sacar_jugador(self, name):
        self.senal_usuario_desconectado_sala_espera.emit(name)

    def recibir_nombre(self, dict):
        self.nombre = dict["nombre"]

    def pedir_carta(self, quien):
        self.send_str({"nombre": quien})

    def pasar_turno(self, turno_actual):
        self.send_str("pasar_turno")

    def evaluar_carta(self, carta):
        self.send_str({"nombre_": self.nombre, "tipo": carta[1], "color": carta[2]})

    def perdio(self, dict):
        dict["depana"] = ""
        self.send_str(dict)

    def dccuatro(self, dict):
        self.send_str(dict)