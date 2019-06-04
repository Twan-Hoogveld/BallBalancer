import serial
from time import sleep

COM_PORT = 'COM4' #ENTER COM PORT HERE
BAUD_RATE= '9600' #ENTER BAUD RATE HERE' 

arduino = serial.Serial(COM_PORT,BAUD_RATE)

while True:
    arduino.write(str.encode('0'))
    sleep(1)
    arduino.write(str.encode('1'))
