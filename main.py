# from machine import Pin, PWM, I2C, UART
# import machine
# import os
# import sdcard
# import time
# import sys
# import math
# from bmp180 import BMP180
# from _thread import start_new_thread
# from micropyGPS import MicropyGPS

# uart1 = UART(2, baudrate=9600, tx=17, rx=16)

# sg90 = PWM(Pin(15, mode=Pin.OUT))
# sg90.freq(50)
# sg90.duty(25)
# time.sleep(1)

# bus = I2C(scl=Pin(22), sda=Pin(21), freq=100000)
# bmp180 = BMP180(bus)
# bmp180.oversample_sett = 2
# bmp180.baseline = 101325

# temp = bmp180.temperature
# p = bmp180.pressure
# altitude = bmp180.altitude
# print(temp, p, altitude)

# utc_time = ""
# latitud = ""
# longitud = ""
# satelites = ""
# gps = MicropyGPS()

# spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(
#     18), mosi=Pin(23), miso=Pin(19))

# cs = machine.Pin(5, Pin.OUT)

# sd = sdcard.SDCard(spi, cs)

# os.mount(sd, "/sd")

# filename = '/sd/data.csv'
# with open(filename, 'w') as file:
#     file.write('Tiempo, Altura, presion, temperatura, latitud, longitud\n')

# altura_inicio = int(bmp180.altitude)
# estado = 0
# paracaidas_activado = False


# def activar_paracaidas():
#     sg90.duty(170)
#     time.sleep(1)
#     with open(filename, 'a') as f:
#         f.write(str(time.time()) + "," + "Activar paracaidas\n")


# def almacenar_estados(altura_actual):
#     with open(filename, 'a') as f:
#         f.write(str(time.time()) + "," + str(int(altura_actual)) + "," +
#                 str(int(altura_actual)) + "," + str(int(altura_actual)) + "\n")
#         print("Estado almacenado", altura_actual)


# def gps_data():
#     buf = uart1.readline()
#     if uart1.any():
#         for char in buf:
#             gps.update(chr(char))

#     print("hora", gps.timestamp)
#     print("latitud", gps.latitude_string())
#     print("longitud",  gps.longitude_string())
#     print("satelites", gps.satellites_in_use)
#     print(temp, p, altitude)


# def toma_datos():
#     while True:
#         with open(filename, 'a') as f:
#             f.write(str(time.time()) + ","
#                     + str(int(bmp180.altitude)) + ","
#                     + str(int(bmp180.pressure)) + ","
#                     + str(int(bmp180.temperature)) + ","
#                     + str((gps.latitude_string())) + ","
#                     + str((gps.longitude_string())) + "\n")
#             print("Dato almacenado")
#         time.sleep(1)


# start_new_thread(toma_datos, ())

# while True:
#     altura_actual = int(bmp180.altitude)
#     print(altura_actual)

#     try:
#         gps_data()
#         if altura_actual >= 10000 and estado == 0:
#             almacenar_estados(altura_actual)
#             print("Estado 0")
#             with open(filename, 'a') as f:
#                 f.write(str(time.time()) + "," +
#                         str(int(altura_actual)) + ", estado = 1" + "\n")

#             estado = 1
#         elif altura_actual >= 15000 and estado == 1:
#             almacenar_estados(altura_actual)
#             print("Estado 1")
#             with open(filename, 'a') as f:
#                 f.write(str(time.time()) + "," +
#                         str(int(altura_actual)) + ", estado = 2" + "\n")

#             estado = 2
#         elif altura_actual >= 20000 and estado == 2:
#             almacenar_estados(altura_actual)
#             print("Estado 2")
#             with open(filename, 'a') as f:
#                 f.write(str(time.time()) + "," +
#                         str(int(altura_actual)) + ", estado = 3" + "\n")
#             estado = 3
#         elif altura_actual >= 25000 and estado == 3:
#             almacenar_estados(altura_actual)
#             print("Estado 3")
#             with open(filename, 'a') as f:
#                 f.write(str(time.time()) + "," +
#                         str(int(altura_actual)) + ", estado = 4" + "\n")
#             estado = 4
#         elif altura_actual <= 22000 and estado == 4 and paracaidas_activado == False:
#             almacenar_estados(altura_actual)
#             paracaidas_activado = True
#             activar_paracaidas()
#             print("Estado Final")
#             os.umount("/sd")

#         time.sleep(1)
#     except:
#         print("An exception occurred")
#         raise

import machine
import time
import os
import sdcard
from machine import UART, Pin, I2C
from micropyGPS import MicropyGPS
from lora_e220 import LoRaE220, Configuration
from lora_e220_constants import FixedTransmission, RssiEnableByte
from lora_e220_operation_constant import ResponseStatusCode
from _thread import start_new_thread
from bmp180 import BMP180


bus = I2C(scl=Pin(22), sda=Pin(21), freq=100000)
bmp180 = BMP180(bus)
bmp180.oversample_sett = 2
bmp180.baseline = 101325

temp = bmp180.temperature
p = bmp180.pressure
altitude = bmp180.altitude
print(temp, p, altitude)

# _______________________________________________________________________________
latitud = ""
longitud = ""
timestamp = ""
satellites = ""
altura = ""
gps = MicropyGPS()

uart2 = UART(2, baudrate=9600, tx=17, rx=16)
uart1 = UART(1, baudrate=9600, tx=32, rx=33)
# _______________________________________________________________________________

lora = LoRaE220('400T30D', uart2, aux_pin=13, m0_pin=12, m1_pin=14)
code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))
code, configuration = lora.get_configuration()
print("Retrieve configuration: {}", ResponseStatusCode.get_description(code))
# _______________________________________________________________________________
spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(
    18), mosi=Pin(23), miso=Pin(19))

cs = machine.Pin(5, Pin.OUT)
sd = sdcard.SDCard(spi, cs)
os.mount(sd, "/sd")

filename = '/sd/data.csv'
with open(filename, 'w') as file:
    file.write(
        'timestamp, latitud, longitud, satellites, altura, Altura, Presion, temperatura\n')
# _______________________________________________________________________________


def toma_datos():
    while True:
        with open(filename, 'a') as f:
            f.write(":".join(map(str, timestamp)) + ","
                    + str(latitud) + ","
                    + str(longitud) + ","
                    + str(satellites) + ","
                    + str(altura) + ","
                    + str((bmp180.altitude)) + ","
                    + str((bmp180.pressure)) + ","
                    + str((bmp180.temperature))+"\n")


start_new_thread(toma_datos, ())


def gps_data():
    global latitud
    global longitud
    global timestamp
    global satellites
    global altura
    buf = uart1.readline()
    if uart1.any():
        for char in buf:
            gps.update(chr(char))

    latitud = gps.latitude_string()
    longitud = gps.longitude_string()
    timestamp = gps.timestamp
    satellites = gps.satellites_in_use
    altura = gps.altitude


while True:
    gps_data()
    message = "Latitud: {}\r\nLongitud: {}\r\nHora: {}\r\nSatélites: {}\r\naltura: {}\r\nAltura: {}\r\nPresion: {}\r\ntemperatura: {}\r\n".format(
        latitud,
        longitud,
        timestamp,
        satellites,
        altura,
        str((bmp180.altitude)),
        str((bmp180.pressure)),
        str((bmp180.temperature))
    )
    code = lora.send_transparent_message(message)
    print("Send message: {}", ResponseStatusCode.get_description(code))
    print(message)
    time.sleep(2)
