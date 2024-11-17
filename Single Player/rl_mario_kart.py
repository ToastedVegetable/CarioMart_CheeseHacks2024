import numpy as np
import cv2
from PIL import ImageGrab  # For screen capture
import time
from pynput.keyboard import Controller, Key
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

# Initialize keyboard controller
keyboard = Controller()

class MarioKartCustomEnv:
    """
    A custom environment for Mario Kart RL training without gym/gymnasium.
    """
    def __init__(self):
        # Screen capture region (adjust based on emulator window)
        self.monitor = (100, 100, 740, 580)  # (left, top, right, bottom)

        # Number of discrete actions: [0=straight, 1=left, 2=right, 3=accelerate, 4=brake]
        self.num_actions = 5

        # Observation dimensions (grayscale screen)
        self.obs_shape = (84, 84, 1)

        # Initialize variables
        self.done = False
        self.last_action = None

    def reset(self):
        """
        Reset the environment (restart the game).
        """
        keyboard.press(Key.f1)  # Example: F1 for reset
        time.sleep(1)
        keyboard.release(Key.f1)

        # Capture the initial screen state
        return self._get_observation()

    def step(self, action):
        """
        Execute an action and return the new state, reward, and done flag.
        """
        self._perform_action(action)

        # Wait a short period to simulate the action's effect
        time.sleep(0.1)

        # Capture the new observation
        obs = self._get_observation()

        # Calculate reward
        reward = self._get_reward()

        # Check if the game is over
        self.done = self._is_done()

        return obs, reward, self.done, {}

    def _get_observation(self):
        """
        Capture and preprocess the screen.
        """
        screen = np.array(ImageGrab.grab(bbox=self.monitor))  # Screen capture
        gray_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        resized_screen = cv2.resize(gray_screen, (84, 84))  # Resize to 84x84
        return np.expand_dims(resized_screen, axis=-1)  # Add channel dimension

    def _perform_action(self, action):
        """
        Simulate keypresses based on the action.
        """
        # Release all keys before performing a new action
        keyboard.release(Key.left)
        keyboard.release(Key.right)
        keyboard.release('z')  # Accelerate
        keyboard.release('x')  # Brake

        # Execute the action
        if action == 0:  # Straight
            pass
        elif action == 1:  # Turn left
            keyboard.press(Key.left)
        elif action == 2:  # Turn right
            keyboard.press(Key.right)
        elif action == 3:  # Accelerate
            keyboard.press('z')
        elif action == 4:  # Brake
            keyboard.press('x')

        # Record the last action
        self.last_action = action

    def _get_reward(self):
        """
        Calculate a reward for the current state.
        """
        # Placeholder: Reward for staying in the game (to be improved)
        return 1.0

    def _is_done(self):
        """
        Determine if the game is over.
        """
        # Placeholder: Game never ends (to be improved)
        return False


# Training Loop
if __name__ == "__main__":
    # Initialize the environment
    env = MarioKartCustomEnv()

    # Vectorize the environment for training
    env = make_vec_env(lambda: env, n_envs=1)

    # Initialize the PPO model
    model = PPO("CnnPolicy", env, verbose=1)

    # Train the model
    model.learn(total_timesteps=10000)

    # Save the model
    model.save("ppo_mario_kart")

    # Test the trained agent
    obs = env.reset()
    for _ in range(1000):
        action, _states = model.predict(obs)
        obs, reward, done, _ = env.step(action)
        if done:
            obs = env.reset()
