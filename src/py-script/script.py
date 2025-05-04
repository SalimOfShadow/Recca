import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import sys
import os
import psutil
import requests
from utils.send_action import send_action



# Build by running : 

# pyinstaller --name py-script --onefile --add-data "images;images" script.py
# or  
# python -m PyInstaller --name py-script --onefile --add-data "images;images" script.py


# Utility function to get the path for a bundled resource
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# selected_game = "KOF XIII"
if os.getenv("CURRENT_GAME") is None:
    os.environ["CURRENT_GAME"] = "KOF XIII" # TODO - prompt the user to select a game if empty


selected_game = os.getenv("CURRENT_GAME")
print("Selected game:", selected_game)

# Base directory for images
games = {
    "KOF XIII": {
        "window_name": "THE KING OF FIGHTER XIII GLOBAL MATCH",
        "process_name": "game.exe",
        "start_image": resource_path("images/KOF_XIII/start-image.png"), # TODO - Account for quick rematches
        "stop_images": [
            resource_path("images/KOF_XIII/stop-image.png"),  
            resource_path("images/KOF_XIII/disconnected-screen.png"),  
            # resource_path("images/KOF_XIII/error-screen-1.png"),
            # resource_path("images/KOF_XIII/error-screen-2.png")
        ]
    },
    "USF4": {
        "window_name": "SSFIVAE",
        "process_name": "SSFIV.exe",
        "start_image": resource_path("images/USF4/start-image.png"),
        "stop_images": [
            resource_path("images/USF4/stop-image.png"),
            resource_path("images/USF4/disconnected-screen.png"),
            resource_path("images/USF4/error-screen-1.png"),
            resource_path("images/USF4/error-screen-2.png")
        ]
    },
    "GUILTY GEAR STRIVE": {
        "window_name": "Guilty Gear -Strive-",
        "process_name": "GGST-Win64-Shipping.exe",
        "start_image": resource_path("images/GUILTY_GEAR_STRIVE/start-image.png"),
        "stop_images": [
            resource_path("images/GUILTY_GEAR_STRIVE/stop-image.png"),
            resource_path("images/GUILTY_GEAR_STRIVE/disconnected-screen.png"),
            resource_path("images/GUILTY_GEAR_STRIVE/error-screen-1.png"),
            resource_path("images/GUILTY_GEAR_STRIVE/error-screen-2.png")
        ]
    },
    "TEKKEN 8": {
        "window_name": "Tekken 8",
        "start_image": resource_path("images/TEKKEN_8/start-image.png"),
        "stop_images": [
            resource_path("images/TEKKEN_8/stop-image.png"),
            resource_path("images/TEKKEN_8/disconnected-screen.png"),
            resource_path("images/TEKKEN_8/error-screen-1.png"),
            resource_path("images/TEKKEN_8/error-screen-2.png")
        ]
    }
}


def check_running_process(process_name):
    global process_running
    process_running = False  # Reset the flag before starting the check
    
    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # If the process name matches, return True
            if proc.info['name'].lower() == process_name.lower():
                print(f"Found the process: {proc.info['name']} with PID: {proc.info['pid']}")
                process_running = True
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def find_match(game, action):
    game_object = games[game]
    
    # Check if the process is running
    process_name = game_object["process_name"]
    if not process_running: 
        if not check_running_process(process_name):
            print(f"Process '{process_name}' is not running. Exiting...")
            sys.exit()  # Exit if the process is not found

    images = []
    if action == "start":
        images = [game_object["start_image"]]

    elif action == "stop":
        images = game_object["stop_images"]

    window = gw.getWindowsWithTitle(game_object["window_name"])
    if not window:
        print("Couldn't find the game's instances...Is it running?")
        sys.exit()  # Exit if the window is not found

    window = window[0]

    x = window.left
    y = window.top
    w = window.width
    h = window.height

    screenshot = pyautogui.screenshot(region=(x, y, w, h))
    img_source = np.array(screenshot)
    img_source = cv2.cvtColor(img_source, cv2.COLOR_BGR2GRAY)
    # Resizing the image source to 1080p,as the template images were captured at that resolution.
    img_source = cv2.resize(img_source, (1920, 1080))   # TODO - FIX THE NON WORKING SOURCE IMAGE FOR USF4

    for image in images: 
        img_test = cv2.imread(image)
        img_test = cv2.cvtColor(img_test, cv2.COLOR_RGB2GRAY)
        result = cv2.matchTemplate(img_source, img_test, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.89:
            print("Match found at location", max_loc)
            print("This is the max val ", max_val)
            print(f"This was the image : {image}")
            
            # Check if the matched image is a disconnection or error image
            if "disconnected" in image or "error" in image:
                try:
                    url = f"http://localhost:4609/stop-recording"
                    headers = {
                        "game": game,
                        "disconnected": "true"
                    }
                    response = requests.get(url, headers=headers)
                    return response 
                except: print("Encountered an error while sending the request") 
                print("Disconnection image found")
                return True

            send_action(selected_game, action)

            w = img_test.shape[1]
            h = img_test.shape[0]
            return True
    else:
        # print("No match found", max_val)
        return False

state = "start"
process_running = False

while True:
    if state == "start":
        if find_match(selected_game, "start"):
            print("Now searching for the ending image")
            state = "end"
    elif state == "end":
        if find_match(selected_game, "stop"):
            state = "start"