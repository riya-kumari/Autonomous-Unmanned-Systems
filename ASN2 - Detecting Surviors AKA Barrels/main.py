import cv2
import numpy as np

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
        # trying filter by color
        imgHsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        ORANGE_MIN = np.array([5, 50, 50], np.uint8)
        ORANGE_MAX = np.array([15, 255, 255], np.uint8)

        WHITE_MAX = np.array([76,75,77])
        WHITE_MIN = np.array([174,177,178])

        maskOrange = cv2.inRange(imgHsv, ORANGE_MIN, ORANGE_MAX)
        result = cv2.bitwise_and(frame, frame, mask=maskOrange)

        # TODO: FIGURE OUT WHAT COLOR VALUE THE WHITE IS SO WE CAN MASK IT, YOU CAN TEST IT BY SEEING THE RESULT OF WHITE MASK RESULT WINDOW WHEN YOU RUN THIS PROGRAM.
        # IT SHOULD BE SIMILAR TO THE ORANGE MASK RESULT
        maskWhite = cv2.inRange(frame, WHITE_MIN, WHITE_MAX)
        resultWhite = cv2.bitwise_and(frame, frame, mask=maskWhite)

        finalResult = result + resultWhite
        finalMask = maskOrange + maskWhite

        cv2.imshow('image hsv', imgHsv)
        cv2.imshow('orange mask result', result)
        cv2.imshow('white mask result', resultWhite)
        # once you get the white mask right, result white should display something
        # https://realpython.com/python-opencv-color-spaces/ Read and follow this carefully, I couldn't figure out the colors for white
        cv2.imshow('final result', finalResult)
        # this is what you use to draw the boxes, once you mask white, the white will show up in this image
        cv2.imshow('final masked image', finalMask)

        imgCanny = cv2.Canny(finalResult, 50, 50)
        # Find contours
        contours, hierarchy = cv2.findContours(
            imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        # For drawing slanted boxes : https://stackoverflow.com/questions/36921249/drawing-angled-rectangles-in-opencv
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                # cv2.drawContours(cnt, cnt, -1, (0, 0, 255), 7)
                # perimeter = cv2.arcLength(cnt, True)
                # approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
                # print(len(approx))

                # x, y, w, h = cv2.boundingRect(approx)
                # cv2.rectangle(frame, (x, y),
                #               (x + w, y + h), (0, 255, 0), 5)
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(frame, [box], 0, (0, 191, 255), 2)

        cv2.imshow('final_frame', frame)

        # change the value of waitKey to slow down the video
        if cv2.waitKey(200) & 0xFF == ord('q'):
            break

    # Breaks the loop
    else:
        break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
