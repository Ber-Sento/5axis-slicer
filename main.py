import tkinter as tk
import os
import sys

from splash import SplashScreen
from app import App


# ===== RESOURCE PATH (PyInstaller SAFE) =====
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ===== START APP =====
def start_app():
    root = tk.Tk()

    # ===== ICON =====
    try:
        icon_path = resource_path("assets/icon.ico")
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"[Warning] Icon not loaded: {e}")

    App(root)
    root.mainloop()


# ===== ENTRY POINT =====
if __name__ == "__main__":

    # 1. SHOW SPLASH
    splash = SplashScreen(duration=2000)
    splash.show()

    # 2. START MAIN APP (ONLY ONCE)
    start_app()
