# text_watcher.py
import platform
import subprocess
import threading
import time
import pyperclip
import tkinter as tk
from tkinter import ttk

class TextSelectionWatcher:
    def __init__(self, parent_app):
        self.parent = parent_app
        self.popup = None
        self.running = True
        self.current_selection = ""
        self.system = platform.system()
        self.setup_watcher()

    def setup_watcher(self):
        if self.system == "Windows":
            threading.Thread(target=self.windows_watcher, daemon=True).start()
        elif self.system == "Darwin":
            threading.Thread(target=self.macos_watcher, daemon=True).start()
        else:
            threading.Thread(target=self.linux_watcher, daemon=True).start()

    def windows_watcher(self):
        import ctypes
        user32 = ctypes.windll.user32

        last_selection = ""
        while self.running:
            try:
                if user32.GetAsyncKeyState(0x01) & 0x8000:
                    time.sleep(0.1)
                    current = self.get_windows_selection()
                    if current and current != last_selection:
                        last_selection = current
                        self.current_selection = current
                        self.parent.root.after(0, self.show_popup)
            except:
                pass
            time.sleep(0.1)

    def get_windows_selection(self):
        import ctypes
        user32 = ctypes.windll.user32
        CF_TEXT = 1

        backup = pyperclip.paste()

        user32.keybd_event(0x11, 0, 0, 0)
        user32.keybd_event(0x43, 0, 0, 0)
        user32.keybd_event(0x43, 0, 0x0002, 0)
        user32.keybd_event(0x11, 0, 0x0002, 0)

        time.sleep(0.1)
        text = pyperclip.paste()

        pyperclip.copy(backup)
        return text.strip()

    def macos_watcher(self):
        while self.running:
            try:
                script = 'tell application "System Events" to get the value of (attribute "AXSelectedText" of first process whose frontmost is true)'
                current = subprocess.run(['osascript', '-e', script],
                                       capture_output=True, text=True).stdout.strip()
                if current and current != self.current_selection:
                    self.current_selection = current
                    self.parent.root.after(0, self.show_popup)
            except:
                pass
            time.sleep(0.5)

    def linux_watcher(self):
        while self.running:
            try:
                current = subprocess.run(['xclip', '-o', '-selection', 'primary'],
                                       capture_output=True, text=True).stdout.strip()
                if current and current != self.current_selection:
                    self.current_selection = current
                    self.parent.root.after(0, self.show_popup)
            except:
                pass
            time.sleep(0.5)

    def show_popup(self):
        if self.popup:
            self.popup.destroy()

        self.popup = tk.Toplevel(self.parent.root)
        self.popup.overrideredirect(True)
        self.popup.attributes('-topmost', True)

        x, y = self.get_mouse_position()
        self.popup.geometry(f"+{x+15}+{y+15}")

        frame = ttk.Frame(self.popup, padding=3)
        frame.pack()

        ttk.Button(
            frame,
            text="添加到日程",
            command=self.add_to_schedule,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            frame,
            text="×",
            command=self.popup.destroy,
            width=2
        ).pack(side=tk.LEFT)

        self.popup.bind("<FocusOut>", lambda e: self.popup.destroy())
        self.adjust_popup_position()

    def get_mouse_position(self):
        if self.system == "Windows":
            import ctypes
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            pt = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return (pt.x, pt.y)
        elif self.system == "Darwin":
            script = 'tell application "System Events" to {set theMouse to mouse position}'
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True).stdout
            x, y = map(int, result.strip().split(', '))
            return (x, y)
        else:
            try:
                output = subprocess.check_output(['xdotool', 'getmouselocation']).decode()
                parts = output.split()
                x = int(parts[0].split(':')[1])
                y = int(parts[1].split(':')[1])
                return (x, y)
            except:
                return (100, 100)

    def adjust_popup_position(self):
        if not self.popup:
            return

        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()

        x, y = self.get_mouse_position()
        x += 15
        y += 15

        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()

        if x + popup_width > screen_width:
            x = screen_width - popup_width - 5
        if y + popup_height > screen_height:
            y = screen_height - popup_height - 5

        self.popup.geometry(f"+{x}+{y}")

    def add_to_schedule(self):
        if self.current_selection:
            self.parent.text_input.delete(1.0, tk.END)
            self.parent.text_input.insert(tk.END, self.current_selection)
            self.parent.analyze_text()
        if self.popup:
            self.popup.destroy()
