# import machine
# from machine import Pin, PWM, I2C
# import os
# import sdcard
# import time
# from _thread import start_new_thread
# import lib.bmp180 as bme
# import sys
# from bmp180 import BMP180

# from machine import Pin, UART, SoftI2C
# import math
# from micropyGPS import MicropyGPS
# uart = UART(2, baudrate=9600)

# sg90 = PWM(Pin(15, mode=Pin.OUT))
# sg90.freq(50)

# sg90.duty(25)
# time.sleep(1)

# bus = I2C(sda=Pin(21), scl=Pin(22), freq=100000)
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


# def gps_data():
#     buf = uart.readline()
#     if uart.any():
#         for char in buf:
#             gps.update(chr(char))

#     print("hora", gps.timestamp)
#     print("latitud", gps.latitude_string())
#     print("longitud",  gps.longitude_string())
#     print("satelites", gps.satellites_in_use)


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


from loraE22 import ebyteE22
import machine
from machine import Pin
import utime
import ubinascii

me   = 0
peer = 1
addr = [0x0000, 0x0001]
chan = [0x00, 0x00]

M0pin = 25
M1pin = 26
AUXpin = 14

e22 = ebyteE22(M0pin, M1pin, AUXpin, Port='U2', Address=addr[me], Channel=chan[me], debug=False)

unique_id = ubinascii.hexlify(machine.unique_id()).decode("ascii")

e22.config['rssi'] = 1

e22.start()

msg_no = 0
while True:
    message = "ESP32 ID: {} / MsgNo: {}".format(unique_id, msg_no)
    tx_msg = { 'msg': message }
    print('Node %d TX: address %d - channel %d - message %s'%(me, addr[peer], chan[peer], tx_msg))
    e22.sendMessage(addr[peer], chan[peer], tx_msg, useChecksum=True)
    msg_no += 1
    utime.sleep_ms(2000)

e22.stop()