import serial
import struct
from time import sleep

COM_PORT = 'COM4' #ENTER COM PORT HERE
BAUD_RATE= '9600' #ENTER BAUD RATE HERE' 

arduino = serial.Serial(COM_PORT,BAUD_RATE)

while True:
    a = 235
    for i in range(2):
        if i == 0:
            arduino.write(struct.pack("B",7))
            sleep(0.7)
        else:
            arduino.write(struct.pack("B",15))
            sleep(0.45)
        