from flask import Flask, request,render_template
from pynput import mouse
from infi.systray import SysTrayIcon
from datetime import datetime
from PIL import ImageGrab
import requests, os

app = Flask(__name__,template_folder='.')

sessionId = ''
session_data = {}

def on_click(x, y, button, pressed):
    global sessionId

    if pressed:
        print(f'Mouse clicked at ({x}, {y}) with {button}')
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S.%fZ')
        click_type = str(button).split('.')[1].capitalize()

        current_dir = os.getcwd()                                            #(it should be session id)
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
   
    start_session_message = "The session is successfully started, with session ID = "+ str(sessionId) + " The Response is 200."
    print (start_session_message)
    print (sessionId)
    return [start_session_message, sessionId]

@app.route('/end-session', methods=['GET'])
def handle_end():
    global session_data
    global sessionId

    end_session_message = "The session is successfully ended, with session ID = "+ str(sessionId) + " The Response is 200."
    print (end_session_message)
    print (sessionId)

    session_data['endedAt'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    response = requests.put('https://appili.gives/items', json=session_data)
    session_data, sessionId = {}, ''
    mouse_listener.stop()

   
    return [end_session_message]

@app.route('/set-session', methods=['POST'])
def handle_set_session():
    global sessionId

    session_id = request.form.get('session-id')
    sessionId = session_id

    current_dir = os.getcwd()
    session_sub_folder = os.path.join(current_dir, 'screenshots', sessionId)
    if not os.path.exists(session_sub_folder):
        os.mkdir(session_sub_folder)

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