import os

import keyboard
import socket
from threading import Thread
from pynput.mouse import Button, Controller
from pynput import mouse
import pyautogui
from PIL import Image
mouse = Controller()


#mouse
def get_movements(cs):# a method that receives the mouse movements from the controlling computer and moves the mouse accordingly
    width, height = pyautogui.size()# get the size of the local screen and send it to the controlling computer to adjust the coordinates for the screen size ratio
    size = str((width, height))
    cs.send(size.encode())
    socket_file = cs.makefile('r')
    while True:
        curr = socket_file.readline().strip().split(",")
        x = int(float(curr[0]))
        y = int(float(curr[1]))
        mouse.position = (x,y)



def get_clicks(cs):# a method that receives the mouse clicks from the controlling computer and performs them on the local computer
    while True:
        data = cs.recv(1024)
        if data == b"mouse pressed":
            button = cs.recv(1024)
            if button == b"Button.left":
                mouse.press(Button.left)
            elif button == b"Button.right":
                mouse.press(Button.right)
            else:
                mouse.press(Button.middle)
        elif data == b"mouse released":
            button = cs.recv(1024)
            if button == b"Button.left":
                mouse.release(Button.left)
            elif button == b"Button.right":
                mouse.release(Button.right)
            else:
                mouse.release(Button.middle)


def get_scrolls(cs):# a method that receives the mouse scrolls from the controlling computer and performs them on the local computer
    while True:
        data = cs.recv(1024).decode()
        if not data:
            break
        parts = data.strip().split(",")
        for i in range(0, len(parts) - 1, 2):
            dx = int(parts[i])
            dy = int(parts[i + 1])
            mouse.scroll(dx,dy)

def get_keys(cs):# a method that receives the key presses and releases from the controlling computer and performs them on the local computer
    key_file = cs.makefile('r')
    while True:
        parts = key_file.readline().strip().split(":")
        key = parts[1]
        if parts[0] == "down":
            keyboard.press(key)
        elif parts[0] == "up":
            keyboard.release(key)

def send_screen_image(cs):# a method that sends screenshots of the local computer to the controlling computer in order to stream the screen
    file_path = "C:\\Users\\elade\\OneDrive\\Pictures\\screen_for_remotedesktop.png"
    converted_file_path = file_path = "C:\\Users\\elade\\OneDrive\\Pictures\\screen_for_remotedesktop.jpeg"
    while True:
        pyautogui.screenshot(file_path)
        image = Image.open(file_path)
        image.save(converted_file_path)#converting the screenshot to jpeg format to reduce the file size, therefore making the streaming faster
        with open(file_path, "rb") as f:
            data = f.read(1024)
            while data:
                cs.send(data)
                rsp = cs.recv(1024)
                if rsp == b"Yes":
                    data = f.read(1024)
                    continue
                else:
                    break
        cs.send(b"EOF")
        os.remove(converted_file_path)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("10.100.102.35", 10000)) 
    server.listen(5)
    
    subsystems = {"0": get_movements, "1": get_clicks, "2": get_scrolls, "3": get_keys, "4": send_screen_image}
    print("Server online. Waiting for 5 connections on port 10000...")
    
    count = 0
    while count < 5:
        cs, addr = server.accept()
        choice = cs.recv(1).decode() # Identify which thread this is
        if choice in subsystems:
            Thread(target=subsystems[choice], args=(cs,), daemon=True).start()
            count += 1

    while True:
        time.sleep(10)