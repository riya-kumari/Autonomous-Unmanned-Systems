import cv2
# run it by typing 'python3 main.py' in terminal/command-prompt
# Opens and reads the video, displaying it in another window
# TODO: Detect the barrels and draw the rectangles around the barrels

#Our dimensions are 640X480


input_video_path = './BarrelVideo.mp4'
cap = cv2.VideoCapture(input_video_path)

if (cap.isOpened() == False):
    print("Error in opening BarrelVideo.mp4")

# Indicate our color boundaries for detection (orange & white)
desired_colors = ([255,178,102],[255,80,0]), 
                  ([246,246,215],[255,255,255])


while (cap.isOpened()):
    # Capture frame-by-frame
    vid, frame = cap.read()

    if vid == True:
        # Display the resulting frame
        cv2.imshow('BarrelVideo', frame)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Breaks the loop
    else:
        break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
