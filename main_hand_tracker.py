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


def draw_hand_connections(frame, hand_landmarks, connections, color):
    """
    Draw hand landmarks and connections on the frame with the specified color.
    """
    mp_drawing.draw_landmarks(
        frame,
        hand_landmarks,
        connections,
        mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=4),
        mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
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
                # Draw landmarks for Player 1 in red
                draw_hand_connections(frame, hand_landmark, mp_hands.HAND_CONNECTIONS, (0, 0, 255))
            else:  # Player 2 (right region)
                player2_landmarks.append(hand_landmark)
                # Draw landmarks for Player 2 in blue
                draw_hand_connections(frame, hand_landmark, mp_hands.HAND_CONNECTIONS, (255, 0, 0))

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

        angle = calculate_angle(point1, point2)
        send_keypress(angle, "player1")

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

        angle = calculate_angle(point1, point2)
        send_keypress(angle, "player2")

    # Show the frame with a dividing line
    cv2.line(frame, (mid_x, 0), (mid_x, h), (255, 255, 255), 2)  # Draw dividing line
    cv2.imshow('Player 1 and Player 2', frame)

    # Press 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Stop the video stream and close windows
cap.stop()
cv2.destroyAllWindows()
