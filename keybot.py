
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

import keyboard
import pyautogui
import pyperclip


root = tk.Tk()
root.title("KeyBot - Keyboard Typing Assistant")
root.geometry("650x500")
root.minsize(500, 400)

root.configure(bg="#0B1120")

running = False
paused = threading.Event()
paused.set()
stop_event = threading.Event()

status = tk.StringVar(value="Ready")
speed = tk.DoubleVar(value=0.08)


def update_status(message):
    root.after(0, lambda: status.set(message))


def toggle_pause():
    if not running:
        return

    if paused.is_set():
        paused.clear()
        update_status("Paused — press F8 to resume")
    else:
        paused.set()
        update_status("Typing resumed")


def stop_typing():
    stop_event.set()
    paused.set()
    update_status("Stopping...")


def start_typing():
    global running

    if running:
        return

    text = text_area.get("1.0", "end-1c")
    delay = speed.get()

    if not text:
        messagebox.showwarning("KeyBot", "Enter some text first.")
        return

    running = True
    stop_event.clear()
    paused.set()
    start_button.config(state="disabled")
    status.set("Switch to your target app in 3 seconds...")

    threading.Thread(
        target=type_text,
        args=(text, delay),
        daemon=True
    ).start()


def type_text(text, delay):
    global running

    try:
        for remaining in range(3, 0, -1):
            if stop_event.is_set():
                return
            update_status(
                f"Switch to your target app... {remaining}"
            )
            if stop_event.wait(1):
                return

        for character in text:
            if stop_event.is_set():
                break

            while not paused.wait(0.1):
                if stop_event.is_set():
                    break

            if stop_event.is_set():
                break

            pyperclip.copy(character)
            pyautogui.hotkey("ctrl", "v")

            if stop_event.wait(delay):
                break

        if stop_event.is_set():
            update_status("Typing stopped")
        else:
            update_status("Typing completed")

    except Exception as error:
        update_status(f"Error: {error}")

    finally:
        running = False
        root.after(0, lambda: start_button.config(state="normal"))


def close_app():
    stop_event.set()
    paused.set()
    keyboard.unhook_all()
    root.destroy()


title = tk.Label(
    root,
    text="KEYBOT",
    font=("Consolas", 24, "bold"),
    fg="#38BDF8",
    bg="#0B1120"
)
title.pack(pady=(18, 4))

subtitle = tk.Label(
    root,
    text="Human-like keyboard typing assistant",
    font=("Consolas", 10),
    fg="#94A3B8",
    bg="#0B1120"
)
subtitle.pack(pady=(0, 12))

text_area = tk.Text(
    root,
    height=12,
    wrap="word",
    font=("Consolas", 11),
    bg="#111827",
    fg="#E2E8F0",
    insertbackground="#38BDF8",
    relief="flat",
    padx=12,
    pady=12
)
text_area.pack(fill="both", expand=True, padx=20, pady=5)

controls = tk.Frame(root, bg="#0B1120")
controls.pack(fill="x", padx=20, pady=10)

tk.Label(
    controls,
    text="Delay per character (seconds):",
    fg="#CBD5E1",
    bg="#0B1120",
    font=("Consolas", 9)
).pack(anchor="w")

speed_scale = ttk.Scale(
    controls,
    from_=0.01,
    to=0.30,
    variable=speed,
    orient="horizontal"
)
speed_scale.pack(fill="x", pady=6)

start_button = tk.Button(
    controls,
    text="START TYPING",
    command=start_typing,
    bg="#0284C7",
    fg="white",
    activebackground="#0369A1",
    relief="flat",
    font=("Consolas", 11, "bold"),
    pady=9
)
start_button.pack(fill="x", pady=5)

status_label = tk.Label(
    root,
    textvariable=status,
    font=("Consolas", 10),
    fg="#38BDF8",
    bg="#0B1120"
)
status_label.pack(pady=5)

hotkeys_label = tk.Label(
    root,
    text="F8: Pause / Resume     F9: Stop",
    font=("Consolas", 10),
    fg="#94A3B8",
    bg="#0B1120"
)
hotkeys_label.pack(pady=(0, 15))

keyboard.add_hotkey("F8", toggle_pause)
keyboard.add_hotkey("F9", stop_typing)

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
