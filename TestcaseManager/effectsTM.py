import tkinter as tk

class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

    def show_tip(self, tip_text, x, y):
        self.x, self.y = x, y
        if self.tip_window or not tip_text:
            return
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=tip_text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

def create_tooltip(tree):
    tooltip = ToolTip(tree)

    def on_motion(event):
        x, y = event.x, event.y
        item = tree.identify_row(y)
        # Check if the item is selected and the mouse is hovering over it
        if item and item in tree.selection():
            item_text = tree.item(item, 'values')[0]
            # Position the tooltip near the cursor
            tooltip.show_tip(item_text, event.x_root + 20, event.y_root + 20)
        else:
            tooltip.hide_tip()

    tree.bind('<Motion>', on_motion)
    tree.bind('<Leave>', lambda e: tooltip.hide_tip())




