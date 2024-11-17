import cv2
import mediapipe as mp
import math
from imutils.video import VideoStream
import time
from hand_angle_to_keypress import send_keypress 
from pynput.keyboard import Controller, Key  

#Initializing mediamap objects
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

#Initializing controller object
keyboard = Controller()

#Padding for open hand
OPEN_HAND_THRESHOLD = 0.15

is_x_pressed = False

#Function to calculate vector angle between two points
def calculate_angle(point1, point2):

    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    angle = math.degrees(math.atan2(dy, dx))
    return angle

#Calculate Euclidain distance b/w two points
def calculate_distance(point1, point2):

    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

#Checks if hand is open based on relative distance of the fingertip node and the palm base
def is_hand_open(landmarks, width, height):
    
    #Sets palm base to the wrist
    palm_base = (landmarks[mp_hands.HandLandmark.WRIST].x * width, landmarks[mp_hands.HandLandmark.WRIST].y * height)

    # Fingertip landmarks
    fingertip_indices = [
        mp_hands.HandLandmark.THUMB_TIP,
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP,
    ]
    fingertip_distances = [
        calculate_distance( palm_base, (landmarks[tip].x * width, landmarks[tip].y * height))
        for tip in fingertip_indices
    ]

    # Average distance of fingertips from palm base
    avg_distance = sum(fingertip_distances) / len(fingertip_distances)

    # Return True if the hand is fingertips are far from the palm) using width to scale
    return avg_distance > OPEN_HAND_THRESHOLD * width 


# Start threaded video stream
cap = VideoStream(src=0).start()
time.sleep(2.0)
angle_hold = 0
right_hand_open = False
left_hand_open = False

while True:
    frame = cap.read()
    if frame is None:
        break

    # Flip the frame horizontally to deal with mirror effect
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert the frame to rgb
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #processing frame
    results = hands.process(rgb_frame)
    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_landmark in enumerate(results.multi_hand_landmarks):
            #Identify which hand is which
            handedness = results.multi_handedness[idx].classification[0].label
            is_open = is_hand_open(hand_landmark.landmark, w, h)

            if handedness == "Right":
                mp_drawing.draw_landmarks(frame, hand_landmark, mp_hands.HAND_CONNECTIONS)

                # Check if the right hand is open and trigger keypress when the palm is opened
                if is_open:
                    if not right_hand_open:
                        keyboard.press('z')
                        print("Right hand opened! z pressed.")
                    right_hand_open = True
                else:
                    keyboard.release('z')
                    right_hand_open = False

            elif handedness == "Left":
                # Draw landmarks for the left hand
                mp_drawing.draw_landmarks(frame, hand_landmark, mp_hands.HAND_CONNECTIONS)

                # Check if the left hand is open and trigger keypress when palm is opened
                if is_open:
                    if not left_hand_open:
                        if is_x_pressed:
                            keyboard.release('x')
                            is_x_pressed = False
                            print("Left hand opened! 'x' key released.")
                    left_hand_open = True
                else:
                    left_hand_open = False

    # Continuously press 'x' if the left hand is not open for acceleration
    if not left_hand_open:
        if not is_x_pressed:
            keyboard.press('x')
            is_x_pressed = True
            print("'x' key pressed continuously.")

    # List to store hand landmarks for angle calculation
    hand_landmarks = []

    # calculate the vector and angle
    if results.multi_hand_landmarks:
        for hand_landmark in results.multi_hand_landmarks:
            middle_mcp = (
                int(hand_landmark.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * w),
                int(hand_landmark.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * h)
            )
            hand_landmarks.append(middle_mcp)

        if len(hand_landmarks) == 2:
            hand_landmarks.sort(key=lambda x: x[0])
            point1 = hand_landmarks[0]
            point2 = hand_landmarks[1]

            # Draw the vector b/w hands and calculate angle
            cv2.line(frame, point1, point2, (0, 255, 0), 3)
            cv2.circle(frame, point1, 5, (0, 0, 255), -1)
            cv2.circle(frame, point2, 5, (0, 0, 255), -1)
            angle = calculate_angle(point1, point2)

            # Send the angle to the keypress handler
            send_keypress(angle)
            
            #holding angle to access later in case of detection problems
            angle_hold = angle

    #if input invalid, pull from previous angle and ignore current frame
    elif len(hand_landmarks) < 2:
        angle = angle_hold
        send_keypress(angle)

    # show frame
    cv2.imshow('Webcam Feed', frame)

    # Press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# stop the video stream and close windows
#PLEASE DO NOT DELETE OTHERWISE MY COMPUTER GO BOOM BOOM 
cap.stop()
cv2.destroyAllWindows()
