from flask import Flask, request
from pynput import mouse
from infi.systray import SysTrayIcon
from datetime import datetime

import requests, os, signal

app = Flask(__name__)

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

session_data = {}
mouse_listener = mouse.Listener(on_click=on_click)

@app.route('/start-session', methods=['GET'])
def handle_start():
    global session_data
    mouse_listener.start()
    session_data ={
        'startedAt': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'mouseClicks': [],
    } 
    return '200'

@app.route('/end-session', methods=['GET'])
def handle_end():
    global session_data
    session_data['sessionId'] = request.args.get('id')
    session_data['endedAt'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    response = requests.put('https://appili.gives/items', json=session_data)
    session_data = {}
    mouse_listener.stop()
    return '200'

if __name__ == '__main__':
    def quit(systray):
        systray.shutdown()

    menu_options = ()
    systray = SysTrayIcon("favicon.ico", "Dexian Catalyst", menu_options)
    systray.start()
    app.run()