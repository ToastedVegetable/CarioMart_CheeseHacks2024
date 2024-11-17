from pynput.keyboard import Controller, Key
import time

keyboard = Controller()
last_pressed_player1 = None  # Track the last pressed key for Player 1
last_pressed_player2 = None  # Track the last pressed key for Player 2
COOLDOWN = 0.5  # Minimum time interval (in seconds) between keypresses


def send_keypress(angle, player):
    """
    Maps the angle to a keypress and simulates it for the specified player.
    """
    global last_pressed_player1, last_pressed_player2

    if player == "player1":
        last_pressed = last_pressed_player1
        left_key = 'a'  # Player 1 left turn
        right_key = 'd'  # Player 1 right turn
    elif player == "player2":
        last_pressed = last_pressed_player2
        left_key = 'j'  # Player 2 left turn
        right_key = 'l'  # Player 2 right turn
    else:
        print(f"Unknown player: {player}")
        return

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
            print(f"{player} Left key pressed")

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
            print(f"{player} Right key pressed")

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
            print(f"{player} Straight: No keys pressed")
