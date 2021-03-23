import cv2
import numpy as np
import pigpio #needs 'sudo pigpiod' in cmd to be able to use pigpiod
from time import sleep


#set up gpio
servoX = 2
servoY = 13
pi = pigpio.pi()
pi.set_mode(servoX, pigpio.OUTPUT)
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(servoPinCircle, GPIO.OUT)
# pwm1=GPIO.PWM(servoPinCircle, 50)
# pwm1.start(0)

marginOfError = 40
angleX = 90
angleY = 90

#these values are tested on each indiv servo
#HS422 is used for X and HS5485 is used for Y
minX = 500
maxX = 2500
minY = 800
maxY = 2250


# Capturing the Video Stream
video_capture = cv2.VideoCapture(0)

# queue for averaging/smoothening the detection
queueX = [0, 0, 0]
queueY = [0, 0, 0]

#for text on screen
font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10,470)
fontScale              = 1
fontColor              = (255,255,255)
lineType               = 2

# maximum queue length
maxLength = 5

# Creating the cascade objects
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
# eye_cascade = cv2.CascadeClassifier(
#     cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml")

pulse = ((maxX - minX)/170 * angleX) + minX
pi.set_servo_pulsewidth(servoX, pulse)
pulse = ((maxY - minY)/170 * angleY) + minY
pi.set_servo_pulsewidth(servoY, pulse)

def draw_found_faces(detected, image, color: tuple):
    for (x, y, width, height) in detected:
        cv2.rectangle(
            image,
            (x, y),
            (x + width, y + height),
            color,
            thickness=2
        )

def turnClockwise():
    #print("Turning left")
    global angleX
    if angleX < 170:
        angleX += 1
        pulse = ((maxX - minX)/170 * angleX) + minX
        pi.set_servo_pulsewidth(servoX, pulse)
        #sleep(0.01)
        print("clockwise " + str(pulse))
        print("angleX " + str(angleX))

def turnAntiClockwise():
    #print("Turning right")
    global angleX
    if angleX > 0:
        angleX -= 1
        pulse = ((maxX - minX)/170 * angleX) + minX
        pi.set_servo_pulsewidth(servoX, pulse)
        #sleep(0.01)
        print("anti clockwise " + str(pulse))
        print("angleX " + str(angleX))

def turnDown():
    #print("Turning left")
    global angleY
    if angleY < 170:
        angleY += 1
        pulse = ((maxY - minY)/170 * angleY) + minY
        pi.set_servo_pulsewidth(servoY, pulse)


def turnUp():
    #print("Turning right")
    global angleY
    if angleY > 0:
        angleY -= 1
        pulse = ((maxY - minY)/170 * angleY) + minY
        pi.set_servo_pulsewidth(servoY, pulse)


while True:
    # Get individual frame
    isThereFrame, frame = video_capture.read()

    # make fullscreen?
    cv2.namedWindow('RM1/Mirror', cv2.WINDOW_NORMAL)

    # cv2.setWindowProperty(
    #   'RM1/Mirror', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    overlay = frame.copy()
    output = frame.copy()
    # Covert the frame to grayscale
    grayscale_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect all the faces in that frame
    detected_faces = face_cascade.detectMultiScale(
        image=grayscale_image, scaleFactor=1.3, minNeighbors=4)
    # detected_eyes = eye_cascade.detectMultiScale(
    #     image=grayscale_image, scaleFactor=1.3, minNeighbors=4)
    draw_found_faces(detected_faces, frame, (0, 0, 255))
    # draw_found_faces(detected_eyes, frame, (0, 255, 0))

    # getting width and height of video feed
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))   # float
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))  # float

    centerX =width/2
    centerY = height/2

    detected_width = 0
    detected_x = width/2
    detected_y = height/2

    face_detected = False

    # takes the biggest face in the screen
    for (x, y, width, height) in detected_faces:
        face_detected = True
        if width > detected_width:
            detected_width = width
            detected_x = x + width/2
            detected_y = y + height/2

    if len(queueX) >= maxLength:
        queueX.pop(0)
        queueY.pop(0)
    queueX.append(detected_x)
    queueY.append(detected_y)



    # this calculates the average size (width) of the face for the past 10 frames
    # averagedWidth = sum(queue)/len(queue)
    averagedX = sum(queueX)/len(queueX)
    averagedY = sum(queueY)/len(queueY)

    if face_detected:
        #print(str(averagedX) + ", " + str(centerX))
        if averagedX > (centerX + marginOfError):
            #print(angleX)
            turnClockwise()
        elif averagedX < (centerX - marginOfError):
            #print(angleX)
            turnAntiClockwise()

        if averagedY > (centerY + marginOfError):
            #print(angleX)
            turnDown()
        elif averagedY < (centerY - marginOfError):
            #print(angleX)
            turnUp()

    # raspi screen is 800x480
    cv2.resizeWindow('RM1/Mirror', 800, 480)

    # flipping the screen so it look more like a mirror
    flippedFrame = cv2.flip(frame, 1)

    #putting text on screeen
    cv2.putText(flippedFrame, str(averagedX) + ", " + str(averagedY), 
    bottomLeftCornerOfText, 
    font, 
    fontScale,
    fontColor,
    lineType)
    cv2.imshow('RM1/Mirror', flippedFrame)

    # Press the ESC key to exit the loop
    # 27 is the code for the ESC key
    if cv2.waitKey(1) == 27:
        break

# Releasing the webcam resource
video_capture.release()

# Destroy the window that was showing the video stream
cv2.destroyAllWindows()

#pwm1.stop()
#GPIO.cleanup()

