import machine
import os
import sdcard
import time
import lib.bme280_float as bme

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
altura_inicio = bme.altitude  # Función para leer la altura inicial del experimento
estado = 0
paracaidas_activado = False


def activar_paracaidas():
    with open(filename, 'a') as f:
        f.write(str(time.time()) + "," + "Activar paracaidas\n")


while True:
    # Función para leer la altura actual del experimento
    altura_actual = bme.altitude
    if altura_actual >= altura_inicio + 50 and estado == 0:
        estado = 1
    elif altura_actual >= altura_inicio + 100 and estado == 1:
        estado = 2
    elif altura_actual >= altura_inicio + 150 and estado == 2:
        estado = 3
    elif altura_actual < altura_inicio + 160 and estado == 3 and paracaidas_activado == False:
        paracaidas_activado = True
        activar_paracaidas()  # Función para activar el paracaídas
    if estado == 3 and paracaidas_activado == True:
        # Experimento completado
        os.umount("/sd")
        break

    with open(filename, 'a') as f:
        f.write(str(time.time()) + "," + str(int(altura_actual)) + "\n")
        print("Dato almacenado")
    time.sleep(5)
