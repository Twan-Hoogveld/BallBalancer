# USAGE
# python multi_object_tracking.py --video videos/soccer_01.mp4 --tracker csrt

# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import threading

#init time
old_time = int(round(time.time() * 1000))

#Printing threading

def print_ball_height(y):
    time.sleep(0.5)
    print("ball :", y)

def print_setpoint(y):
    time.sleep(0.5)
    print("setpoint :" ,y)

threads = []



#PID
error_old = 0
kp = 1
ki = 1
kd = 1

def pid_control(ball_height, setpoint, delta_time = 0.2, ):
    global error_old
    ie = 0
    error_new = setpoint - ball_height
    delta_error = error_new-error_old
    delta_time = 0.01
    ie += error_new

    error_old = error_new
    total_action = kp * error_new + kd * (delta_error/delta_time)+ ki * ie
    print("total : ", total_action)




# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="csrt",
                help="OpenCV object tracker type")
args = vars(ap.parse_args())

# initialize a dictionary that maps strings to their corresponding
# OpenCV object tracker implementations
OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}

# initialize OpenCV's special multi-object tracker
trackers = cv2.MultiTracker_create()

# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# loop over frames from the video stream
while True:
    # grab the current frame, then handle if we are using a
    # VideoStream or VideoCapture object
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame

    # check to see if we have reached the end of the stream
    if frame is None:
        break

    # resize the frame (so we can process it faster)
    frame = imutils.resize(frame, width=600)

    # grab the updated bounding box coordinates (if any) for each
    # object that is being tracked
    (success, boxes) = trackers.update(frame)

    # loop over the bounding boxes and draw then on the frame
    # boxes is number of objects
    # seletc ball first
    # then setpoint
    counter = 0
    for box in boxes:
        #first selection is ball
        if counter == 0:
            (x, y, w, h) = [int(v) for v in box]
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            ball_height = y;
            t = threading.Thread(target=print_ball_height, args=(ball_height,))
            threads.append(t)
            t.start()
        #second selection is setpoint
        elif counter == 1:
            (x, y, w, h) = [int(v) for v in box]
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            setpoint = y
            d = threading.Thread(target=print_setpoint, args=(setpoint,))
            threads.append(d)
            d.start()
        counter += 1


    # old_time = 0
    # if len(boxes) == 2:
    #     current_time = int(round(time.time() * 1000))
    #     # Each 0.2 Seconds recalculate
    #     if current_time-old_time > 200:
    #         pid_control(ball_height, setpoint)
    #     old_time = current_time


    if len(boxes) == 2:
        time_new = int(round(time.time() * 1000))
        delta_time = old_time - time_new
        tr = threading.Thread(target=pid_control, args=(ball_height, setpoint,delta_time))
        threads.append(tr)
        tr.start()
        old_time = time_new


    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 's' key is selected, we are going to "select" a bounding
    # box to track
    if key == ord("p"):
        # select the bounding box of the object we want to track (make
        # sure you press ENTER or SPACE after selecting the ROI)
        box = cv2.selectROI("Frame", frame, fromCenter=False,
                            showCrosshair=True)

        # create a new object tracker for the bounding box and add it
        # to our multi-object tracker
        tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
        trackers.add(tracker, frame, box)

    # if the `q` key was pressed, break from the loop
    elif key == ord("q"):
        break

# if we are using a webcam, release the pointer
if not args.get("video", False):
    vs.stop()

# otherwise, release the file pointer
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
