from pynput.keyboard import Controller, Key
import time

keyboard = Controller()
last_pressed_player1 = None  #keeps track of the pressed key for player1 (for steering)
last_pressed_player2 = None  #keeps track of the last pressed key for player2 (for steering)
is_accelerating_player1 = True  #acceleration state for player1
is_accelerating_player2 = True  #acceleration state for player2


def send_keypress(angle, player, is_left_hand_open, is_right_hand_open):
    #simulates keypresses
    global last_pressed_player1, last_pressed_player2
    global is_accelerating_player1, is_accelerating_player2

    if player == "player1":
        last_pressed = last_pressed_player1
        left_key = Key.left  #player1 left turn
        right_key = Key.right  #player1 right turn
        accel_key = 'a'  #player1 acceleration
        right_hand_key = 'c'  #player1 right hand action
        is_accelerating = is_accelerating_player1
    elif player == "player2":
        last_pressed = last_pressed_player2
        left_key = 'y'  #player2 left turn
        right_key = 'u'  #player2 right turn
        accel_key = 'q'  #player2 acceleration
        right_hand_key = 'd'  #player2 right hand action
        is_accelerating = is_accelerating_player2
    else:
        print(f"Unknown player: {player}")
        return

    #handle acceleration state
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

    #handle right hand action
    if is_right_hand_open:
        keyboard.press(right_hand_key)
        time.sleep(0.05)
        keyboard.release(right_hand_key)
        print(f"{player}: Right hand action triggered")

    #handle left turns
    if -75 < angle < -20:
        # if last_pressed != left_key:
            #press left key and release right key
            keyboard.release(right_key)
            keyboard.press(left_key)
            keyboard.release(right_key)
            time.sleep(0.05)
            if player == "player1":
                last_pressed_player1 = left_key
            else:
                last_pressed_player2 = left_key
            print(f"{player}: Left key pressed")

    #handle right turns
    elif 20 < angle < 75:
        # if last_pressed != right_key:
            #press right key and release left key
            keyboard.release(left_key)
            keyboard.press(right_key)
            keyboard.release(left_key)
            time.sleep(0.05)
            if player == "player1":
                last_pressed_player1 = right_key
            else:
                last_pressed_player2 = right_key
            print(f"{player}: Right key pressed")

    #handle straight
    elif -20 < angle < 20:
        # if last_pressed is not None:
            #release both keys
            keyboard.release(left_key)
            keyboard.release(right_key)
            if player == "player1":
                last_pressed_player1 = None
            else:
                last_pressed_player2 = None
            print(f"{player}: Straight (no keys pressed)")
