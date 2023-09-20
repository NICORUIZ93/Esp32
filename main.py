import machine
from machine import Pin, PWM, I2C
import os
import sdcard
import time
from _thread import start_new_thread
import lib.bmp180 as bme
import sys
from bmp180 import BMP180

sg90 = PWM(Pin(15, mode=Pin.OUT))
sg90.freq(50)

sg90.duty(25)
time.sleep(1)


bus = I2C(sda=Pin(21), scl=Pin(22), freq=100000)   # on esp8266
bmp180 = BMP180(bus)
bmp180.oversample_sett = 2
bmp180.baseline = 101325

# temp = bmp180.temperature
# p = bmp180.pressure
# altitude = bmp180.altitude
# print(temp, p, altitude)

# Crear objeto SPI
spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(
    14), mosi=Pin(12), miso=Pin(13))

# Crear objeto Pin para el pin CS
cs = machine.Pin(27, Pin.OUT)

# Crear objeto SDCard
sd = sdcard.SDCard(spi, cs)

# Montar la tarjeta SD
os.mount(sd, "/sd")

# Configurar el archivo CSV
filename = '/sd/data.csv'
with open(filename, 'w') as file:
    file.write('Tiempo,Altura,presion,temperatura\n')

# Leer la altura cada 30 segundos y escribirla en el archivo CSV
# Función para leer la altura inicial del experimento
altura_inicio = int(bmp180.altitude)
estado = 0
paracaidas_activado = False


def activar_paracaidas():
    sg90.duty(170)
    time.sleep(1)
    with open(filename, 'a') as f:
        f.write(str(time.time()) + "," + "Activar paracaidas\n")


def almacenar_estados(altura_actual):
    with open(filename, 'a') as f:
        f.write(str(time.time()) + "," + str(int(altura_actual)) + "," +
                str(int(altura_actual)) + "," + str(int(altura_actual)) + "\n")
        print("Estado almacenado", altura_actual)


def toma_datos():
    while True:
        altura_actual = int(bmp180.altitude)
        with open(filename, 'a') as f:
            f.write(str(time.time()) + "," + str(int(bmp180.altitude)) + "," +
                    str(int(bmp180.pressure)) + "," + str(int(bmp180.temperature)) + "\n")
            print("Dato almacenado")
        time.sleep(1)


start_new_thread(toma_datos, ())

while True:
    altura_actual = int(bmp180.altitude)
    print(altura_actual)

    if altura_actual >= 10000 and estado == 0:
        almacenar_estados(altura_actual)
        print("Estado 0")
        with open(filename, 'a') as f:
            f.write(str(time.time()) + "," +
                    str(int(altura_actual)) + ", estado = 1" + "\n")

        estado = 1
    elif altura_actual >= 15000 and estado == 1:
        almacenar_estados(altura_actual)
        print("Estado 1")
        with open(filename, 'a') as f:
            f.write(str(time.time()) + "," +
                    str(int(altura_actual)) + ", estado = 2" + "\n")

        estado = 2
    elif altura_actual >= 20000 and estado == 2:
        almacenar_estados(altura_actual)
        print("Estado 2")
        with open(filename, 'a') as f:
            f.write(str(time.time()) + "," +
                    str(int(altura_actual)) + ", estado = 3" + "\n")
        estado = 3
    elif altura_actual >= 25000 and estado == 3:
        almacenar_estados(altura_actual)
        print("Estado 3")
        with open(filename, 'a') as f:
            f.write(str(time.time()) + "," +
                    str(int(altura_actual)) + ", estado = 4" + "\n")
        estado = 4
    elif altura_actual <= 22000 and estado == 4 and paracaidas_activado == False:
        almacenar_estados(altura_actual)
        paracaidas_activado = True
        activar_paracaidas()
        print("Estado Final")
        # os.umount("/sd")

    time.sleep(1)
