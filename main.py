import machine
import bme280_float as bme280
import time
import sdcard
import os
import csv

i2c = machine.I2C(0, sda=machine.Pin(21), scl=machine.Pin(22))
bme = bme280.BME280(i2c=i2c)

spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0)
cs = machine.Pin(5, machine.Pin.OUT)
sd = sdcard.SDCard(spi, cs)

# Configurar el archivo CSV
filename = '/sdcard/data.csv'
if 'data.csv' not in os.listdir('/sdcard'):
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Altura'])

# Leer la altura cada 30 segundos y escribirla en el archivo CSV
altura_inicio = bme.altitude  # Función para leer la altura inicial del experimento
estado = 0
paracaidas_activado = False

def activar_paracaidas():
    with open(filename, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([time.time(), "Activar paracaidas"])

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
        break
    with open(filename, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([time.time(), altura_actual])
    time.sleep(30)
