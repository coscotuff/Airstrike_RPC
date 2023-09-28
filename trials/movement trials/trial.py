import tkinter as tk
import tkinter.simpledialog

N = 3

class movement_dialogue_box(tkinter.simpledialog.Dialog):
    def __init__(self, parent, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.N = N
        super().__init__(parent)

    def button_box(self):
        box = tk.Frame(self)
        movement_buttons = []
        for y in range(max(0, self.y - self.speed), min(self.N - 1, self.y + self.speed + 1)):
            row = []
            for x in range(max(0, self.x - self.speed), min(self.N - 1, self.x + self.speed + 1)):
                button = tk.Button(
                    box,
                    text=f"({x}, {y})",
                    # Get the chosen coordinate
                    command=lambda x=x, y=y: self.motion_button_click(x, y, box),
                )
                button.grid(row=y, column=x)
                row.append(button)
            movement_buttons.append(row)
        box.pack()

    def motion_button_click(self, x, y, box):
        self.x = x
        self.y = y

    def body(self, master):
        self.button_box()
        return None

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    dialogue = movement_dialogue_box(root, 1, 1, 1)
    print(dialogue.x, dialogue.y)
