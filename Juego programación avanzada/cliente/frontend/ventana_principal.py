from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QComboBox,
    QPushButton, QListWidget, QScrollArea, QListWidgetItem, QMessageBox
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QUrl
from PyQt6.QtMultimedia import QSoundEffect
import frontend.constantes_frontend as c
import os


class SalonDeFama(QWidget):
    def __init__(self, ranking=list):
        super().__init__()
        # Definimos el layout
        self.layout = QVBoxLayout()

        # Creamos el título
        titulo = QLabel("Salón de la fama")
        titulo.setFont(QFont("Arial", 24))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(titulo)

        # Creamos el ranking
        self.lista_rankings = QListWidget()
        for puntaje in ranking:
            item = QListWidgetItem(puntaje)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lista_rankings.addItem(item)
        self.lista_rankings.setFont(QFont("Arial", 16))

        # Creamos el Scroll
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.lista_rankings)
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)
        self.setLayout(self.layout)


class VentanaPrincipal(QMainWindow):
    senal_iniciar_juego = pyqtSignal(str, str)
    senal_salir = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DCCome Lechuga")
        self.setGeometry(100, 100, 1200, 750)

    def empezar(self, ranking):
        # Crear el layout principal
        layout_principial = QHBoxLayout()

        # Añadir el Salon de Fama
        salon_de_fama = SalonDeFama(ranking)
        layout_principial.addWidget(salon_de_fama)

        # Añadir la columna de la derecha
        layout_principial.addWidget(self.crear_columna_derecha())

        # Establecer el layout principal
        central_widget = QWidget()
        central_widget.setLayout(layout_principial)
        self.setCentralWidget(central_widget)

        # Aplicar estilos
        self.aplicar_estilos()

        # Crear Musica
        self.musica_fondo = QSoundEffect()
        self.musica_fondo.setSource(QUrl.fromLocalFile(os.path.join(c.RUTA_SONIDOS, "musica_1.wav")))
        self.musica_fondo.setLoopCount(1000 * 55)
        self.musica_fondo.setVolume(10)
        self.musica_fondo.play()
        
        # Mostrar
        self.show()

    def crear_columna_derecha(self):
        columna_derecha = QWidget()
        layout_columna = QVBoxLayout()
        
        # Añadir el logo
        logo_label = QLabel()
        ruta_logo = os.path.join(c.RUTA_SPRITES, "logo.png")
        pixmap = QPixmap(ruta_logo)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_columna.addWidget(logo_label)

        # Nombre de usuario
        usuario_label = QLabel("Nombre de Usuario")
        usuario_label.setFont(QFont("Arial", 16))
        layout_columna.addWidget(usuario_label)

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Nombre de Usuario")
        layout_columna.addWidget(self.input_usuario)

        # Seleccion Puzzle
        puzzle_label = QLabel("Selecciona Puzzle")
        puzzle_label.setFont(QFont("Arial", 16))
        layout_columna.addWidget(puzzle_label)

        self.lista_puzzles = QComboBox()
        dificultades = os.listdir(c.RUTA_PUZZLES)
        self.lista_puzzles.addItem("")
        self.lista_puzzles.addItems([puzzle[:-4] for puzzle in dificultades])
        layout_columna.addWidget(self.lista_puzzles)

        # Botones de Jugar y Salir
        button_layout = QHBoxLayout()
        boton_iniciar = QPushButton("Jugar")
        boton_salir = QPushButton("Salir")
        button_layout.addWidget(boton_iniciar)
        button_layout.addWidget(boton_salir)

        boton_iniciar.clicked.connect(self.iniciar_juego)
        boton_salir.clicked.connect(self.salir)
        
        layout_columna.addLayout(button_layout)

        columna_derecha.setLayout(layout_columna)
        return columna_derecha

    def aplicar_estilos(self):
        # Aplicar estilos

        self.setStyleSheet(f"""
            VentanaPrincipal {{
                background-color: {c.COLOR_FONDO};
            }}
            QPushButton {{
                font-size: 16px;
                padding: 10px;
                background-color: {c.COLOR_BOTONES};
                color: white;
            }}
            QLineEdit {{
                font-size: 16px;
                padding: 5px;
            }}
            QComboBox {{
                font-size: 16px;
                padding: 5px;
            }}
            QLabel {{
                color: {c.COLOR_LETRAS};
            }}
        """)

    def mostrar_popup(self, mensaje):
        # Crear el popup
        self.popup = QMessageBox(self)
        self.popup.setWindowTitle("Popup")
        self.popup.setText(mensaje)
        self.popup.setIcon(QMessageBox.Icon.Information)

        # Mostrar el popup
        self.popup.show()

        # Timer que cierre el popup después de 5 segundos
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cerrar_popup)
        self.timer.setSingleShot(True)
        self.timer.start(5000) 

    def cerrar_popup(self):
        self.popup.close()
    
    def iniciar_juego(self):
        usuario = self.input_usuario.text()
        puzzle = self.lista_puzzles.currentText()
        self.senal_iniciar_juego.emit(usuario, puzzle)

    def salir(self):
        self.senal_salir.emit() 
