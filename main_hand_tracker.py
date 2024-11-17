import cv2
import mediapipe as mp
import math
from imutils.video import VideoStream
import time
from hand_angle_to_keypress import send_keypress  # Import the function from the other file
from pynput.keyboard import Controller  # For keypress simulation

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=4, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Initialize keyboard controller
keyboard = Controller()

# Threshold for detecting open hand
OPEN_HAND_THRESHOLD = 0.15  # Relative distance for fingertips from palm center


def calculate_angle(point1, point2):
    """
    Calculate the angle of the vector between two points.
    """
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    angle = math.degrees(math.atan2(dy, dx))
    return angle


def is_hand_open(landmarks, width, height):
    """
    Determines if the hand is open based on the relative distances of fingertips to the palm base.
    """
    # Palm base landmark (wrist)
    palm_base = (landmarks[mp_hands.HandLandmark.WRIST].x * width,
                 landmarks[mp_hands.HandLandmark.WRIST].y * height)

    # Fingertip landmarks
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

    # Average distance of fingertips from palm base
    avg_distance = sum(fingertip_distances) / len(fingertip_distances)

    # Return True if the hand is open (fingertips are far from the palm)
    return avg_distance > OPEN_HAND_THRESHOLD * width


def draw_hand_skeleton(frame, hand_landmarks, color):
    """
    Draw the hand skeleton and points on the frame with the specified color.
    """
    mp_drawing.draw_landmarks(
        frame,
        hand_landmarks,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=4),  # Connections
        mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),  # Points
    )


# Start threaded video stream
cap = VideoStream(src=0).start()
time.sleep(2.0)  # Allow the camera to warm up

while True:
    frame = cap.read()
    if frame is None:
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Split the frame width into two regions for two players
    mid_x = w // 2

    # Convert the frame to RGB as Mediapipe processes RGB images
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with Mediapipe
    results = hands.process(rgb_frame)

    # Track hand landmarks separately for Player 1 and Player 2
    player1_landmarks = []
    player2_landmarks = []

    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_landmark in enumerate(results.multi_hand_landmarks):
            # Get wrist x-coordinate to determine which region the hand is in
            wrist_x = hand_landmark.landmark[mp_hands.HandLandmark.WRIST].x * w

            # Assign hands to Player 1 or Player 2 based on x-coordinate
            if wrist_x < mid_x:  # Player 1 (left region)
                player1_landmarks.append(hand_landmark)
                # Draw Player 1's hand in red
                draw_hand_skeleton(frame, hand_landmark, (0, 0, 255))
            else:  # Player 2 (right region)
                player2_landmarks.append(hand_landmark)
                # Draw Player 2's hand in blue
                draw_hand_skeleton(frame, hand_landmark, (255, 0, 0))

    # Detect left and right hands for each player
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

    # Handle Player 1 hands
    if len(player1_landmarks) >= 2:
        point1 = (
            int(player1_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * w),
            int(player1_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * h),
        )
        point2 = (
            int(player1_landmarks[1].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * w),
            int(player1_landmarks[1].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * h),
        )

        # Draw the vector between the two hands in red
        cv2.line(frame, point1, point2, (0, 0, 255), 3)
        cv2.circle(frame, point1, 5, (0, 0, 255), -1)
        cv2.circle(frame, point2, 5, (0, 0, 255), -1)

        # Calculate the angle
        angle_player1 = calculate_angle(point1, point2)

        # Pass state to send_keypress for Player 1
        send_keypress(angle_player1, "player1", player1_left_hand_open, player1_right_hand_open)

    # Handle Player 2 hands
    if len(player2_landmarks) >= 2:
        point1 = (
            int(player2_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * w),
            int(player2_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * h),
        )
        point2 = (
            int(player2_landmarks[1].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * w),
            int(player2_landmarks[1].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * h),
        )

        # Draw the vector between the two hands in blue
        cv2.line(frame, point1, point2, (255, 0, 0), 3)
        cv2.circle(frame, point1, 5, (255, 0, 0), -1)
        cv2.circle(frame, point2, 5, (255, 0, 0), -1)

        # Calculate the angle
        angle_player2 = calculate_angle(point1, point2)

        # Pass state to send_keypress for Player 2
        send_keypress(angle_player2, "player2", player2_left_hand_open, player2_right_hand_open)

    # Show the frame with a dividing line
    cv2.line(frame, (mid_x, 0), (mid_x, h), (255, 255, 255), 2)  # Draw dividing line
    cv2.imshow('Player 1 and Player 2', frame)

    # Press 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Stop the video stream and close windows
cap.stop()
cv2.destroyAllWindows()
