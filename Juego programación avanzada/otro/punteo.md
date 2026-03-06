# Inicio

1. Ejecutar el servidor
2. Ejecutar el cliente

Networking: La ejecución del cliente **no debe depender de archivos en la carpeta del servidor, y la ejecución del servidor no debe depender de archivos y/o recursos en la carpeta del cliente**. 

# Jugador = Cliente

Jugador es una **instancia** de cliente
Cargos: 
- Enviar la información de los puzzles completados por el usuario al servidor
- Recibir e interpretar las respuestas y actualizaciones que envía el servidor
- Actualizar la interfaz gráfica de acuerdo a las respuestas que recibe del servidor

## Constantes

Ambos tiempos deben estar en segundos 

### del juego
TIEMPO_JUEGO = tiempo de juego total (regresivo)
TIEMPO_ADICIONAL = tiempo que se añade al tiempo de juego tras clickear una sandía

No es constante pero hay que registrar el
TIEMPO_UTILIZADO para resolver el puzzle, no es afectado por tiempo adicional (progresivo)

PUNTAJE_INF = en caso de usarse el cheatcode INF este sería el puntaje por defecto

### de entidades
TIEMPO_TRANSICION = tiempo en el que un popó se vuelve lechuga
TIEMPO_APARACION = cada cuanto aparece una sandía
TIEMPO_DURACION = cuanto dura la sandía en la ventana

## Archivos
`puntaje.txt`: Registra el puntaje asociado a un nombre de usuario, debe existir una línea por cada partida jugada. (extra mío: añadir la fecha y hora)

verificar que exista antes de crearlo

## Entidades: 
### PEPA
Desplazamiento **discreto**: no puede quedar entre dos casillas
Animación de movimiento **continua**: se debe ver fluida, 4 sprites
Quieto: Mostrar sprite estático

Casilla:
- `Llena`: Se come la lechuga y la deja vacía
- `Vacía`: Hace *poop* y deja una sprite de popó

Tras TIEMPO_TRANSICION el popó se vuelve lechuga insantaneamente.

### Sandía
Posición Aleatoria
Aparecen cada TIEMPO_APARICION
Captura resulta en TIEMPO_ADICIONAL
Duraran TIEMPO_DURACION


## Frontend / Gráficos

*Señales* entre back-end y front-end
*Threading* para modelar las interacciones en la interfaz

### Ventanta de Inicio
1. Logo DCCome Lechuga
2. **Línea de texto editable** para ingresar el nombre de usuario
   1. Nombre debe ser: alfanumérico, al menos una mayúscula y un número 
   2. En caso de error informar al cliente mediante un *pop up temporal*/mensaje de error ye l motivo
3. Menú **desplegable** para seleccionar el puzzle, solo se muestran los nombres en la carpeta base_puzzles
4. Salón Fama *ranking* de los mejores puntajes históricos guardados en el cliente, sección tipo **scroll**
   1. Se muestran en formato nombre_usuario - puntaje_obtenido (ordenados de manera descendente) centrado
5. **Botón** para comenzar partida (Solo válido si se escoge un puzzle y se ingresa un nombre de usuario)
6. **Botón** para salir del programa, se cierra la ventana y el programa
   
### Ventana de Juego
1. Puzzle:
   1. Tablero
   2. Números Columnas
   3. Números Filas
2. Estadísticas principales
   1. Tiempo Restante
   2. **Botón** para comprobar la solución
      1. Se avisa al jugador si es correcta o no
   3. **Botón** para pausar el juego
      1. Se detiene la cuenta regresiva, tiempo de las sandías, movimiento y animación de pepa
      2. Se oculta el tablero y los números
   4. **Botón** para salir del programa 
3. Mostrar *pop-up* en caso de victoria con puntaje final o de derrota

Se vuelve a la ventana principal 

#### Lógica
Se abre después de de ingresado un `nombre de usuario y puzzle válido`

- Usuario resuelve el puzzle seleccionado
- Revisa el tiempo restante para resolverlo

Se envía la solución a un servidor para validar si la respuesta es la correcta. 

`Correcta`: Se registrará el puntaje en `puntaje.txt` con el nombre de usuario y se le informa al jugador
`Invalida`: Se permitará que siga juegando por el tiempo que le quede y se le informa al jugador

- Si el tiempo se acaba se informa que **perdió por falta de tiempo** se vuelve a la ventana de inicio
- Si resuelve correctamente se vuelve a la ventana de inicio
- Si el usuario sale del programa antes de resolver el puzzle no se guarda la información de la partida

#### Visual
Tablero n x n
Números indica la cantidad de lechugas seguidas (una tras otra) por celda/columna

Si no hay lechugas se pone un guión (-)
Las casillas aparecen todas llenas (todas con lechugas)
El jugador mueve a Pepa para comerce las lechugas

## Backend
### Mecánicas
#### Puzzle
Enviar la información del puzzle al visual

#### Modo de juego
Movimiento WASD
Con G llena o vacia una celda
Sandías aparecen aliatoriamente, al hacer **click** suman TIEMPO_ADICIONAL al TIEMPO_JUEGO
Con F se pausa el juego (Se bloquea la vista e interacción con el tablero)
Botón de validación = envía la solución 

### CHEATCODES
Se presionan las teclas de forma simultánea o de manera consecutiva 

- I + N + F: esta combinación da tiempo infinito para completar el puzzle. En este caso el puntaje
del puzzle es por defecto PUNTAJE_INF.
- M + U + T + E: esta combinación desactiva el uso de todos los sonidos **durante la partida actual**,
perdiendo su efecto si se termina la partida y se empieza otra

#### Puntaje
Ver la fórmula del puntaje
Registrarlo en `puntaje.txt`

### Sonidos
Comer una lechuga -> comer.wav
Haga *poop* -> poop.wav
Click sandía -> obtener_sandia.wav
Juego ganado -> juego_ganado.wav
Juego_perdido -> juego_perdido.wav

Música de fondo -> musica_1.wac o musica_2.wav
¿Se puede poner música descargada de youtube?

# Networking

## Conexión
Archivo formato JSON con el host para instanciar el socket del servidor, en la capeta del servidor y otro en la de cliente

El port se obtiene como **argumento** de consola, verificar que este argumento sea un número valido entre los puertos posibles.

**Ver método de codificiación**

## Desconexión repentina
- Si es el servidor quien se desconecta, cada cliente conectado debe mostrar un mensaje en la ventana (ya sea como texto plano o pop-up) explicando la situación, antes de cerrar el programa.
- Si es un cliente quien se desconecta, se descarta su conexión y se muestra en consola un mensaje que indica lo anterior

# Servidor
Procesar y validar la solución del puzzle, se encuentran en la solución_puzzles



