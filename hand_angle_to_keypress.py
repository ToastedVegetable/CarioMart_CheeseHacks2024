from pynput.keyboard import Controller, Key
import time

keyboard = Controller()
last_pressed = None #keep track of last keypress
last_press_time = 0  # Timestamp for the last keypress
COOLDOWN = 0.5  # Minimum time interval between keypresses (avoid chaos)

#Maps the angle to a keypress
def send_keypress(angle):

    global last_pressed, last_press_time

    current_time = time.time()

    if -75 < angle < -20:
        # simulate turning left
        # if last_pressed != Key.left or (current_time - last_press_time > COOLDOWN):
            keyboard.press(Key.left)
            time.sleep(0.2)
            keyboard.release(Key.right)  # Ensure the opposite direction is released
            keyboard.release(Key.left)  #not turn too much
            last_pressed = Key.left
            last_press_time = current_time
            print("Left key pressed")

    elif 20 < angle < 75:
        #simulate turning right
        # if last_pressed != Key.right or (current_time - last_press_time > COOLDOWN):
            keyboard.press(Key.right)
            time.sleep(0.2)
            keyboard.release(Key.left)  # Ensure the opposite direction is released
            keyboard.release(Key.right)  #not turn too much
            last_pressed = Key.right
            last_press_time = current_time
            print("Right key pressed")

    elif -20 < angle < 20:
        # Simulate "Go straight" (no left/right key held)
        if last_pressed is not None:
            keyboard.release(Key.left)
            keyboard.release(Key.right)
            last_pressed = None
            print("Straight (no key)")

    else:
        # Keep the last input
        if last_pressed == Key.left:
            keyboard.press(Key.left)
            print("Continuing left key")
        elif last_pressed == Key.right:
            keyboard.press(Key.right)
            print("Continuing right key")
