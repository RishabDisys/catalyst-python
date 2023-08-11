from flask import Flask, request
from pynput import mouse
from infi.systray import SysTrayIcon
from datetime import datetime
from PIL import ImageGrab
import requests, os

app = Flask(__name__)

sessionId = ''
session_data = {}

def on_click(x, y, button, pressed):
    global sessionId

    if pressed:
        print(f'Mouse clicked at ({x}, {y}) with {button}')
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S.%fZ')
        click_type = str(button).split('.')[1].capitalize()

        current_dir = os.getcwd()
        screenshot_filename = f'{timestamp}.png'
        screenshotFolder = os.path.join(current_dir, 'screenshots')
        sessionSubFolder = os.path.join(current_dir, 'screenshots', sessionId)
        if not os.path.exists(screenshotFolder): os.mkdir(screenshotFolder)
        if not os.path.exists(sessionSubFolder): os.mkdir(sessionSubFolder)

        screenshot_path = os.path.join(current_dir, 'screenshots', sessionId, screenshot_filename)
        session_data["mouseClicks"].append({
            "timeStamp": timestamp,
            "clickType": click_type,
            "xLocation": x,
            "yLocation": y,
            "fileName": screenshot_filename 
        })
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)

mouse_listener = mouse.Listener(on_click=on_click)

@app.route('/start-session', methods=['GET'])
def handle_start():
    global session_data
    global sessionId

    sessionId = request.args.get('id')
    mouse_listener.start()
    session_data = {
        'sessionId': sessionId,
        'startedAt': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'mouseClicks': [],
    } 
    return '200'

@app.route('/end-session', methods=['GET'])
def handle_end():
    global session_data
    global sessionId

    session_data['endedAt'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    response = requests.put('https://appili.gives/items', json=session_data)
    session_data, sessionId = {}, ''
    mouse_listener.stop()
    return '200'

if __name__ == '__main__':
    def quit(systray):
        systray.shutdown()

    menu_options = ()
    systray = SysTrayIcon("favicon.ico", "Dexian Catalyst", menu_options)
    systray.start()
    app.run()