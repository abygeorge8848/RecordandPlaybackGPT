import tkinter as tk

class FadingMessage(tk.Toplevel):
    def __init__(self, parent, text, x, y):
        super().__init__(parent, bg='black', padx=5, pady=5)
        self.overrideredirect(True)  # Remove window decorations

        tk.Label(self, text=text, fg='white', bg='black').pack()
        self.wm_geometry(f"+{x}+{y}")  # Position near the cursor

        self.alpha = 1.0  # Initial opacity
        self.fade_away()

    def fade_away(self):
        self.alpha -= 0.04  # Decrease opacity
        self.wm_attributes("-alpha", self.alpha)  # Apply new opacity

        if self.alpha > 0:
            # Continue fading after 100ms
            self.after(40, self.fade_away)
        else:
            # Destroy the widget when fully transparent
            self.destroy()