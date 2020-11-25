from generador_de_mazos import sacar_cartas
import socket
import threading
import json

class Servidor:

    def __init__(self, host, port):
        with open("parametros_servidor.json", "r", encoding="utf-8") as json_file:
            self.parametros = json.load(json_file)

        self.host = host
        self.port = port
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockets = {}
        self.bind_listen()
        self.accept_connections()
        self.nombres_usuarios = list()
        self.usuarios_conectados = 0
        self.usuarios_ya_conectados = list()
        self.ingresado = "no"
        self.mazo = []
        self.generar_mazo()
        self.empezo = "no"
        self.cartas_sacadas = 0
        self.sentido = 1




    def bind_listen(self):
        self.socket_server.bind((self.host, self.port))
        print(f"Servidor escuchando en {self.host} : {self.port}")
        print("     Cliente      |      Evento      |      Detalles")
        print("------------------|------------------|---------------------")
        self.socket_server.listen()

    def accept_connections(self):
        thread = threading.Thread(target=self.accept_connection_thread, daemon=True)
        thread.start()

    def accept_connection_thread(self):
        while True:
            client_socket, adress = self.socket_server.accept()
            self.sockets[client_socket] = adress
            listening_client_thread = threading.Thread(target=self.listening_client_thread, args=(client_socket, ), daemon=True)
            listening_client_thread.start()

    def listening_client_thread(self, client_socket):
        while True:
            try:
                response = client_socket.recv(4096)
                recived = json.loads(response)

                if self.empezo == "si":
                    if len(self.nombres_usuarios) == 1:
                        self.ganador(self.nombres_usuarios[0])

                if type(recived) == dict:
                    if "nombre" in recived.keys():
                        if recived["nombre"].isalnum() and recived["nombre"] not in self.nombres_usuarios:
                            self.nombres_usuarios.append(recived["nombre"])
                            largo_nombre = len(recived["nombre"])

                            if ((18 - largo_nombre)) % 2 != 0:
                                valor_aprox = int(((18 - largo_nombre) / 2)) + 1
                            else:
                                valor_aprox = ((18 - largo_nombre) / 2)

                            print(" " * int(((18 - largo_nombre) / 2)) + f"{recived['nombre']}" + " " * int(
                                valor_aprox) + "|" + "    Conectarse    |         -")
                            recived["aceptado"] = "si"

                            a = json.dumps({'abrir': "si", "aceptado": "no", "sacar": "no"})
                            self.send(a, client_socket)
                            self.ingresado = "si"

                            recived["abrir"] = "no"
                            recived["sacar"] = "no"
                            msg_cod = json.dumps(recived)
                            nombre = recived["nombre"]
                            recibo = recived
                            for u in self.usuarios_ya_conectados:
                                self.send(json.dumps(u), client_socket)

                            for skt in self.sockets.keys():
                                self.send(msg_cod, skt)

                            self.usuarios_ya_conectados.append(recived)
                            self.usuarios_conectados += 1

                            if self.usuarios_conectados == 4:
                                self.iniciar_partida()
                                self.empezo = "si"

                    if "tipo" in recived.keys():
                        self.evaluar_carta(recived["nombre_"], recived["tipo"], recived["color"])

                    if "perdio" in recived.keys():
                        if self.sockets.get(client_socket):
                            largo_nombre3 = len(recived["perdio"])

                            if ((18 - largo_nombre3)) % 2 != 0:
                                valor_aprox3 = int(((18 - largo_nombre3) / 2)) + 1
                            else:
                                valor_aprox3 = ((18 - largo_nombre3) / 2)
                            print(" " * int((18 - largo_nombre3) / 2) + f"{recived['perdio']}" + " " * int(
                                valor_aprox3) + "|" + "      Perdio      |         -")
                            self.nombres_usuarios.remove(recived["perdio"])
                            self.usuarios_conectados -= 1

                            recibo["nombre"] = recived["perdio"]
                            recibo["sacar"] = "si"
                            recibo["aceptado"] = "no"
                            msg_cod = json.dumps(recibo)


                            for skt in self.sockets.keys():
                                self.send(msg_cod, skt)

                    if "dccuatro" in recived.keys():
                        print(recived)
                        nombre_4 = recived["quien"]
                        largo_nombre4 = len(nombre_4)

                        if ((18 - largo_nombre4)) % 2 != 0:
                            valor_aprox4 = int(((18 - largo_nombre4) / 2)) + 1
                        else:
                            valor_aprox4 = ((18 - largo_nombre4) / 2)

                        print(" " * int((18 - largo_nombre4) / 2) + f"{nombre_4}" + " " * int(valor_aprox4) + "|" + "    Dccuatro      |     Le dieron Dccuatro")


                    if len(recived.keys()) == 1:

                        self.cartas_sacadas += 1

                        largo_nombre1 = len(recived["nombre"])

                        if ((18 - largo_nombre1)) % 2 != 0:
                            valor_aprox1 = int(((18 - largo_nombre1) / 2)) + 1
                        else:
                            valor_aprox1 = ((18 - largo_nombre1) / 2)

                        carta = self.mazo.pop(0)

                        if self.cartas_sacadas > 20:
                            print(" " * int(((18 - largo_nombre1) / 2)) + f"{recived['nombre']}" + " " * int(
                                valor_aprox1) + "|" + "    Robar Carta   |" + f"      {carta[0]} {carta[1]}")

                        carta = self.mazo_encriptado.pop(0)

                        for skt in self.sockets:
                            self.send(json.dumps({"nombre": recived["nombre"], "carta": list(carta), "agregar": "si"}),
                                      skt)


                elif type(recived) == str:
                    if recived == "pasar_turno":
                        if self.sentido == 1:
                            n_usuarios = len(self.nombres_usuarios)
                            valor_actual = self.nombres_usuarios.index(self.turno_de)
                            valor_actual += 1


                            if valor_actual == n_usuarios:
                                valor_actual = 0
                            self.turno_de = self.nombres_usuarios[valor_actual]

                            msg_jugadores_cod = json.dumps({"turno": self.turno_de})

                            for skt in self.sockets.keys():
                                self.send(msg_jugadores_cod, skt)



                        elif self.sentido == -1:
                            n_usuarios = len(self.nombres_usuarios)
                            valor_actual = self.nombres_usuarios.index(self.turno_de)
                            valor_actual -= 1

                            if valor_actual == -1:
                                valor_actual = n_usuarios - 1
                            self.turno_de = self.nombres_usuarios[valor_actual]

                            msg_jugadores_cod = json.dumps({"turno": self.turno_de})

                            for skt in self.sockets.keys():
                                self.send(msg_jugadores_cod, skt)



            except ConnectionResetError:
                if self.sockets.get(client_socket):
                    if self.ingresado == "si":

                        print(" " * int((18-largo_nombre)/2) + f"{nombre}" + " " * int(valor_aprox) + "|" + "   Desconectarse  |         -")
                        self.nombres_usuarios.remove(nombre)
                        if self.empezo == "no":
                            self.usuarios_ya_conectados.remove(recived)
                        self.usuarios_conectados -= 1

                        recibo["sacar"] = "si"
                        recibo["aceptado"] = "no"
                        msg_cod = json.dumps(recibo)
                        del self.sockets[client_socket]

                        for skt in self.sockets.keys():
                            self.send(msg_cod, skt)


                    else:
                        del self.sockets[client_socket]

    @staticmethod
    def send(value, sock):

        stringified_value = str(value)
        msg_bytes = stringified_value.encode()
        msg_length = len(msg_bytes).to_bytes(4, byteorder='big')
        sock.send(msg_length + msg_bytes)

    def iniciar_partida(self):
        carta = self.mazo.pop(0)
        self.carta_actual = carta
        print("                  |" + " Comienza partida |      "+ f"{carta[0]} {carta[1]}")
        msg_cod = json.dumps("empezar")
        msg_jugadores_cod = json.dumps({"jugadores": self.nombres_usuarios, "turno": self.nombres_usuarios[0]})
        self.turno_de = self.nombres_usuarios[0]

        carta = self.mazo_encriptado.pop(0)

        for skt in self.sockets.keys():
            self.send(msg_cod, skt)
            self.send(msg_jugadores_cod, skt)
            self.send(json.dumps({"nombre": "centro", "carta": list(carta), "agregar": "si"}), skt)

    def generar_mazo(self):
        self.mazo = sacar_cartas(self.parametros["largo_mazo"])
        self.encriptar_mazo()

    def encriptar_mazo(self):

        self.mazo_encriptado = list()
        for u in self.mazo:
            codigo = self.encriptar_carta(u[0], u[1])

            self.mazo_encriptado.append(codigo)

    def encriptar_carta(self, tipo, color):

        codigo = b""
        codigo += ((1).to_bytes(4, byteorder="big"))
        largo_string = len(color.encode())
        codigo += largo_string.to_bytes(4, byteorder="little")
        codigo += color.encode()

        codigo += ((2).to_bytes(4, byteorder="big"))
        largo_string = len(tipo.encode())
        codigo += largo_string.to_bytes(4, byteorder="little")
        codigo += tipo.encode()

        codigo += ((3).to_bytes(4, byteorder="big"))

        if color == "":
            pixmap = self.parametros["pixmap_color"]
        else:
            pixmap = f"sprites/simple/{tipo}_{color}.png"

        largo_string = len(pixmap.encode())
        codigo += largo_string.to_bytes(4, byteorder="little")
        codigo += pixmap.encode()
        return codigo

    def evaluar_carta(self, nombre, tipo, color):

        if tipo == "+2":
            if self.carta_actual[0] == "+2" or self.carta_actual[1] == color:
                carta = self.encriptar_carta(tipo, color)
                self.carta_actual = (tipo, color)
                self.jugo_carta(nombre, tipo, color)
                for skt in self.sockets:
                    self.send(json.dumps({"nombre": nombre, "carta": list(carta), "agregar": "no"}), skt)
                    self.send(json.dumps({"nombre": "centro", "carta": list(carta), "agregar": "si"}), skt)

        elif tipo == "sentido":
            if self.carta_actual[0] == "sentido" or self.carta_actual[1] == color:
                carta = self.encriptar_carta(tipo, color)
                self.carta_actual = (tipo, color)

                if self.sentido == 1:
                    self.sentido = -1
                elif self.sentido == -1:
                    self.sentido = 1

                self.jugo_carta(nombre, tipo, color)

                for skt in self.sockets:
                    self.send(json.dumps({"nombre": nombre, "carta": list(carta), "agregar": "no"}), skt)
                    self.send(json.dumps({"nombre": "centro", "carta": list(carta), "agregar": "si"}), skt)

        elif tipo == "color":
            carta = self.encriptar_carta(tipo, color)
            self.carta_actual = (tipo, color)

            self.jugo_carta(nombre, tipo, color)

            for skt in self.sockets:
                self.send(json.dumps({"nombre": nombre, "carta": list(carta), "agregar": "no"}), skt)
                self.send(json.dumps({"nombre": "centro", "carta": list(carta), "agregar": "si"}), skt)


        else:
            if self.carta_actual[0] == tipo or self.carta_actual[1] == color:
                carta = self.encriptar_carta(tipo, color)
                self.carta_actual = (tipo, color)

                self.jugo_carta(nombre, tipo, color)

                for skt in self.sockets:
                    self.send(json.dumps({"nombre": nombre, "carta": list(carta), "agregar": "no"}), skt)
                    self.send(json.dumps({"nombre": "centro", "carta": list(carta), "agregar": "si"}), skt)

    def jugo_carta(self, nombre, tipo, color):
        largo_nombre2 = len(nombre)

        if ((18 - largo_nombre2)) % 2 != 0:
            valor_aprox2 = int(((18 - largo_nombre2) / 2)) + 1
        else:
            valor_aprox2 = ((18 - largo_nombre2) / 2)

        print(" " * int(((18 - largo_nombre2) / 2)) + f"{nombre}" + " " * int(valor_aprox2) + "|" + "    Jugar Carta   |" + f"      {tipo} {color}")

    def ganador(self, nombre):

        for skt in self.sockets:
            self.send(json.dumps({"ganador": nombre}), skt)