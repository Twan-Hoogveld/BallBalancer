from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

# Camera Used
# 0 = Webcam
# 1 = PS3 Cam
cam = 0

#Light condition
# 0 = dark
# 1 = bright
light = 0

# BGR Colors
orange_webcam_light = np.uint8([[[80, 177, 255]]])
orange_webcam_dark = np.uint8([[[44, 121, 194]]])

blue_webcam_vaseline_light = np.uint8([[[101, 69, 46]]])
blue_webcam_vaseline_dark = np.uint8([[[101, 69, 46]]])

orange_ps_cam = np.uint8([[[147, 184, 213]]])


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "orange"
# ball in the HSV color space, then initialize the
# list of tracked points
if not cam:
    if light:
        ball = orange_webcam_light
        blue = blue_webcam_vaseline_light
    else:
        ball = orange_webcam_dark
        blue = blue_webcam_vaseline_dark

else:
    ball = orange_ps_cam


hsvOrange = cv2.cvtColor(ball, cv2.COLOR_BGR2HSV)
print(hsvOrange)
ball_lower = np.array([hsvOrange[0][0][0] - 10, 100, 100])
ball_upper = np.array([hsvOrange[0][0][0] + 10, 255, 255])
print(ball_lower)
print(ball_upper)

pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam (0 IS WEBCAM, 1 IS PS3 CAM)

vs = VideoStream(src=cam).start()


# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping
while True:
    # grab the current frame
    frame = vs.read()

    # handle the frame from VideoCapture or VideoStream


    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, ball_lower, ball_upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
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

        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (255, 255, 255), 2)
        print(int(x),int(y))

        cv2.circle(frame, center, 5, (0, 0, 255), -1)

    # update the points queue
    pts.appendleft(center)

    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break


vs.stop()
vs.release()

# close all windows
cv2.destroyAllWindows()
