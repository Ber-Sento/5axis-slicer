import tkinter as tk
import os
import sys


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class SplashScreen:
    def __init__(self, duration=2000):
        self.duration = duration

        self.root = tk.Tk()
        self.root.overrideredirect(True)

        # start fully transparent
        self.root.attributes("-alpha", 0.0)

        width = 420
        height = 420

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.configure(bg="#f5f5f5")

        # ===== LOGO =====
        logo_path = resource_path("assets/logo.png")

        if os.path.exists(logo_path):
            self.logo = tk.PhotoImage(file=logo_path)
            tk.Label(self.root, image=self.logo, bg="#f5f5f5").pack(pady=25)
        else:
            tk.Label(
                self.root,
                text="5AxisSlicer",
                font=("Arial", 18, "bold"),
                fg="white",
                bg="#1e1e1e"
            ).pack(pady=40)

        tk.Label(
            self.root,
            text="Loading slicer engine...",
            fg="#444444",
            bg="#f5f5f5",
            font=("Arial", 12)
        ).pack()

        self.fade_in()
        self.root.after(self.duration, self.close)
        self.root.configure(highlightbackground="#dddddd", highlightthickness=1)

    # ===== FADE IN ANIMATION =====
    def fade_in(self):
        alpha = self.root.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.05
            self.root.attributes("-alpha", alpha)
            self.root.after(30, self.fade_in)

    def close(self):
        self.root.destroy()

    def show(self):
        self.root.mainloop()
