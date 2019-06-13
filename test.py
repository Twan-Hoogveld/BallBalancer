import serial
import struct
from time import sleep

COM_PORT = 'COM2' #ENTER COM PORT HERE
BAUD_RATE= '9600' #ENTER BAUD RATE HERE' 

arduino = serial.Serial(COM_PORT,BAUD_RATE)
arduino.write(struct.pack("B",255))
sleep(3)


while True:
    for i in range(2):
        if i == 0:
            arduino.write(struct.pack("B",4))
            sleep(0.80)
            print(".")
        else:
            arduino.write(struct.pack("B",12))
            sleep(0.25)
            print(",")
        
        