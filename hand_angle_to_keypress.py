from pynput.keyboard import Controller, Key
import time

keyboard = Controller()
last_pressed_player1 = None  # Track the last pressed key for Player 1 (steering)
last_pressed_player2 = None  # Track the last pressed key for Player 2 (steering)
is_accelerating_player1 = True  # Track acceleration state for Player 1
is_accelerating_player2 = True  # Track acceleration state for Player 2


def send_keypress(angle, player, is_left_hand_open, is_right_hand_open):
    """
    Maps the angle and palm detection to keypresses and simulates them for the specified player.
    """
    global last_pressed_player1, last_pressed_player2
    global is_accelerating_player1, is_accelerating_player2

    if player == "player1":
        last_pressed = last_pressed_player1
        left_key = 'a'  # Player 1 left turn
        right_key = 'd'  # Player 1 right turn
        accel_key = 'w'  # Player 1 acceleration
        right_hand_key = 'z'  # Player 1 right hand action
        is_accelerating = is_accelerating_player1
    elif player == "player2":
        last_pressed = last_pressed_player2
        left_key = 'j'  # Player 2 left turn
        right_key = 'l'  # Player 2 right turn
        accel_key = 'i'  # Player 2 acceleration
        right_hand_key = 'm'  # Player 2 right hand action
        is_accelerating = is_accelerating_player2
    else:
        print(f"Unknown player: {player}")
        return

    # Handle left hand open (stop acceleration)
    if is_left_hand_open:
        if is_accelerating:
            keyboard.release(accel_key)
            if player == "player1":
                is_accelerating_player1 = False
            else:
                is_accelerating_player2 = False
            print(f"{player}: Acceleration stopped (left hand open)")
    else:
        if not is_accelerating:
            keyboard.press(accel_key)
            if player == "player1":
                is_accelerating_player1 = True
            else:
                is_accelerating_player2 = True
            print(f"{player}: Acceleration started (left hand closed)")

    # Handle right hand open (special keypress)
    if is_right_hand_open:
        keyboard.press(right_hand_key)
        keyboard.release(right_hand_key)
        print(f"{player}: Right hand action triggered")

    # Handle turning left
    if -75 < angle < -20:
        if last_pressed != left_key:
            # Press the left key and release the right key
            keyboard.press(left_key)
            keyboard.release(right_key)
            if player == "player1":
                last_pressed_player1 = left_key
            else:
                last_pressed_player2 = left_key
            print(f"{player}: Left key pressed")

    # Handle turning right
    elif 20 < angle < 75:
        if last_pressed != right_key:
            # Press the right key and release the left key
            keyboard.press(right_key)
            keyboard.release(left_key)
            if player == "player1":
                last_pressed_player1 = right_key
            else:
                last_pressed_player2 = right_key
            print(f"{player}: Right key pressed")

    # Handle straight (no keys pressed)
    elif -20 < angle < 20:
        if last_pressed is not None:
            # Release both keys
            keyboard.release(left_key)
            keyboard.release(right_key)
            if player == "player1":
                last_pressed_player1 = None
            else:
                last_pressed_player2 = None
            print(f"{player}: Straight (no keys pressed)")
