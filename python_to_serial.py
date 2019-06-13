import serial
import struct
from time import sleep

COM_PORT = 'COM4' #ENTER COM PORT HERE
BAUD_RATE= '9600' #ENTER BAUD RATE HERE' 

arduino = serial.Serial(COM_PORT,BAUD_RATE)

arduino.write(struct.pack("B",255))
sleep(5)

#while True:
    # a = 235
    # for i in range(5):
    #     arduino.write(struct.pack("B",a + (i*5) ))
    #     print(a + i * 5)
    #     sleep(1)

while True:
    arduino.write(struct.pack("B",230))
    sleep(1)