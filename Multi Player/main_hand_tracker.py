import cv2
import mediapipe as mp
import math
from imutils.video import VideoStream
import time
from hand_angle_to_keypress import send_keypress
from pynput.keyboard import Controller 

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=4, min_detection_confidence=0.5, min_tracking_confidence=0.5)


keyboard = Controller()


OPEN_HAND_THRESHOLD = 0.1  #distance for fingertips from palm center


def calculate_angle(point1, point2):
    #calculate angle between two points
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    angle = math.degrees(math.atan2(dy, dx))
    return angle


def is_hand_open(landmarks, width, height):
    #use wrists as landmark base
    palm_base = (landmarks[mp_hands.HandLandmark.WRIST].x * width,
                 landmarks[mp_hands.HandLandmark.WRIST].y * height)

    #create fingertip landmarks
    fingertip_indices = [
        mp_hands.HandLandmark.THUMB_TIP,
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP,
    ]
    fingertip_distances = [
        math.sqrt((palm_base[0] - (landmarks[tip].x * width)) ** 2 +
                  (palm_base[1] - (landmarks[tip].y * height)) ** 2)
        for tip in fingertip_indices
    ]

    #average the distance from fingertips to palm base
    avg_distance = sum(fingertip_distances) / len(fingertip_distances)

    #return True if hand is open
    return avg_distance > OPEN_HAND_THRESHOLD * width


def draw_hand_skeleton(frame, hand_landmarks, color):
    #draw the hand skeleton with the specified colors
    mp_drawing.draw_landmarks(
        frame,
        hand_landmarks,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=4), 
        mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),  
    )


#start video
cap = VideoStream(src=0).start()
time.sleep(2.0)

while True:
    frame = cap.read()
    if frame is None:
        break

    #mirror webcam
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    #split the frame into two to faciliate two players
    mid_x = w // 2

    #convert frame to rgb
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)

    player1_landmarks = []
    player2_landmarks = []

    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_landmark in enumerate(results.multi_hand_landmarks):
            #get wrist x to determine what region it's in
            wrist_x = hand_landmark.landmark[mp_hands.HandLandmark.WRIST].x * w

            #assign player1 and player2 based on wrist position
            if wrist_x < mid_x:  #player1 (left)
                player1_landmarks.append(hand_landmark)
                #draw player1 as red
                draw_hand_skeleton(frame, hand_landmark, (0, 0, 255))
            else:  #player2 (right)
                player2_landmarks.append(hand_landmark)
                #draw player2 as blue
                draw_hand_skeleton(frame, hand_landmark, (255, 0, 0))

    #detect left and right hands for both players
    player1_left_hand_open = any(
        is_hand_open(hand_landmark.landmark, w, h) for hand_landmark in player1_landmarks
        if hand_landmark.landmark[mp_hands.HandLandmark.WRIST].x * w < mid_x // 2
    )
    player1_right_hand_open = any(
        is_hand_open(hand_landmark.landmark, w, h) for hand_landmark in player1_landmarks
        if hand_landmark.landmark[mp_hands.HandLandmark.WRIST].x * w >= mid_x // 2
    )
    player2_left_hand_open = any(
        is_hand_open(hand_landmark.landmark, w, h) for hand_landmark in player2_landmarks
        if hand_landmark.landmark[mp_hands.HandLandmark.WRIST].x * w < mid_x + (w - mid_x) // 2
    )
    player2_right_hand_open = any(
        is_hand_open(hand_landmark.landmark, w, h) for hand_landmark in player2_landmarks
        if hand_landmark.landmark[mp_hands.HandLandmark.WRIST].x * w >= mid_x + (w - mid_x) // 2
    )

    #handle the player1 hands
    if len(player1_landmarks) >= 2:
        point1 = (
            int(player1_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * w),
            int(player1_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * h),
        )
        point2 = (
            int(player1_landmarks[1].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * w),
            int(player1_landmarks[1].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * h),
        )

        #draw the vector in red
        cv2.line(frame, point1, point2, (0, 0, 255), 3)
        cv2.circle(frame, point1, 5, (0, 0, 255), -1)
        cv2.circle(frame, point2, 5, (0, 0, 255), -1)

        #calculate angle
        angle_player1 = calculate_angle(point1, point2)

        send_keypress(angle_player1, "player1", player1_left_hand_open, player1_right_hand_open)

    #handle the player2 hands
    if len(player2_landmarks) >= 2:
        point1 = (
            int(player2_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * w),
            int(player2_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * h),
        )
        point2 = (
            int(player2_landmarks[1].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * w),
            int(player2_landmarks[1].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * h),
        )

        #draw the vector in blue
        cv2.line(frame, point1, point2, (255, 0, 0), 3)
        cv2.circle(frame, point1, 5, (255, 0, 0), -1)
        cv2.circle(frame, point2, 5, (255, 0, 0), -1)

        #calculate angle
        angle_player2 = calculate_angle(point1, point2)

        send_keypress(angle_player2, "player2", player2_left_hand_open, player2_right_hand_open)

    #create a dividing line to show the frames
    cv2.line(frame, (mid_x, 0), (mid_x, h), (255, 255, 255), 2)
    cv2.imshow('Player 1 and Player 2', frame)

    #press g to quit
    if cv2.waitKey(1) & 0xFF == ord('g'):
        break

#DO NOT DELETE THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!
cap.stop()
cv2.destroyAllWindows()
