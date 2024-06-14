# Encoding: utf-8
import time
import win32api
import win32con
import win32gui
import win32process
import psutil
import tkinter as tk
from threading import Thread
from datetime import datetime

GAME_FILENAME = "Client-Win64-Shipping.exe"


def find_window_by_filename(filename):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(found_pid)
                if process.name() == filename:
                    hwnds.append(hwnd)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


def activate_window(hwnd):
    win32gui.SetForegroundWindow(hwnd)


def send_key(hwnd, key, delay):
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
    time.sleep(delay)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, key, 0)


# 按键映射
KEY_MAPPING = {
    'space': win32con.VK_SPACE,
    'insert': win32con.VK_INSERT,
    'esc': win32con.VK_ESCAPE,
    'end': win32con.VK_END,
    'f': ord('F')
}

actions_template = [
    ('space', 0.05),
    ('space', 0.5),
    ('insert', 0.05),  # 关tp
    ('insert', 0.5),
    ('insert', 0.05),  # 开tp
    ('insert', 0.5),
    ('esc', 0.05),
    ('esc', 0.5),
    ('end', 0.05),  # 开自动tp
    ('end', 0.5),
    ('space', 0.05),
    # ('space', 0.5),  # 无冠者 6次tp
    ('f', 0.05),
    ('f', 1.0),
    ('f', 0.05),
    ('f', 1.0),
    ('f', 0.05),
    ('f', 1.0),
    ('f', 0.05),
    ('f', 1.0),
    ('f', 0.05),
    ('f', 1.0),
    ('f', 0.05),
    ('f', 1.0),
    ('f', 0.05),
    ('f', 1.0),
    ('esc', 0.05),
    ('esc', 0.5),
    ('space', 0.05),
    # ('space', 0.5),  # 4次tp
    ('space', 0.05),
    ('space', 0.5)
]

running = False


def generate_actions(user_time):
    F_time = (user_time + 5) * 6
    esc_time = (user_time + 5) * 4
    actions = actions_template.copy()
    actions.insert(11, ('space', F_time))
    actions.insert(31, ('space', esc_time))
    return actions


def run_macro_by_filename(filename, loop_count, user_time):
    global running
    hwnds = find_window_by_filename(filename)
    if not hwnds:
        status_text.set(f"未找到文件名为 '{filename}' 的窗口")
        return

    hwnd = hwnds[0]
    activate_window(hwnd)
    time.sleep(1)

    actions = generate_actions(user_time)

    loop = 0
    start_time = datetime.now()
    while running:
        loop += 1
        if 0 < loop_count < loop:
            break
        update_status(loop, loop_count)
        for action, delay in actions:
            if not running:
                break
            key = KEY_MAPPING.get(action)
            if key is not None:
                send_key(hwnd, key, delay)

    end_time = datetime.now()
    elapsed_time = str(end_time - start_time).split('.')[0]
    status_text.set("循环终止")
    update_status(loop, loop_count, finished=True, elapsed_time=elapsed_time)


def start_macro():
    global running
    running = True
    loop_count = int(entry_loops.get())
    user_time = int(entry_time.get())
    thread = Thread(target=run_macro_by_filename, args=(GAME_FILENAME, loop_count, user_time))
    thread.start()


def stop_macro():
    global running
    hwnds = find_window_by_filename(GAME_FILENAME)
    if hwnds:
        hwnd = hwnds[0]
        activate_window(hwnd)
        send_key(hwnd, win32con.VK_END, 0.05)
    running = False


def update_status(current_loop, total_loops, finished=False, elapsed_time=None):
    if finished:
        status_text.set(f"循环完成，该起床了！总耗时: {elapsed_time}")
    else:
        status_text.set(f"当前循环次数: {current_loop} / {total_loops}")


root = tk.Tk()
root.title("4费躺平器")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

label_loops = tk.Label(frame, text="循环次数 (0为无限):")
label_loops.grid(row=0, column=0, padx=5, pady=5)

entry_loops = tk.Entry(frame)
entry_loops.grid(row=0, column=1, padx=5, pady=5)

label_time = tk.Label(frame, text="传送间隔:")
label_time.grid(row=1, column=0, padx=5, pady=5)

entry_time = tk.Entry(frame)
entry_time.grid(row=1, column=1, padx=5, pady=5)

button_start = tk.Button(frame, text="开始躺平", command=start_macro)
button_start.grid(row=2, column=0, padx=5, pady=5)

button_stop = tk.Button(frame, text="起床开肝", command=stop_macro)
button_stop.grid(row=2, column=1, padx=5, pady=5)

status_text = tk.StringVar()
status_label = tk.Label(frame, textvariable=status_text)
status_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()
