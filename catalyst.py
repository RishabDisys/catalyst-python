from pynput import mouse, keyboard
import time
import json
from datetime import datetime

# Create an object to store session data
session_data = {
    "startedAt": None,
    "endedAt": None,
    "sessionId": None,
    "mouseClicks": []
}

# Mouse Click Listener
def on_click(x, y, button, pressed):
    if pressed:
        print(f'Mouse clicked at ({x}, {y}) with {button}')
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        click_type = str(button).split('.')[1].capitalize()
        session_data["mouseClicks"].append({
            "timeStamp": timestamp,
            "clickType": click_type,
            "xLocation": x,
            "yLocation": y
        })

# Keyboard Listener for Esc key
def on_key_press(key):
    try:
        print(f'Key pressed: {key.char}')
    except AttributeError:
        print(f'Special key pressed: {key}')
        
    if key == keyboard.Key.esc:
        session_data["endedAt"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        # Print the collected event data in JSON format
        print(json.dumps(session_data, indent=2))
        # Stop the program when the Escape key is pressed
        return False

# Set session start time and ID
session_data["startedAt"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
session_data["sessionId"] = "52cfd211su2a2"  # Replace with your session ID

# Start Mouse Listener
mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

# Start Keyboard Listener
keyboard_listener = keyboard.Listener(on_press=on_key_press)
keyboard_listener.start()

# Keep the listeners running
mouse_listener.join()
keyboard_listener.join()