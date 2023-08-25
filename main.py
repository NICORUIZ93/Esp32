import machine
import os
import sdcard
import time
from _thread import start_new_thread
import lib.bme280_float as bme
import sys


i2c = machine.I2C(0, sda=machine.Pin(21), scl=machine.Pin(22))
bme = bme.BME280(i2c=i2c)

# Crear objeto SPI
spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0, sck=machine.Pin(
    18), mosi=machine.Pin(23), miso=machine.Pin(19))

# Crear objeto Pin para el pin CS
cs = machine.Pin(5, machine.Pin.OUT)

# Crear objeto SDCard
sd = sdcard.SDCard(spi, cs)

# Montar la tarjeta SD
os.mount(sd, "/sd")

# Configurar el archivo CSV
filename = '/sd/data.csv'
with open(filename, 'w') as file:
    file.write('Timestamp,Data\n')

# Leer la altura cada 30 segundos y escribirla en el archivo CSV
# Función para leer la altura inicial del experimento
altura_inicio = int(bme.altitude)
estado = 0
paracaidas_activado = False


def activar_paracaidas():
    with open(filename, 'a') as f:
        f.write(str(time.time()) + "," + "Activar paracaidas\n")


def almacenar_estados(altura_actual):
    with open(filename, 'a') as f:
        f.write(str(time.time()) + "," + str(int(altura_actual)) + "\n")
        print("Estado almacenado", altura_actual)


def toma_datos():
    while True:
        altura_actual = int(bme.altitude)
        with open(filename, 'a') as f:
            f.write(str(time.time()) + "," + str(int(altura_actual)) + "\n")
            print("Dato almacenado")
        time.sleep(1)


start_new_thread(toma_datos, ())

while True:
    altura_actual = int(bme.altitude)
    print(altura_actual)

    if altura_actual >= (altura_inicio + 50) and estado == 0:
        almacenar_estados(altura_actual)
        print("Estado 0")
        estado = 1
    elif altura_actual >= (altura_inicio + 100) and estado == 1:
        almacenar_estados(altura_actual)
        print("Estado 1")
        estado = 2
    elif altura_actual >= (altura_inicio + 150) and estado == 2:
        almacenar_estados(altura_actual)
        print("Estado 2")
        estado = 3
    elif altura_actual >= (altura_inicio + 200) and estado == 3:
        almacenar_estados(altura_actual)
        print("Estado 3")
        estado = 4
    elif altura_actual < (altura_inicio + 160) and estado == 4 and paracaidas_activado == False:
        almacenar_estados(altura_actual)
        paracaidas_activado = True
        activar_paracaidas()
        print("Estado Final")
        os.umount("/sd")
        sys.exit()

    time.sleep(1)
