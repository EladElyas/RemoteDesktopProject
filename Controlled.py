import os

import keyboard
import socket
from threading import Thread
from pynput.mouse import Button, Controller
from pynput import mouse
import pyautogui
from PIL import Image
mouse = Controller()
def create_socket(port):# a method that receives a port and creates a socket for that port, therefore allowing multiple client-server connections at the same time
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("10.100.102.35", port))
    server.listen()
    print("waiting for connection...")
    try:
        cs, ca = server.accept()
        print("Connection established!")
        return cs
    except Exception as e:
        print("connection failed: ", e)

#mouse
def get_movements():# a method that receives the mouse movements from the controlling computer and moves the mouse accordingly
    cs = create_socket(10000)
    width, height = pyautogui.size()# get the size of the local screen and send it to the controlling computer to adjust the coordinates for the screen size ratio
    size = str((width, height))
    cs.send(size.encode())
    socket_file = cs.makefile('r')
    while True:
        curr = socket_file.readline().strip().split(",")
        x = int(float(curr[0]))
        y = int(float(curr[1]))
        mouse.position = (x,y)



def get_clicks():# a method that receives the mouse clicks from the controlling computer and performs them on the local computer
    cs = create_socket(10001)
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


def get_scrolls():# a method that receives the mouse scrolls from the controlling computer and performs them on the local computer
    scroll_socket = create_socket(10002)
    while True:
        data = scroll_socket.recv(1024).decode()
        if not data:
            break
        parts = data.strip().split(",")
        for i in range(0, len(parts) - 1, 2):
            dx = int(parts[i])
            dy = int(parts[i + 1])
            mouse.scroll(dx,dy)

def get_keys():# a method that receives the key presses and releases from the controlling computer and performs them on the local computer
    key_client = create_socket(10003)
    key_file = key_client.makefile('r')
    while True:
        parts = key_file.readline().strip().split(":")
        key = parts[1]
        if parts[0] == "down":
            keyboard.press(key)
        elif parts[0] == "up":
            keyboard.release(key)

def send_screen_image():# a method that sends screenshots of the local computer to the controlling computer in order to stream the screen
    image_client = create_socket(10004)
    file_path = "C:\\Users\\elade\\OneDrive\\Pictures\\screen_for_remotedesktop.png"
    converted_file_path = file_path = "C:\\Users\\elade\\OneDrive\\Pictures\\screen_for_remotedesktop.jpeg"
    while True:
        pyautogui.screenshot(file_path)
        image = Image.open(file_path)
        image.save(converted_file_path)#converting the screenshot to jpeg format to reduce the file size, therefore making the streaming faster
        with open(file_path, "rb") as f:
            data = f.read(1024)
            while data:
                image_client.send(data)
                rsp = image_client.recv(1024)
                if rsp == b"Yes":
                    data = f.read(1024)
                    continue
                else:
                    break
        image_client.send(b"EOF")
        os.remove(converted_file_path)


t1 = Thread(target=get_movements)
t2 = Thread(target=get_clicks)
t3 = Thread(target=get_scrolls)
t4 = Thread(target= get_keys)
t5 = Thread(target= send_screen_image)
t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t1.join()
t2.join()
t3.join()
t4.join()
t5.join()