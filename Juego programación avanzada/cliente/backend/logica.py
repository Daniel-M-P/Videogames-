import socket
import json
import os
import re
import backend.constantes_backend as c
from threading import Thread
from PyQt6.QtCore import pyqtSignal, QObject, QThread, QTimer
from random import randint

class ControladorTiempo(QObject):
    senal_actualizar_tiempo = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.tiempo_restante = c.TIEMPO_JUEGO
        self.temporizador = QTimer(self)
        self.temporizador.timeout.connect(self.actualizar_tiempo)
        self.temporizador.setInterval(1000)
        self.temporizador.start()

    def actualizar_tiempo(self):
        if self.tiempo_restante != 0:
            self.tiempo_restante -= 1 
            minutos = self.tiempo_restante // 60
            segundos = self.tiempo_restante % 60
            titulo = "<h2>Tiempo restante</h2>"
            tiempo = f"<h3>{minutos:02}:{segundos:02}</h3>"
            self.senal_actualizar_tiempo.emit(f"{titulo}{tiempo}")

    def anadir_tiempo(self):
        self.tiempo_restante += c.TIEMPO_ADICIONAL
    
    def pausar(self):
        self.temporizador.stop()
    
    def reanudar(self):
        self.temporizador.start()

class ControladorSandias(QObject):
    senal_aparecer_sandia = pyqtSignal(int, int)
    senal_desaparecer_sandia = pyqtSignal(int, int)
    def __init__(self, numeros_columnas: int):
        super().__init__()
        self.numeros_columnas = numeros_columnas
        self.temporizador_aparicion = QTimer(self)
        self.temporizador_aparicion.timeout.connect(self.aparecer_sandia)
        self.temporizador_aparicion.setInterval(c.TIEMPO_APARICION)
        self.temporizador_aparicion.start()

        self.temporizador_desaparicion = QTimer(self)
        self.temporizador_desaparicion.setSingleShot(True)
        self.temporizador_desaparicion.setInterval(c.TIEMPO_DURACION)

    def aparecer_sandia(self):
        numero_columna = randint(0, self.numeros_columnas - 1)
        numero_fila = randint(0, self.numeros_columnas - 1)
        self.senal_aparecer_sandia.emit(numero_columna, numero_fila)
        self.temporizador_desaparicion.timeout.connect(lambda: self.senal_desaparecer_sandia.emit(numero_columna, numero_fila))
        self.temporizador_desaparicion.start()

    def pausar(self):
        self.temporizador_aparicion.stop()
        self.temporizador_desaparicion.stop()
    
    def reanudar(self):
        self.temporizador_aparicion.start()
        self.temporizador_desaparicion.start()

class Logica(QObject):
    senal_empezar_VentanaInicio = pyqtSignal(list)
    senal_popup = pyqtSignal(str)
    senal_iniciar_juego = pyqtSignal(str, str)
    actualizarJuegoSignal = pyqtSignal(dict)
    resultadoPuzzleSignal = pyqtSignal(bool)
    finJuegoSignal = pyqtSignal(str)

    def __init__(self, host):
        super().__init__()
        self.host = host
        self.port = 8000
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ranking = []

    # Empieza el backend
    def empezar(self):
        # Conectamos con el servisor
        # self.conectar_al_servidor()
        
        # Obtenemos el ranking 
        self.obtener_ranking()
        
        # Empezamos la ventana_de_inicio
        self.empezar_ventana_de_inicio()

    def empezar_ventana_de_inicio(self):
        ranking_ordenadao = self.ordenar_ranking()
        self.senal_empezar_VentanaInicio.emit(ranking_ordenadao)

    def guardar_ranking(self, usuario, puntaje):
        with open("puntaje.txt", "w") as archivo:
            for usuario, valor in self.ranking:
                archivo.write(usuario + ";" + str(valor) + "\n")
    
    def obtener_ranking(self):
        try:
            directorio_actual = os.path.dirname(__file__)
            ruta_puntaje = os.path.join(directorio_actual, "puntaje.txt")
            with open(ruta_puntaje, "r") as archivo:
                rankings = archivo.readlines()
                if len(rankings) != 0:
                    for ranking in rankings:
                        usuario, puntaje = ranking.split(";")
                        self.ranking.append((usuario, int(puntaje)))
        except FileNotFoundError:
            print("No existe puntaje.txt en cliente")

    def ordenar_ranking(self):
        ranking_formateado = []
        self.ranking.sort(key= lambda x: x[1], reverse=True)
        for usuario, puntaje in self.ranking:
            ranking_formateado.append(usuario + " - " + str(puntaje))
        return ranking_formateado

    def conectar_al_servidor(self):
        self.socket.connect((self.host, self.port))
        thread = Thread(target=self.escuchar_servidor)
        thread.start()

    def escuchar_servidor(self):
        while True:
            data = self.socket.recv(1024)
            if data:
                mensaje = json.loads(data.decode('utf-8'))
                self.procesar_mensaje(mensaje)

    def iniciar_juego(self, usuario, puzzle):
        patron = r'^(?=.*[A-Z])(?=.*\d).+$'
        if usuario == "":
            self.senal_popup.emit("Ingrese un nombre de usuario")
        elif not usuario.isalnum():
            self.senal_popup.emit("El nombre de usuario solo debe contener letras y números")
        elif not re.match(patron, usuario):
            self.senal_popup.emit("El nombre de usuario debe contener al menos una mayúscula y un número")
        elif puzzle == "":
            self.senal_popup.emit("Debe seleccionar un puzzle")
        else:
            self.usuario_actual = usuario
            self.puzzle_actual = puzzle
            self.senal_iniciar_juego.emit(usuario, puzzle)

    def obtener_numeros_puzzle(self, archivo_puzzle):
        with open(f"{archivo_puzzle}.txt", 'r') as archivo:
            numeros_columnas = [columna.split(",") for columna in archivo.readline().split(";")]
            numeros_filas = [fila.split(",") for fila in archivo.readline().split(";")]

        return numeros_columnas, numeros_filas

    def obtener_controlador_sandias(self, numero_columnas):
        return ControladorSandias(numero_columnas)

    def obtener_controlador_tiempo(self):
        return ControladorTiempo()

    def procesar_mensaje(self, mensaje):
        # Procesa el mensaje recibido del servidor
        pass

    def comprobar_puzzle(self, informacion_puzzle):
        informacion_puzzle = informacion_puzzle[:-1]
        self.enviar_puzzle(informacion_puzzle)

    def enviar_puzzle(self, puzzle):
        data = json.dumps(puzzle).encode('utf-8')
        largo_archivo = len(data).to_bytes(4, byteorder="big")
        self.socket.sendall(largo_archivo)

        bytes_enviados = 0
        while bytes_enviados < largo_archivo:
            # Enviaremos el mensaje cortado desde el último punto efectivamente enviado.
            bytes_enviados += sock.send(datos[bytes_enviados:])
