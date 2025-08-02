import keyboard
import socket
import os
from threading import Thread
from pynput.mouse import Button, Controller
from pynput import mouse
from functools import partial
from PIL import Image, ImageTk
import tkinter as tk
import pyautogui
root = tk.Tk()

def create_socket(port):#a method that receives a port and creates a socket for that port, therefore allowing multiple client-server connections at the same time
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(("10.100.102.35", port))
    except Exception as e:
        print("connection failed: ", e)
    return client
#keyboard
def send_key(client, event):#sending the key press or release event to the server
    message = f"{event.event_type}:{event.name}\n"
    client.send(message.encode())
    
def listen_for_keys():#a method that listens for keyboard events
    client = create_socket(10003)
    keyboard.hook(partial(send_key, client))
    keyboard.wait()

#mouse

def click_detected(client, x, y, button, pressed):#a method that sends whether the mouse button was pressed or released, along with wwhich button was pressed or released
    if pressed:
        client.send(b"mouse pressed")
    else:
        client.send(b"mouse released")
    client.send(str(button).encode())


def listen_for_clicks():#a method that listens for mouse clicks
    click_client = create_socket(10001)
    click_callback = partial(click_detected, click_client)
    with mouse.Listener(on_click= click_callback) as listener:
        listener.join()

def scroll_detected(client, x, y, dx, dy):#a method that sends how much the mouse was scrolled to the server
    client.send(f"{dx},{dy}".encode())

def listen_for_scrolls():#a method that listens for mouse scrolls
    scroll_client = create_socket(10002)
    scroll_callback = partial(scroll_detected, scroll_client)
    with mouse.Listener(on_scroll= scroll_callback) as listener:
        listener.join()

def movement_detected(client, height_ratio, width_ratio, x, y):# a method that sends the position of where the mouse should be moved to in the server, after
    #adjusting the coordinates according to the remote screen size in relation to the local screen size
    x = x*width_ratio
    y = y*height_ratio
    try:
        client.send(f"{x},{y}\n".encode())
    except Exception as e:
        print("Send failed: ", e)

def listen_for_movements():# a method that listens for mouse movements and sends the ratio of the coordinates to the server in order to adjust the mouse position
    #according to the remote screen size in relation to the local screen size
    movement_client = create_socket(10000)
    remote_size = movement_client.recv(1024).decode()
    remote_width, remote_height = remote_size.strip().replace("(", "").replace(")", "").replace(" ", "").split(",")
    local_width, local_height = pyautogui.size()
    height_ratio = int(remote_height) / local_height
    width_ratio = int(remote_width) / local_width

    movement_callback = partial(movement_detected, movement_client, height_ratio, width_ratio)
    with mouse.Listener(on_move=movement_callback) as listener:
        listener.join() 

        
def receive_screen_image(image_client, file_path):# a method that receives the screen image from the server and saves it to a file
        with open(file_path, "wb") as f:
            while True:
                data = image_client.recv(1024)
                if data == b"EOF":
                    break
                else:
                    image_client.send(b"Yes")
                    f.write(data)

def display_screen_image():# a method that displays the screen image received from the server in a tkinter window, and then deletes the image file before updating the image
    file_path = "c:\\Users\\אלעד\\Downloads\\screen_image.jpeg"
    image_client = create_socket(10004)
    root.attributes("-fullscreen", True)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    label = tk.Label(root)
    label.pack()
    while True:
        receive_screen_image(image_client, file_path)
        image = Image.open(file_path)
        image = image.resize((screen_width, screen_height))
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        root.update()
        os.remove(file_path)



t1 = Thread(target= listen_for_movements)
t2 = Thread(target= listen_for_clicks)
t3 = Thread(target= listen_for_scrolls)
t4 = Thread(target= listen_for_keys)
t5 = Thread(target= display_screen_image)
t1.start()
t2.start()
t3.start()
t4.start()
t5.start()

root.mainloop()

t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
    








