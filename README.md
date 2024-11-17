# CarioMart_CheeseHacks2024


### Introduction:

  Ever wanted to control Mario Kart with just your hands? This project turns that dream into reality! Using real-time hand tracking, we’ve built a fun, gesture-based controller that lets two players race without needing a physical game controller. Just raise your hands, make some gestures, and let the game begin!


### Features:


  Multiplayer Support:
    Supports two players with independent controls by splitting the camera feed (Can also be singleplayer without splitting the camera feed).
  
  Gesture-Based Controls:
    Left hand open: Stops acceleration.
    Right hand open: Triggers a special action (like using an item).
    Middle finger tracking: Steer left, right, or go straight.
    Real-Time Tracking:
    Smooth and responsive hand tracking ensures no lag during gameplay.
  
  Mario Kart Compatibility:
    Fully tested and optimized for Mario Kart on a PC emulator.



### Libraries:


  Mediapipe: Handles real-time hand tracking and gesture detection.
  
  OpenCV: Processes the webcam feed and sends it to Mediapipe
  
  Pynput: Simulates keypresses to interact with the game.
  
  Python: The core glue that ties everything together.
  
