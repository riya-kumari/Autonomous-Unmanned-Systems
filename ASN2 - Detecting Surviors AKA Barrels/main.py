import cv2
import numpy as np


# run it by typing 'python3 main.py' in terminal/command-prompt
# Opens and reads the video, displaying it in another window
# TODO: Detect the barrels and draw the rectangles around the barrels
import random as rng
# from colorlabeler import ColorLabeler

input_video_path = './BarrelVideo.mp4'
cap = cv2.VideoCapture(input_video_path)

if (cap.isOpened() == False):
    print("Error in opening BarrelVideo.mp4")

# Indicate our color boundaries for detection (orange & white)
desired_colors = ([255, 178, 102], [255, 80, 0]), ([
    246, 246, 215], [255, 255, 255])


def empty(a):
    pass


while (cap.isOpened()):
    # Capture frame-by-frame
    success, frame = cap.read()

    if success == True:
        imgBlur = cv2.GaussianBlur(frame, (7, 7), 1)
        imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        imgGrayBlur = cv2.blur(imgGray, (3, 3))
        imgGrayBlur = cv2.bilateralFilter(imgGray, 5, 175, 175)
        imgHsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        imgCanny = cv2.Canny(imgGrayBlur, 50, 50)
        kernel = np.ones((5, 5))
        # img_dilate = cv2.dilate(imgCanny, kernel, iterations=1)

        # Find contours
        contours, hierarchy = cv2.findContours(
            imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # contours = imutils.grab_contours(contours)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for i in range(3):
            # contours:
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if area > 500:
                cv2.drawContours(frame, cnt, -1, (0, 0, 255), 7)
                perimeter = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
                print(len(approx))

                x, y, w, h = cv2.boundingRect(approx)
                cv2.rectangle(frame, (x, y),
                              (x + w, y + h), (0, 255, 0), 5)

        cv2.imshow('imgCanny', imgCanny)
        cv2.imshow('Barrel-video', frame)

        # Draw contours

        # Press Q on keyboard to  exit
        if cv2.waitKey(200) & 0xFF == ord('q'):
            break

    # Breaks the loop
    else:
        break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
