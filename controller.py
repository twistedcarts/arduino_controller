import time
import serial
import tkinter as tk
from pynput.mouse import Listener
import threading

status_message = "initializing arduino..."
try:
    arduino = serial.Serial('COM7', 9500, timeout=1) # change "COM7" and "9500" to your specific arduino setup, the com port will vary between devices
    status_message = "initialized arduino"
except serial.SerialException:
    status_message = "failed to initialize arduino"

left_pressed = False
right_pressed = False

# refer to comments in firmware/firmware.ino on how to change the recoil values and add more weapons
weapon_modes = {
    "M4": b"M",    # M4
    "MPX": b"X",   # MPX
    "P90": b"P",   # P90
    "F2": b"F",    # F2
    "SMG-12": b"S" # SMG-12
}

selected_weapon = "MPX" # defualt selection

def update_gui():
    status_label.config(text=f"{status_message}\nleft: {'pressed' if left_pressed else 'released'} | "
                             f"right: {'pressed' if right_pressed else 'released'}")
    recoil_label.config(text=f"selected: {selected_weapon}")

def on_click(x, y, button, pressed):
    global left_pressed, right_pressed
    if button.name == "left":
        left_pressed = pressed
    elif button.name == "right":
        right_pressed = pressed

    # mouse i/o detection
    if left_pressed and right_pressed:
        if pressed:
            arduino.write(b"1")
    else:
        arduino.write(b"0")
    
    root.after(10, update_gui)

def on_weapon_change(event):
    global selected_weapon
    selected_weapon = weapon_var.get()
    arduino.write(weapon_modes[selected_weapon])
    root.after(10, update_gui)

def run_listeners():
    mouse_listener = Listener(on_click=on_click, daemon=True)
    mouse_listener.start()
    mouse_listener.join()

# tkinter setup
root = tk.Tk()
root.title("Spotify")
root.geometry("300x200")
root.configure(padx=10, pady=10)

status_label = tk.Label(root, text=status_message, font=("Arial", 12))
status_label.pack(pady=10)

recoil_label = tk.Label(root, text=f"Mode: {selected_weapon}", font=("Arial", 12))
recoil_label.pack(pady=10)

weapon_frame = tk.Frame(root)
weapon_frame.pack(pady=10)

weapon_label = tk.Label(weapon_frame, text="Weapon:", font=("Arial", 12))
weapon_label.pack(side=tk.LEFT, padx=5)

weapon_var = tk.StringVar(root)
weapon_var.set(selected_weapon)
weapon_dropdown = tk.OptionMenu(weapon_frame, weapon_var, *weapon_modes.keys(), command=on_weapon_change)
weapon_dropdown.pack(side=tk.LEFT)

threading.Thread(target=run_listeners, daemon=True).start()
root.mainloop()
arduino.close()
