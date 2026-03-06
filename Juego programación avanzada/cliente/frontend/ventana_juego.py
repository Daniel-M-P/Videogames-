import os
import frontend.constantes_frontend as c
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QUrl
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtGui import QPixmap
from frontend.pepa import Pepa

class Cuadrado(QLabel):
    senal_anadir_tiempo = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.tamano = c.TAMANO_CUADRADOS
        self.setFixedSize(self.tamano, self.tamano)
        self.setStyleSheet(f"border: 1px solid {c.COLOR_FONDO};")
        lechuga_png = os.path.join(c.RUTA_SPRITES, "lechuga.png")
        self.lechuga_png = QPixmap(lechuga_png)

        sandia_png = os.path.join(c.RUTA_SPRITES, "sandia.png")
        self.sandia_png = QPixmap(sandia_png)

        caca_png = os.path.join(c.RUTA_SPRITES, "poop.png")
        self.caca_png = QPixmap(caca_png)

        self.sandia_wav = QSoundEffect(self)
        sandia_url = QUrl.fromLocalFile(os.path.join(c.RUTA_SONIDOS, "obtener_sandia.wav"))
        self.sandia_wav.setSource(sandia_url)
        self.sandia_wav.setVolume(10)

        self.hay_sandia = False

        # Ve donde y donde no hay lechuga, tiene que vaciar los lugares
        self.hay_lechuga = False
        self.hay_caca = False
        self.ser_lechuga()

    def ser_lechuga(self):
        self.hay_lechuga = True
        self.hay_caca = False
        self.setStyleSheet(f"""
            background-color: {c.COLOR_LETRAS};
        """)
        self.setPixmap(self.lechuga_png)
        self.setScaledContents(True)

    def desaparecer_lechuga(self):
        self.hay_lechuga = False
        self.clear()
        self.setStyleSheet(f"""
            background-color: {c.COLOR_FONDO}; 
            border: 1px solid {c.COLOR_FONDO};
        """)

    def ser_caca(self):
        self.hay_caca = True
        self.setPixmap(self.caca_png)
        transformacion = QTimer(self)
        transformacion.setSingleShot(True)
        transformacion.setInterval(c.TIEMPO_TRANSICION)
        transformacion.timeout.connect(self.ser_lechuga)
        transformacion.start()

    def desaparecer_sandia(self):
        self.hay_sandia = False
        if self.hay_lechuga:
            self.ser_lechuga()
        else:
            self.clear()
            self.setStyleSheet(f"""
                background-color: {c.COLOR_FONDO}; 
                border: 1px solid {c.COLOR_FONDO};
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.hay_sandia:
            self.senal_anadir_tiempo.emit()
            self.sandia_wav.play()
            self.desaparecer_sandia()

    def ser_sandia(self):
        self.hay_sandia = True
        self.setPixmap(self.sandia_png)
        self.setScaledContents(True)

class PuzzleWidget(QWidget):
    def __init__(self, filas, cols, numeros_filas, numeros_columnas, pepa):
        super().__init__()

        self.filas = filas
        self.cols = cols

        grid_layout = self.crear_grid(filas, cols, numeros_filas, numeros_columnas)
        grid_layout.addWidget(pepa, 1, 1)

        self.setLayout(grid_layout)

    def aparecer_sandia(self, numero_columna, numero_fila):
        cuadrado = self.grid_cuadrados[(numero_columna, numero_fila)]
        if cuadrado.hay_sandia == False:
            cuadrado.ser_sandia()

    def desaparecer_sandia(self, numero_columna, numero_fila):
        cuadrado = self.grid_cuadrados[(numero_columna, numero_fila)]
        if cuadrado.hay_sandia == True:
            cuadrado.desaparecer_sandia()

    def accion_g(self, numero_columna, numero_fila, pepa):
        cuadrado = self.grid_cuadrados[(numero_columna, numero_fila)]
        if cuadrado.hay_lechuga:
            pepa.sonido_comer()
            cuadrado.desaparecer_lechuga()
        elif cuadrado.hay_caca == False:
            pepa.sonido_poop()
            cuadrado.ser_caca()

    def informacion_puzzle(self):
        informacion_puzzle = ""
        for col in range(self.cols):
            columna = ""
            for fila in range(self.filas):
                cuadrado = self.grid_cuadrados[(col, fila)]
                if cuadrado.hay_lechuga:
                    columna += "1"
                else:
                    columna += "0"
            informacion_puzzle += columna + ";"
        return informacion_puzzle

    def crear_grid(self, filas, cols, numeros_filas, numeros_columnas):
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0) 

        # Esquina vacía
        empty_corner = QLabel()
        grid_layout.addWidget(empty_corner, 0, 0)

        # Columna de números superior
        for col in range(cols):
            col_label = QLabel("\n".join(numeros_columnas[col]))
            col_label.setAlignment(Qt.AlignmentFlag.AlignHCenter |  Qt.AlignmentFlag.AlignBottom)
            grid_layout.addWidget(col_label, 0, col + 1)

        # Fila de números laterales (izquierda) 
        for fila in range(filas):
            fila_label = QLabel(" ".join(numeros_filas[fila]))
            fila_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid_layout.addWidget(fila_label, fila + 1, 0)

        # Grid de los cuadrados
        self.grid_cuadrados = {}
        for fila in range(filas):
            for col in range(cols):
                cuadrado = Cuadrado()
                grid_layout.addWidget(cuadrado, fila + 1, col + 1)
                self.grid_cuadrados[(col, fila)] = cuadrado

        empty_corner2 = QLabel()
        grid_layout.addWidget(empty_corner2, 0, cols)

        return grid_layout


class VentanaJuego(QMainWindow):
    senal_salir = pyqtSignal()
    senal_anadir_tiempo = pyqtSignal(int)
    senal_pausar_juego = pyqtSignal()
    senal_reanudar_juego = pyqtSignal()
    senal_comprobar_puzzle = pyqtSignal(str)
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Puzzle Widget")
        self.setGeometry(100, 100, c.TAMANO_HORIZONTAL, c.TAMANO_VERTICAL)
                # Define fila and column hints

    
    def empezar(self, nombre_jugador, numeros_columnas, numeros_filas, puzzle_actual):

        # Creamos el layout principal
        layout_principal = QHBoxLayout()

        # Creamos el puzzle y lo añadimos a la columna izquierda
        self.columna_izquierda = QVBoxLayout()
        self.pausado = False
        n_puzzle = len(numeros_columnas)
        
        #Creamos a PEPA
        self.pepa = Pepa(self, n_puzzle)
        self.puzzle_widget = PuzzleWidget(n_puzzle, n_puzzle, numeros_filas, numeros_columnas, self.pepa)
        self.columna_izquierda.addWidget(self.puzzle_widget)
        layout_principal.addLayout(self.columna_izquierda)

        # Creamos la columna derecha
        columna_derecha = QVBoxLayout()

        # Creamos el contador
        self.contador = QLabel()
        self.contador.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # Creamos el nombre del jugador
        self.nombre_jugador = QLabel(f"<h2>Jugador actual:</h2><h3>{nombre_jugador}</h3>")
        self.nombre_jugador.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.puzzle_actual = QLabel(f"<h2>Puzzle actual:</h2><h3>{puzzle_actual}</h3>")
        self.puzzle_actual.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # Creamos y conectamos los botones
        boton_comprobar = QPushButton("Comprobar Puzzle")
        boton_pausar = QPushButton("Pausar")
        boton_salir = QPushButton("Salir")
        boton_comprobar.clicked.connect(self.comprobar_puzzle)
        boton_pausar.clicked.connect(self.pausar_juego)
        boton_salir.clicked.connect(self.salir)

        # Añadimos los botones y el contador a la columna derecha
        columna_derecha.addWidget(self.contador)
        columna_derecha.addWidget(self.nombre_jugador)
        columna_derecha.addWidget(self.puzzle_actual)
        columna_derecha.addWidget(boton_pausar)
        columna_derecha.addWidget(boton_comprobar)
        columna_derecha.addWidget(boton_salir)
        layout_principal.addLayout(columna_derecha)

        # Establecer el layout principal
        central_widget = QWidget()
        central_widget.setLayout(layout_principal)
        self.setCentralWidget(central_widget)

        # Crear Musica
        self.musica_fondo = QSoundEffect()
        self.musica_fondo.setSource(QUrl.fromLocalFile(os.path.join(c.RUTA_SONIDOS, "musica_1.wav")))
        self.musica_fondo.setLoopCount(1000 * 55)
        self.musica_fondo.setVolume(10)
        self.musica_fondo.play()

        # Aplicamos estilos
        self.aplicar_estilos()
        self.show()

    def keyPressEvent(self, event):
        # Crear un lock para el moviemiento
        if self.pausado == False:
            if event.key() == Qt.Key.Key_W:
                self.pepa.mover('up', QPoint(0, -c.TAMANO_CUADRADOS))
            elif event.key() == Qt.Key.Key_S:
                self.pepa.mover('down', QPoint(0, c.TAMANO_CUADRADOS))
            elif event.key() == Qt.Key.Key_A:
                self.pepa.mover('left', QPoint(-c.TAMANO_CUADRADOS, 0))
            elif event.key() == Qt.Key.Key_D:
                self.pepa.mover('right', QPoint(c.TAMANO_CUADRADOS, 0))
            if event.key() == Qt.Key.Key_G:
                columna = self.pepa.columna_actual
                fila = self.pepa.fila_actual
                self.puzzle_widget.accion_g(columna, fila, self.pepa)


    def actualizar_tiempo(self, texto):
        self.contador.setText(texto)

    def comprobar_puzzle(self):
        informacion_puzzle = self.puzzle_widget.informacion_puzzle()
        self.senal_comprobar_puzzle.emit(informacion_puzzle)


    def pausar_juego(self):
        if self.pausado == False:
            self.puzzle_widget.setVisible(False)
            self.musica_fondo.stop()
            self.senal_pausar_juego.emit()
            self.contador.setText("<h2>Juego Pausado</h2>")
            self.pausado = True
        
        else:
            self.puzzle_widget.setVisible(True)
            self.musica_fondo.play()
            self.senal_reanudar_juego.emit()
            self.pausado = False

        self.columna_izquierda.update()

    def salir(self):
        self.senal_salir.emit()


    def aplicar_estilos(self):
        self.setStyleSheet(f"""
            VentanaJuego {{
                background-color: {c.COLOR_FONDO};
            }}
            QLabel {{
                color: {c.COLOR_LETRAS};
                font-size: 16px;
                padding: 2px;
            }}
            QPushButton {{
                font-size: 16px;
                padding: 10px;
                background-color: {c.COLOR_BOTONES};
                color: white;
            }}
        """)
