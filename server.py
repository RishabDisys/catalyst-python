from flask import Flask, request, render_template
from flask_cors import CORS
from pynput import mouse 
from infi.systray import SysTrayIcon
from datetime import datetime
from PIL import ImageGrab
import requests, os, threading

import base64

app = Flask(__name__,template_folder='.')
CORS(app)

mouse_thread = None
sessionId = ''
session_data = {}

def on_click(x, y, button, pressed):
    global sessionId

    if pressed and 'mouseClicks' in session_data:
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

        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)

        session_data["mouseClicks"].append({
            "timeStamp": timestamp,
            "clickType": click_type,
            "xLocation": x,
            "yLocation": y,
            "filePath": screenshot_path
        })

def start_mouse_thread():
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

@app.route('/start-session', methods=['GET'])
def handle_start():
    global session_data
    global sessionId
    global mouse_thread

    sessionId = request.args.get('id')
    if not mouse_thread or not mouse_thread.is_alive():
        mouse_thread = threading.Thread(target=start_mouse_thread)
        mouse_thread.start()
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
    global mouse_thread

    session_data['endedAt'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    response = requests.put('https://appili.gives/items', json=session_data)
    session_data, sessionId = {}, ''
    if mouse_thread and mouse_thread.is_alive():
        mouse_thread.join(timeout=0)
    return '200'

@app.route('/get-image')
def handle_image():
    sessionId = request.args.get('id')
    filename = request.args.get('file')
    screenshot_path = os.path.join(os.getcwd() , 'screenshots', sessionId, filename + '.png')
    with open(screenshot_path, "rb") as image_file:
        base64_encoded = base64.b64encode(image_file.read())
        return base64_encoded.decode("utf-8")  
    
@app.route('/health-check')
def handle_health():
    return '200'      

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    def quit(systray):
        systray.shutdown()
    menu_options = ()
    systray = SysTrayIcon("favicon.ico", "Dexian Catalyst", menu_options)
    systray.start()
    app.run()