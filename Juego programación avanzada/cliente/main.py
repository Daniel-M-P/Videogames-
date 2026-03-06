import sys
import os
import json
import frontend.constantes_frontend as c
from PyQt6.QtWidgets import QApplication
from frontend.ventana_principal import VentanaPrincipal
from frontend.ventana_juego import VentanaJuego
from backend.logica import Logica

class Cliente:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        with open("data.json", "r") as file:
            config = json.load(file)
            self.host = config["host"]


        self.logica = Logica(self.host)
        self.ventana_principal = VentanaPrincipal()
        self.ventana_juego = VentanaJuego()

    def conectar(self):
        self.logica.senal_empezar_VentanaInicio.connect(self.ventana_principal.empezar)
        self.logica.senal_popup.connect(self.ventana_principal.mostrar_popup)
        self.logica.senal_iniciar_juego.connect(self.iniciar_juego)

        self.ventana_principal.senal_iniciar_juego.connect(self.logica.iniciar_juego)
        self.ventana_principal.senal_salir.connect(self.salir)

        self.ventana_juego.senal_salir.connect(self.salir)
        # self.ventana_juego.verificarSignal.connect(self.verificar_puzzle)
        # self.ventana_juego.cerrarSignal.connect(self.cerrar_juego)

    def iniciar(self):
        # Conectamos frontend-backend
        self.conectar()

        # Iniciamos el backend
        self.logica.empezar()
        sys.exit(self.app.exec())

    def iniciar_juego(self, usuario, puzzle):
        # Inicia el juego con el usuario y puzzle seleccionados
        self.ventana_principal.close()
        self.ventana_principal.musica_fondo.stop()
        archivo_puzzle = os.path.join(c.RUTA_PUZZLES, puzzle)
        numeros_columnas, numeros_filas = self.logica.obtener_numeros_puzzle(archivo_puzzle)

        self.ventana_juego.empezar(usuario, numeros_columnas, numeros_filas, puzzle)
        self.controlador_sandias = self.logica.obtener_controlador_sandias(len(numeros_columnas))
        self.controlador_sandias.senal_aparecer_sandia.connect(self.ventana_juego.puzzle_widget.aparecer_sandia)
        self.controlador_sandias.senal_desaparecer_sandia.connect(self.ventana_juego.puzzle_widget.desaparecer_sandia)

        self.controlador_tiempo = self.logica.obtener_controlador_tiempo()
        self.controlador_tiempo.senal_actualizar_tiempo.connect(self.ventana_juego.actualizar_tiempo)

        for cuadrado in self.ventana_juego.puzzle_widget.grid_cuadrados.values():
            cuadrado.senal_anadir_tiempo.connect(self.controlador_tiempo.anadir_tiempo)

        self.ventana_juego.senal_pausar_juego.connect(self.pausar_juego)
        self.ventana_juego.senal_reanudar_juego.connect(self.reanudar_juego)
        self.ventana_juego.senal_comprobar_puzzle.connect(self.logica.comprobar_puzzle)
        # self.controlador_tiempo.senal_terminar_juego.connect(self.ventana_juego.puzzle_widget.terminar_juego)

    def pausar_juego(self):
        self.controlador_sandias.pausar()
        self.controlador_tiempo.pausar()

    def reanudar_juego(self):
        self.controlador_sandias.reanudar()
        self.controlador_tiempo.reanudar()

    def salir(self):
        self.app.quit()

    def verificar_puzzle(self):
        # Lógica para verificar el puzzle
        pass

    def cerrar_juego(self):
        # Lógica para cerrar el juego
        self.ventana_juego.close()
        self.ventana_juego.musica_fondo.stop()
        self.ventana_principal.show()

if __name__ == "__main__":
    cliente = Cliente()
    cliente.iniciar()
