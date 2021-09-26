import cv2
import numpy as np
# run it by typing 'python3 main.py' in terminal/command-prompt
# Opens and reads the video, displaying it in another window
# TODO: Detect the barrels and draw the rectangles around the barrels


input_video_path = './BarrelVideo.mp4'
cap = cv2.VideoCapture(input_video_path)

if (cap.isOpened() == False):
    print("Error in opening BarrelVideo.mp4")

# Indicate our color boundaries for detection (orange & white)
desired_colors = ([255, 178, 102], [255, 80, 0]), ([
    246, 246, 215], [255, 255, 255])


def empty(a):
    pass


cv2.namedWindow("HSV")
cv2.resizeWindow("HSV", 640, 240)
cv2.createTrackbar("HUE Min", "HSV", 0, 179, empty)
cv2.createTrackbar("HUE Max", "HSV", 179, 179, empty)
cv2.createTrackbar("SAT Min", "HSV", 0, 255, empty)
cv2.createTrackbar("SAT Max", "HSV", 255, 255, empty)
cv2.createTrackbar("VALUE Min", "HSV", 0, 255, empty)
cv2.createTrackbar("VALUE Max", "HSV", 255, 255, empty)


while (cap.isOpened()):
    # Capture frame-by-frame
    vid, frame = cap.read()
    imgHsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h_min = cv2.getTrackbarPos("HUE Min", "HSV")
    h_max = cv2.getTrackbarPos("HUE Max", "HSV")
    s_min = cv2.getTrackbarPos("SAT Min", "HSV")
    s_max = cv2.getTrackbarPos("SAT Max", "HSV")
    v_min = cv2.getTrackbarPos("VALUE Min", "HSV")
    v_max = cv2.getTrackbarPos("VALUE Max", "HSV")
    print(h_min)

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(imgHsv, lower, upper)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    hStack = np.hstack([frame, mask, result])

    cv2.imshow('HSV Color Space', imgHsv)
    cv2.imshow('Mask', mask)
    cv2.imshow('Result', result)
    if vid == True:
        # Display the resulting frame
        cv2.imshow('BarrelVideo-original', frame)

        # Press Q on keyboard to  exit
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            break

    # Breaks the loop
    else:
        break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
