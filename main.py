"""
Mouse Movement Simulator for Availability Maintenance

Create by: Jose Romero
Version: 1.0
Date: 2025

Description:
This module provides functionality to simulate human-like mouse movements to
maintain "available" status on applications like Microsoft Teams, Slack, etc.
It includes both straight-line and curved human-like movement patterns.

Platform Support: Windows, Linux
macOS Support: Limited (see README for details)

Disclaimer:
This tool is intended for legitimate use cases such as preventing auto "away"
status during extended periods of inactivity. Please ensure compliance with
your organization's policies and terms of service.
"""

import math
import random
import time
import sys
import platform
import subprocess

# Import configuration
import config

# Platform-specific imports
if platform.system() == "Windows":
    import win32api
    import win32con
elif platform.system() == "Linux":
    try:
        import Xlib.display
    except ImportError:
        print("Error: python-xlib not installed. Install with: pip install python-xlib")
        sys.exit(1)


class MouseController:
    """Cross-platform mouse controller"""

    def __init__(self):
        self.system = platform.system()
        if self.system == "Linux":
            self.display = Xlib.display.Display()
            self.screen = self.display.screen()
            self.root = self.screen.root

    def get_cursor_pos(self) -> tuple[int, int]:
        """Get current mouse position"""
        if self.system == "Windows":
            return win32api.GetCursorPos()
        elif self.system == "Linux":
            try:
                query = self.root.query_pointer()
                return query.root_x, query.root_y
            except Xlib.error.ConnectionClosedError:
                # Reconnect if display connection is closed
                self.display = Xlib.display.Display()
                self.screen = self.display.screen()
                self.root = self.screen.root
                query = self.root.query_pointer()
                return query.root_x, query.root_y
        elif self.system == "Darwin":  # macOS
            # Use AppleScript to get cursor position (more reliable)
            try:
                result = subprocess.run([
                    'osascript', '-e',
                    'tell application "System Events" to get position of mouse'
                ], capture_output=True, text=True, check=True)
                x, y = map(int, result.stdout.strip().split(', '))
                return x, y
            except (subprocess.CalledProcessError, ValueError):
                # Fallback to a default position
                return (500, 500)

    def set_cursor_pos(self, x: int, y: int) -> None:
        """Set mouse position"""
        if self.system == "Windows":
            win32api.SetCursorPos((x, y))
        elif self.system == "Linux":
            # Use xdotool for Linux
            try:
                subprocess.run(['xdotool', 'mousemove', str(x), str(y)],
                             check=False, capture_output=True)
            except FileNotFoundError:
                print("Error: xdotool not found. Install with: sudo apt-get install xdotool")
                raise
        elif self.system == "Darwin":  # macOS
            # Use AppleScript for macOS (more reliable than CGWarpMouseCursorPosition)
            try:
                subprocess.run([
                    'osascript', '-e',
                    f'tell application "System Events" to set position of mouse to {{{x}, {y}}}'
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print("Error: Could not move mouse on macOS. Make sure accessibility permissions are granted.")
                raise

    def get_screen_dimensions(self) -> tuple[int, int]:
        """Get screen dimensions"""
        if self.system == "Windows":
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            return screen_width, screen_height
        elif self.system == "Linux":
            return self.screen.width_in_pixels, self.screen.height_in_pixels
        elif self.system == "Darwin":  # macOS
            # Use system_profiler to get screen dimensions
            try:
                result = subprocess.run([
                    'system_profiler', 'SPDisplaysDataType'
                ], capture_output=True, text=True, check=True)

                # Parse the output to find resolution
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Resolution' in line:
                        resolution = line.split(':')[1].strip()
                        if 'x' in resolution:
                            width, height = map(int, resolution.split(' x '))
                            return width, height

                # Fallback to common resolution
                return 1440, 900
            except (subprocess.CalledProcessError, ValueError, IndexError):
                # Fallback to common resolution
                return 1440, 900


def get_screen_dimensions() -> tuple[int, int]:
    """
    Get available screen dimensions.

    Returns:
        tuple[int, int]: A tuple containing (width, height) of the primary
        screen in pixels.
    """
    controller = MouseController()
    return controller.get_screen_dimensions()


def get_screen_bounds() -> tuple[int, int, int, int]:
    """
    Calculate screen boundaries based on margin configuration.

    Returns:
        tuple[int, int, int, int]: (min_x, min_y, max_x, max_y) boundaries
    """
    controller = MouseController()
    screen_width, screen_height = controller.get_screen_dimensions()

    if not config.ENABLE_SCREEN_SAFE_ZONE:
        return 0, 0, screen_width, screen_height

    # Parse margin configuration
    margin = config.SCREEN_MARGIN
    if len(margin) == 1:
        # Same margin for all sides
        left = top = right = bottom = margin[0]
    elif len(margin) == 2:
        # Horizontal and vertical margins
        left = right = margin[0]
        top = bottom = margin[1]
    elif len(margin) == 4:
        # Individual margins for each side
        left, top, right, bottom = margin
    else:
        raise ValueError("SCREEN_MARGIN must have 1, 2, or 4 values")

    min_x = left
    min_y = top
    max_x = screen_width - right
    max_y = screen_height - bottom

    # Validate bounds
    if min_x >= max_x or min_y >= max_y:
        raise ValueError("Screen margins are too large for the screen dimensions")

    return min_x, min_y, max_x, max_y


def get_next_position(max_x: int, max_y: int, min_x: int = 0, min_y: int = 0) -> tuple[int, int]:
    """
    Generate a random position within specified boundaries.

    Args:
        max_x (int): Maximum X coordinate
        max_y (int): Maximum Y coordinate
        min_x (int, optional): Minimum X coordinate. Defaults to 0.
        min_y (int, optional): Minimum Y coordinate. Defaults to 0.

    Returns:
        tuple[int, int]: A tuple containing (x, y) coordinates

    Raises:
        ValueError: If min_x >= max_x or min_y >= max_y
    """
    if min_x >= max_x:
        raise ValueError("min_x must be less than max_x")

    if min_y >= max_y:
        raise ValueError("min_y must be less than max_y")

    return random.randint(min_x, max_x), random.randint(min_y, max_y)


def get_small_movement_position(current_x: int, current_y: int) -> tuple[int, int]:
    """
    Generate a position for a small movement near the current position.

    Args:
        current_x (int): Current X coordinate
        current_y (int): Current Y coordinate

    Returns:
        tuple[int, int]: New position within small movement range
    """
    controller = MouseController()
    screen_width, screen_height = controller.get_screen_dimensions()

    # Calculate small movement boundaries
    min_x = max(0, current_x - config.SMALL_MOVEMENT_RANGE[1])
    max_x = min(screen_width, current_x + config.SMALL_MOVEMENT_RANGE[1])
    min_y = max(0, current_y - config.SMALL_MOVEMENT_RANGE[1])
    max_y = min(screen_height, current_y + config.SMALL_MOVEMENT_RANGE[1])

    # Ensure movement is at least the minimum distance
    while True:
        target_x, target_y = get_next_position(max_x, max_y, min_x, min_y)
        distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
        if distance >= config.SMALL_MOVEMENT_RANGE[0]:
            return target_x, target_y


def linear_mouse_move(target_x: int, target_y: int) -> None:
    """
    Move mouse from current position to target in a straight line.

    Args:
        target_x (int): Target X coordinate
        target_y (int): Target Y coordinate
    """
    controller = MouseController()

    # Get current mouse position
    start_x, start_y = controller.get_cursor_pos()

    # Use config values
    step_interval = random.uniform(*config.LINEAR_STEP_INTERVAL_RANGE)
    steps = random.randint(*config.LINEAR_STEPS_RANGE)

    # Calculate increments for each step
    x_increment = (target_x - start_x) / steps
    y_increment = (target_y - start_y) / steps

    # Move through each intermediate point
    for step in range(1, steps + 1):
        current_x = int(start_x + x_increment * step)
        current_y = int(start_y + y_increment * step)

        # Add jitter if enabled
        if config.ENABLE_JITTER:
            jitter_x = random.randint(-config.JITTER_INTENSITY, config.JITTER_INTENSITY)
            jitter_y = random.randint(-config.JITTER_INTENSITY, config.JITTER_INTENSITY)
            current_x += jitter_x
            current_y += jitter_y

        controller.set_cursor_pos(current_x, current_y)
        time.sleep(step_interval)


def human_like_mouse_move(target_x: int, target_y: int) -> None:
    """
    Move mouse from current position to target with human-like curved movement.

    Args:
        target_x (int): Target X coordinate
        target_y (int): Target Y coordinate
    """
    controller = MouseController()

    # Get current mouse position
    start_x, start_y = controller.get_cursor_pos()

    # Calculate distance for realistic curvature
    dx = target_x - start_x
    dy = target_y - start_y
    distance = math.sqrt(dx**2 + dy**2)

    # Use config values
    movement_duration = random.uniform(*config.MOVEMENT_DURATION_RANGE)
    step_interval = random.uniform(*config.BEZIER_STEP_INTERVAL_RANGE)
    curvature_factor = random.uniform(*config.BEZIER_CURVATURE_RANGE)

    # Create control points for Bezier curve with realistic curvature
    offset_range = distance * curvature_factor

    # Control point 1 (30% of the way with random offset)
    ctrl1_x = start_x + dx * 0.3 + random.uniform(-offset_range, offset_range)
    ctrl1_y = start_y + dy * 0.3 + random.uniform(-offset_range, offset_range)

    # Control point 2 (70% of the way with random offset)
    ctrl2_x = start_x + dx * 0.7 + random.uniform(-offset_range, offset_range)
    ctrl2_y = start_y + dy * 0.7 + random.uniform(-offset_range, offset_range)

    # Calculate number of steps based on duration and interval
    steps = int(movement_duration / step_interval)

    # Move through Bezier curve points
    for i in range(steps + 1):
        t = i / steps

        # Cubic Bezier curve calculation
        current_x = (
            (1-t)**3 * start_x +
            3*(1-t)**2*t * ctrl1_x +
            3*(1-t)*t**2 * ctrl2_x +
            t**3 * target_x
        )

        current_y = (
            (1-t)**3 * start_y +
            3*(1-t)**2*t * ctrl1_y +
            3*(1-t)*t**2 * ctrl2_y +
            t**3 * target_y
        )

        # Add subtle human-like jitter
        if config.ENABLE_JITTER:
            jitter_x = random.randint(-config.JITTER_INTENSITY, config.JITTER_INTENSITY)
            jitter_y = random.randint(-config.JITTER_INTENSITY, config.JITTER_INTENSITY)
            current_x += jitter_x
            current_y += jitter_y

        controller.set_cursor_pos(int(current_x), int(current_y))

        # Variable interval for more natural movement
        variable_interval = step_interval + random.uniform(-0.005, 0.005)
        time.sleep(max(0.001, variable_interval))  # Ensure positive interval


def choose_movement_type(consecutive_count: dict) -> str:
    """
    Choose which movement type to use based on configuration and history.

    Args:
        consecutive_count (dict): Count of consecutive movement types

    Returns:
        str: Movement type to use ('linear' or 'bezier')
    """
    # Check which movement types are enabled
    enabled_types = []
    if config.USE_LINEAR_MOVEMENT:
        enabled_types.append('linear')
    if config.USE_BEZIER_MOVEMENT:
        enabled_types.append('bezier')

    if not enabled_types:
        raise ValueError("At least one movement type must be enabled in config")

    if len(enabled_types) == 1:
        return enabled_types[0]

    if not config.RANDOMIZE_MOVEMENT_TYPES:
        # Alternate if both are enabled but not randomizing
        return 'linear' if consecutive_count['linear'] <= consecutive_count['bezier'] else 'bezier'

    # Random choice between enabled types
    return random.choice(enabled_types)


def check_dependencies() -> bool:
    """Check if required dependencies are installed for the current platform"""
    system = platform.system()

    if system == "Windows":
        try:
            import win32api
            import win32con
            return True
        except ImportError:
            print("Error: pywin32 is required for Windows. Install with: pip install pywin32")
            return False

    elif system == "Linux":
        # Check if xdotool is available
        try:
            result = subprocess.run(['which', 'xdotool'], capture_output=True, text=True)
            if result.returncode != 0:
                print("Error: xdotool is required for Linux. Install with: sudo apt-get install xdotool")
                return False

            # Check python-xlib
            import Xlib.display
            return True
        except ImportError:
            print("Error: python-xlib is required for Linux. Install with: pip install python-xlib")
            return False

    elif system == "Darwin":  # macOS
        # Check if osascript is available (should be on all macOS systems)
        try:
            subprocess.run(['which', 'osascript'], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            print("Error: osascript not found. This should be available on all macOS systems.")
            return False

    else:
        print(f"Error: Unsupported platform: {system}")
        return False


def main() -> None:
    """
    Main function to run the mouse movement simulator indefinitely.
    """
    print("Mouse Movement Simulator for Availability Maintenance")
    print(f"Platform: {platform.system()}")
    print("Press Ctrl+C to stop the script")
    print("-" * 50)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Display current configuration
    if config.VERBOSE_LOGGING:
        print("Configuration:")
        print(f"  Linear movements: {config.USE_LINEAR_MOVEMENT}")
        print(f"  Bezier movements: {config.USE_BEZIER_MOVEMENT}")
        print(f"  Wait time range: {config.WAIT_TIME_RANGE} seconds")
        print(f"  Screen margin: {config.SCREEN_MARGIN}")
        print("-" * 50)

    try:
        # Get screen bounds based on configuration
        min_x, min_y, max_x, max_y = get_screen_bounds()
        screen_width, screen_height = get_screen_dimensions()
        print(f"Screen dimensions: {screen_width} x {screen_height}")
        print(f"Movement area: ({min_x}, {min_y}) to ({max_x}, {max_y})")

        movement_count = 0
        consecutive_count = {'linear': 0, 'bezier': 0}
        last_movement_type = None
        controller = MouseController()

        while True:
            movement_count += 1

            # Get current position
            current_x, current_y = controller.get_cursor_pos()

            # Decide if this should be a small movement
            if (config.ENABLE_SMALL_MOVEMENTS and
                random.random() < config.SMALL_MOVEMENT_CHANCE):
                target_x, target_y = get_small_movement_position(current_x, current_y)
                movement_size = "small"
            else:
                target_x, target_y = get_next_position(max_x, max_y, min_x, min_y)
                movement_size = "normal"

            if config.PRINT_MOVEMENT_DETAILS:
                print(f"Movement {movement_count} ({movement_size}): From ({current_x}, {current_y}) to ({target_x}, {target_y})")

            # Choose movement type
            movement_type = choose_movement_type(consecutive_count)

            # Update consecutive count
            if movement_type == last_movement_type:
                consecutive_count[movement_type] += 1
            else:
                consecutive_count[movement_type] = 1
                # Reset the other type's count
                other_type = 'bezier' if movement_type == 'linear' else 'linear'
                consecutive_count[other_type] = 0

            # Ensure we don't exceed max consecutive same type
            if consecutive_count[movement_type] > config.MAX_CONSECUTIVE_SAME_TYPE:
                # Switch to the other enabled type
                if movement_type == 'linear' and config.USE_BEZIER_MOVEMENT:
                    movement_type = 'bezier'
                elif movement_type == 'bezier' and config.USE_LINEAR_MOVEMENT:
                    movement_type = 'linear'
                consecutive_count[movement_type] = 1
                # Reset the other type
                other_type = 'bezier' if movement_type == 'linear' else 'linear'
                consecutive_count[other_type] = 0

            last_movement_type = movement_type

            # Execute movement
            if movement_type == 'linear':
                linear_mouse_move(target_x, target_y)
            else:
                human_like_mouse_move(target_x, target_y)

            if config.PRINT_MOVEMENT_DETAILS:
                print(f"Completed {movement_type} movement to ({target_x}, {target_y})")

            # Wait time between movements
            wait_time = random.randint(*config.WAIT_TIME_RANGE)
            if config.VERBOSE_LOGGING:
                print(f"Waiting {wait_time} seconds until next movement...")
                print("-" * 50)

            time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\nScript stopped by user. Goodbye!")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Script terminated.")


if __name__ == "__main__":
    main()
