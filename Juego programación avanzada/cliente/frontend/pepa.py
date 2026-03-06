import os
import frontend.constantes_frontend as c
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QTimer, QMutex, QUrl
from PyQt6.QtMultimedia import QSoundEffect

class Pepa(QLabel):
    def __init__(self, parent, numero_columnas):
        super().__init__(parent)
        self.tamano = c.TAMANO_CUADRADOS
        self.setFixedSize(self.tamano, self.tamano)
        self.numero_columnas = numero_columnas
        self.columna_actual = 0
        self.fila_actual = 0
        self.maximo = numero_columnas

        self.poop_wav = QSoundEffect(parent)
        poop_url = QUrl.fromLocalFile(os.path.join(c.RUTA_SONIDOS, "poop.wav"))
        self.poop_wav.setSource(poop_url)
        self.poop_wav.setVolume(10)

        self.comer_wav = QSoundEffect(parent)
        comer_url = QUrl.fromLocalFile(os.path.join(c.RUTA_SONIDOS, "comer.wav"))
        self.comer_wav.setSource(comer_url)
        self.comer_wav.setVolume(10)

        sprites = {
            'down': [os.path.join(c.RUTA_PEPA, f"down_{i}.png") for i in range(4)],
            'up': [os.path.join(c.RUTA_PEPA, f"up_{i}.png") for i in range(4)],
            'left': [os.path.join(c.RUTA_PEPA, f"left_{i}.png") for i in range(4)],
            'right': [os.path.join(c.RUTA_PEPA, f"right_{i}.png") for i in range(4)]
        }


        # Escalamos los sprites y los guardamos
        self.sprites = {
            'down': [QPixmap(sprite).scaled(self.tamano, self.tamano, Qt.AspectRatioMode.KeepAspectRatio) for sprite in sprites['down']],
            'up': [QPixmap(sprite).scaled(self.tamano, self.tamano, Qt.AspectRatioMode.KeepAspectRatio) for sprite in sprites['up']],
            'left': [QPixmap(sprite).scaled(self.tamano, self.tamano, Qt.AspectRatioMode.KeepAspectRatio) for sprite in sprites['left']],
            'right': [QPixmap(sprite).scaled(self.tamano, self.tamano, Qt.AspectRatioMode.KeepAspectRatio) for sprite in sprites['right']]
        }

        # Establecer pixmap y posicion inicial
        self.direccion_actual = "down"  # Dirección inicial de la tortuga
        self.sprite_index = 0
        self.setPixmap(self.sprites[self.direccion_actual][self.sprite_index])

        # QTimer para manejar la actualización de los sprites
        self.animacion = QTimer()
        self.animacion.timeout.connect(self.actualizar_sprite)

        # QMutex para bloquear el desplazamiento
        self.mutex = QMutex()

    def actualizar_sprite(self):
        self.sprite_index = (self.sprite_index + 1) % len(self.sprites[self.direccion_actual])
        self.setPixmap(self.sprites[self.direccion_actual][self.sprite_index])

    def sonido_poop(self):
        self.poop_wav.play()

    def sonido_comer(self):
        self.comer_wav.play()

    def mover(self, direccion, offset):
        verificar_limite = {
            'up': lambda: self.fila_actual > 0,
            'down': lambda: self.fila_actual < self.maximo - 1,
            'left': lambda: self.columna_actual > 0,
            'right': lambda: self.columna_actual < self.maximo - 1
        }

        # Limitamos el movimiento si se termino el movimiento anterior y si está dentro dle limite
        if not verificar_limite[direccion]() or not self.mutex.tryLock():
            return

        actualizar_coordenadas = {
            "up": lambda: setattr(self, 'fila_actual', self.fila_actual - 1),
            "down": lambda: setattr(self, 'fila_actual', self.fila_actual + 1),
            "left": lambda: setattr(self, 'columna_actual', self.columna_actual - 1),
            "right": lambda: setattr(self, 'columna_actual', self.columna_actual + 1)
        }

        actualizar_coordenadas[direccion]()

        self.direccion_actual = direccion
        self.posicion = QPoint(self.geometry().x(), self.geometry().y())
        self.nueva_posicion = self.posicion + offset
        
        self.desplazamiento = QPropertyAnimation(self, b"pos")
        self.desplazamiento.setDuration(c.TIEMPO_DESPLAZAMIENTO) 
        self.desplazamiento.setStartValue(self.posicion)
        self.desplazamiento.setEndValue(self.nueva_posicion)
        self.desplazamiento.finished.connect(self.desplazamiento_terminado)

        self.desplazamiento.start()
        self.animacion.start(c.TIEMPO_ANIMACION)

    def desplazamiento_terminado(self):
        self.animacion.stop()
        self.setPixmap(self.sprites[self.direccion_actual][0])
        self.posicion = self.nueva_posicion

        self.mutex.unlock()

