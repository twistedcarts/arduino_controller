import customtkinter as ctk
import serial
import time
import threading
import random
import string
from pynput.mouse import Listener

# == appearance ==
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# == arduino ==
status_message = "initializing ard..."
try:
    arduino = serial.Serial('COM3', 9500, timeout=1)
    status_message = "initialized ard"
except serial.SerialException:
    status_message = "failed to initialize ard"

# == globals ==
left_pressed = False
right_pressed = False
selected_weapon = "C8-SFW"
custom_recoil_y = 0
custom_recoil_x = 0

weapon_configs = {
    "C8-SFW": {"name": "C8-SFW", "recoil_Y": 30, "recoil_X": 0},
    "F2": {"name": "F2", "recoil_Y": 50, "recoil_X": -2},
    "MPX": {"name": "MPX", "recoil_Y": 11, "recoil_X": 0},
    "P90": {"name": "P90", "recoil_Y": 30, "recoil_X": 1},
}

# == gui ==
app = ctk.CTk()
app.geometry("700x450")
app.title("".join(random.choices(string.ascii_letters + string.digits, k=12)))

font_main = ctk.CTkFont(size=15, family="Segoe UI")
font_title = ctk.CTkFont(size=18, weight="bold", family="Segoe UI")
text_color = "#FFFFFF"

sidebar = ctk.CTkFrame(app, width=150, corner_radius=0)
sidebar.pack(side="left", fill="y")
ctk.CTkLabel(sidebar, text="", height=20).pack()

tab_buttons = {}
content_frames = {}
selected_tab = "Recoil Control"

def switch_tab(tab_name):
    global selected_tab
    selected_tab = tab_name
    for name, btn in tab_buttons.items():
        if name == tab_name:
            btn.configure(fg_color="#ffaa00", text_color="black", hover_color="#ffaa00")
        else:
            btn.configure(fg_color="transparent", text_color=text_color, hover_color="#333")
    for frame in content_frames.values():
        frame.pack_forget()
    content_frames[tab_name].pack(fill="both", expand=True, padx=20, pady=20)

for name, emoji in [("Recoil Control", "👁"), ("Weapons", "🔥"), ("Configs", "⚙️")]:
    btn = ctk.CTkButton(
        sidebar,
        text=f"{emoji} {name}",
        fg_color="transparent",
        hover_color="#333",
        anchor="w",
        corner_radius=6,
        font=font_main,
        text_color=text_color,
        command=lambda n=name: switch_tab(n)
    )
    btn.pack(pady=6, padx=10, fill="x")
    tab_buttons[name] = btn

main_frame = ctk.CTkFrame(app, corner_radius=0)
main_frame.pack(side="left", fill="both", expand=True)

ctk.CTkLabel(main_frame, text="Recoil Control", font=font_title, text_color=text_color)\
    .pack(anchor="nw", padx=30, pady=(20, 0))

content_border = ctk.CTkFrame(main_frame, corner_radius=10, border_width=2, border_color="#444")
content_border.pack(fill="both", expand=True, padx=20, pady=20)

# == recoil tab ==
recoil_frame = ctk.CTkFrame(content_border, fg_color="transparent")
content_frames["Recoil Control"] = recoil_frame

labels = ["Left", "Right", "Down", "Up"]
entry_vars = {}

for i, label in enumerate(labels):
    ctk.CTkLabel(recoil_frame, text=label, font=font_main).grid(row=i+1, column=0, sticky="w", padx=(0, 10), pady=5)
    var = ctk.StringVar()
    entry_vars[label] = var
    ctk.CTkEntry(recoil_frame, justify="center", width=60, textvariable=var).grid(row=i+1, column=1, pady=5)

def save_custom_values():
    global selected_weapon, custom_recoil_y, custom_recoil_x
    try:
        custom_recoil_x = int(entry_vars["Left"].get()) - int(entry_vars["Right"].get())
        custom_recoil_y = int(entry_vars["Down"].get()) - int(entry_vars["Up"].get())
        weapon_configs["Custom"] = {"name": "Custom", "recoil_Y": custom_recoil_y, "recoil_X": custom_recoil_x}
        selected_weapon = "Custom"
        if status_message == "initialized ard":
            cfg = weapon_configs["Custom"]
            cfg_string = f"CFG:{cfg['name']},{cfg['recoil_Y']},{cfg['recoil_X']}\n"
            arduino.write(cfg_string.encode())
            print(f"Sent to Arduino: {cfg_string.strip()}")
    except ValueError:
        print("Invalid recoil values.")

ctk.CTkButton(recoil_frame, text="Save", font=font_main, width=80, command=save_custom_values)\
    .grid(row=5, column=0, pady=(15, 0), sticky="w")

# == weapons tab ==
weapons_frame = ctk.CTkFrame(content_border, fg_color="transparent")
content_frames["Weapons"] = weapons_frame

ctk.CTkLabel(weapons_frame, text="Select Weapon", font=font_main)\
    .pack(anchor="w", padx=10, pady=(10, 5))

weapon_var = ctk.StringVar(value=selected_weapon)

def on_weapon_change(choice):
    global selected_weapon
    selected_weapon = choice
    if status_message == "initialized ard":
        cfg = weapon_configs.get(choice, {"name": "Unknown", "recoil_Y": 0, "recoil_X": 0})
        cfg_string = f"CFG:{cfg['name']},{cfg['recoil_Y']},{cfg['recoil_X']}\n"
        arduino.write(cfg_string.encode())
        print(f"Sent to Arduino: {cfg_string.strip()}")

weapon_dropdown = ctk.CTkOptionMenu(
    weapons_frame,
    values=list(weapon_configs.keys()),
    variable=weapon_var,
    command=on_weapon_change,
    font=font_main,
    width=200
)
weapon_dropdown.pack(anchor="w", padx=10, pady=(0, 20))

ctk.CTkButton(
    weapons_frame,
    text="Save",
    font=font_main,
    width=100,
    command=lambda: on_weapon_change(weapon_var.get())
).pack(anchor="w", padx=10)

# == placeholder tabs ==
configs_frame = ctk.CTkFrame(content_border, fg_color="transparent")
content_frames["Configs"] = configs_frame
ctk.CTkLabel(configs_frame, text="not implemented", font=font_main).pack(padx=20, pady=20)

# == backend ==
def on_click(x, y, button, pressed):
    global left_pressed, right_pressed
    if button.name == "left":
        left_pressed = pressed
    elif button.name == "right":
        right_pressed = pressed

    if left_pressed and right_pressed:
        if pressed:
            arduino.write(b"1\n")
    else:
        arduino.write(b"0\n")

listener_thread = threading.Thread(
    target=lambda: Listener(on_click=on_click, daemon=True).start(),
    daemon=True
)
listener_thread.start()

# == startup ==
if status_message == "initialized ard":
    time.sleep(1)
    default_cfg = weapon_configs[selected_weapon]
    cfg_string = f"CFG:{default_cfg['name']},{default_cfg['recoil_Y']},{default_cfg['recoil_X']}\n"
    arduino.write(cfg_string.encode())
    print(f"Sent to Arduino: {cfg_string.strip()}")

switch_tab("Recoil Control")
app.mainloop()

# == cleanup ==
if status_message == "initialized ard":
    arduino.close()
