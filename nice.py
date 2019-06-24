#python color_tracking.py --video balls.mp4
#python color_tracking.py

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import urllib #for reading image from URL
import serial
import struct
import time
#Aruino Setup
COM_PORT = 'COM4' #ENTER COM PORT HERE
BAUD_RATE= '9600' #ENTER BAUD RATE HERE' 
fan_speed = 0
arduino = serial.Serial(COM_PORT,BAUD_RATE)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the colors in the HSV color space
lower = {'green':(40, 35, 35),'orange':(0, 60, 87)} 
upper = {'green':(90,255,255), 'orange':(20,255,255)}

# define standard colors for circle around the object
colors = {'red':(0,0,255), 'green':(0,255,0), 'blue':(255,0,0), 'yellow':(0, 255, 217), 'orange':(0,140,255)}

# PID
green_setpoint_y = 0
orange_ball_y = 0

error_old = 0
kp = 0.3
ki = 0
kd = 0
ie = 0

def pid_control(ball_height, setpoint, delta_time = 0.02, ):
    global error_old
    global ie
    error_new = setpoint - ball_height
    delta_error = error_new - error_old
    ie += error_new * delta_time

    error_old = error_new
    total_action = kp * error_new + kd * (delta_error/delta_time)+ ki * ie 

    return int(total_action)


#pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture(1)


# otherwise, grab a reference to the video file
else:
    camera = cv2.VideoCapture(args["video"])
# keep looping
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if args.get("video") and not grabbed:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    #for each color in dictionary check object in frame
    for key, value in upper.items():
        # construct a mask for the color from dictionary`1, then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        kernel = np.ones((9,9),np.uint8)
        mask = cv2.inRange(hsv, lower[key], upper[key])
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size. Correct this value for your obect's size
            if radius > 0.5:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius), colors[key], 2)
                cv2.putText(frame,key + " ball", (int(x-radius),int(y-radius)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors[key],2)
                if key == "green":
                    green_setpoint_y = 400 - y
                elif key == "orange":
                    orange_ball_y = 400 - y



    # show the frame to our screen
    cv2.imshow("Frame", frame)

    #Print to test, may cause LAG
    #print("Green : ", green_setpoint_y, "  Orange : ", orange_ball_y)

    #PID Call
    fan_normal = 150 #forexample
    PID_value = fan_normal + pid_control(orange_ball_y,green_setpoint_y, 0.02)

    #cuttig max and min
    if PID_value > 255:
        PID_value = 255
    elif PID_value < 0:
        PID_value = 0
    
    print(PID_value)
    
    arduino.write(struct.pack("B",PID_value))

    time.sleep(0.02)
    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
