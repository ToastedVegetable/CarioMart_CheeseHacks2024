import gym
import numpy as np
import cv2
import mss
import time
from pynput.keyboard import Controller, Key

keyboard = Controller()

class MarioKartEnv(gym.Env):
    def __init__(self):
        super(MarioKartEnv, self).__init__()

        #dimensions for capturing the emulator window
        self.monitor = {"top": 100, "left": 100, "width": 640, "height": 480}
        self.action_space = gym.spaces.Discrete(5)

        #resized and grayscaled emulator screen
        self.observation_space = gym.spaces.Box(
            low=0, high=255, shape=(84, 84, 1), dtype=np.uint8
        )

    #reset environment
    def reset(self):
        
        keyboard.press(Key.f1)
        time.sleep(1)
        keyboard.release(Key.f1)
        return self._get_observation()

    #execute action in emulator and return new state
    def step(self, action):
        self._perform_action(action)
        time.sleep(0.1)

        obs = self._get_observation()

        #calculate reward (to be improved based on game performance)
        reward = self._get_reward()

        done = self._is_done()

        return obs, reward, done, {}

    #capture and preprocess sreen
    def _get_observation(self):

        with mss.mss() as sct:
            screen = np.array(sct.grab(self.monitor))
        gray_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        resized_screen = cv2.resize(gray_screen, (84, 84))  #resize
        return np.expand_dims(resized_screen, axis=-1)

    #simulate keypresses based on action observed
    def _perform_action(self, action):
        #reset keys before starting
        keyboard.release(Key.left)
        keyboard.release(Key.right)
        keyboard.release('z') 
        keyboard.release('x')

        #perfrom action
        if action == 0: 
            pass
        elif action == 1: 
            keyboard.press(Key.left)
        elif action == 2: 
            keyboard.press(Key.right)
        elif action == 3: 
            keyboard.press('z')
        elif action == 4:
            keyboard.press('x')

    #reward function based on game state
    def _get_reward(self):
        return 1.0

    #check if game over
    def _is_done(self):
        return False