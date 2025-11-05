"""
Configuration file for Mouse Movement Simulator

This file contains all customizable settings for the mouse movement behavior.
Adjust these values to change how the script behaves.
"""

# Movement type settings
USE_LINEAR_MOVEMENT = True
USE_BEZIER_MOVEMENT = True

# Timing settings (in seconds)
WAIT_TIME_RANGE = (10, 60)  # Min and max wait between movements
MOVEMENT_DURATION_RANGE = (1.0, 3.0)  # Min and max duration for each movement

# Linear movement settings
LINEAR_STEP_INTERVAL_RANGE = (0.005, 0.02)  # Seconds between steps
LINEAR_STEPS_RANGE = (30, 80)  # Number of steps for linear movement

# Bezier movement settings
BEZIER_STEP_INTERVAL_RANGE = (0.01, 0.03)  # Seconds between steps
BEZIER_CURVATURE_RANGE = (0.2, 0.4)  # How curved the bezier path is

# Screen boundaries
# Pixels from edges to avoid:
#   (50,): all four margins
#   (50, 100): 50px margin left and right and 100px margin top and bottom
#   (25, 50, 75, 100): 25px left, 50px top, 75px right, 100px bottom
SCREEN_MARGIN = (50,)
ENABLE_SCREEN_SAFE_ZONE = True  # Whether to avoid screen edges

# Behavior settings
ENABLE_JITTER = True  # Add small random movements for realism
JITTER_INTENSITY = 1  # Pixels of jitter (1-3 recommended)
RANDOMIZE_MOVEMENT_TYPES = True  # Randomly choose between enabled movement types

# Logging and output
VERBOSE_LOGGING = True
PRINT_MOVEMENT_DETAILS = True

# Advanced settings
MAX_CONSECUTIVE_SAME_TYPE = 3  # Max consecutive movements of same type
ENABLE_SMALL_MOVEMENTS = True  # Occasionally make small movements
SMALL_MOVEMENT_CHANCE = 0.2  # 20% chance for small movement
SMALL_MOVEMENT_RANGE = (50, 200)  # Pixel range for small movements
