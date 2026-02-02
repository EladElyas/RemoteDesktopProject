import keyboard
import socket
import os
from threading import Thread
from numpy import choose
from pynput.mouse import Button, Controller
from pynput import mouse
from functools import partial
from PIL import Image, ImageTk
import tkinter as tk
import pyautogui
import io

def connect_subsystem(id_number):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(("10.100.102.35", 10000))
        client.send(str(id_number).encode())      # Send ID immediately
        return client
    except Exception as e:
        print(f"Connection {id_number} failed: {e}")
        return None
#keyboard
def send_key(client, event):#sending the key press or release event to the server
    message = f"{event.event_type}:{event.name}\n"
    client.send(message.encode())
    
def listen_for_keys():#a methodhat listens for keyboard events
    client = connect_subsystem("3")
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
    click_client = connect_subsystem("1")
    click_callback = partial(click_detected, click_client)
    with mouse.Listener(on_click= click_callback) as listener:
        listener.join()

def scroll_detected(client, x, y, dx, dy):#a method that sends how much the mouse was scrolled to the server
    client.send(f"{dx},{dy}".encode())

def listen_for_scrolls():#a method that listens for mouse scrolls
    scroll_client = connect_subsystem("2")
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
    movement_client = connect_subsystem("0")
    remote_size = movement_client.recv(1024).decode()
    remote_width, remote_height = remote_size.strip().replace("(", "").replace(")", "").replace(" ", "").split(",")
    local_width, local_height = pyautogui.size()
    height_ratio = int(remote_height) / local_height
    width_ratio = int(remote_width) / local_width

    movement_callback = partial(movement_detected, movement_client, height_ratio, width_ratio)
    with mouse.Listener(on_move=movement_callback) as listener:
        listener.join() 

        
def receive_screen_image(image_client):
    image_buffer = io.BytesIO()
    
    while True:
        data = image_client.recv(1024)
        if b"EOF" in data:
            image_buffer.write(data.split(b"EOF")[0])
            break
        else:
            image_client.send(b"Yes")
            image_buffer.write(data)
    image_buffer.seek(0)
    return image_buffer

def display_screen_image():# a method that displays the screen image received from the server in a tkinter window, and then deletes the image file before updating the image
    image_client = connect_subsystem("4")
    root.attributes('-fullscreen', True)
    resolution = tuple(pyautogui.size())
    label = tk.Label(root)
    label.pack()
    while True:
        virtual_file = receive_screen_image(image_client)
        image = Image.open(virtual_file)
        image = image.resize(resolution)
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo
        root.update()


def connection_list(choose):# a method that displays a tkinter window with an entry box to enter the connection ID of the desired connection to connect to
    choose.title("Available Connections Board")
    choose.attributes('-fullscreen', True)

    #creating an empty label to act as an anchor, in order to place the other widgets in the desired positions
    buffer_label = tk.Label(choose, text="")
    buffer_label.grid(row=0, column=0, padx=340, pady=10)

    choice_label = tk.Label(choose, text="Choose a connection ID to connect to:")
    choice_label.grid(row=0, column=1, padx=10, pady=10)
    choice_label.config(font = ("Arial", 20))

    choice_label_bar = tk.Entry(choose)
    choice_label_bar.grid(row=5, column=1, padx=10, pady=10)
    choice_label_bar.config(font = ("Arial", 20))

    submit_button = tk.Button(choose, text="Connect", command=lambda: choose.quit())
    submit_button.grid(row=7, column=1, padx=10, pady=10)
    submit_button.config(font = ("Arial", 20))
    choose.mainloop()
    return choice_label_bar.get()


def choose_connection():# a method that allows the user to choose which connection to connect to from a list of available connections
    
    choose = tk.Tk()
    target_ip = connection_list(choose)
    choose.destroy()
    print(target_ip)
    return target_ip


choose_connection()

root = tk.Tk()

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
        








