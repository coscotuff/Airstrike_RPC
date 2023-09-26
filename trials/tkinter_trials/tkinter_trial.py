import tkinter as tk
from tkinter import colorchooser
import random

# Constants
GRID_SIZE = 10
GRID_CELL_SIZE = 40  # Adjust this for cell size
DEFAULT_COLOR = "white"
MAX_LIVES = 5
MAX_TURNS = 10


# Function to change the color of a cell
def change_color(x, y, color):
    canvas.itemconfig(grid[y][x], fill=color)


# Function to update the information at the bottom of the grid
def update_info():
    info_label.config(
        text=f"Current Coordinates: ({current_x}, {current_y}) | Lives Left: {lives_left} | Turns Left: {turns_left}"
    )


# Function to handle color change button click
def change_color_button_click():
    color = colorchooser.askcolor(title="Choose Color")[1]
    change_color(current_x, current_y, color)
    update_info()


# Function to display a red region on the grid based on center and radius
def display_red_region(center_x, center_y, radius):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if abs(x - center_x) < radius and abs(y - center_y) < radius:
                change_color(x, y, "red")


# Function for live updates
def live_update():
    # Example: Update the red region based on new center and radius
    center_x, center_y, radius = random.randint(0, 9), random.randint(0, 9), random.randint(1, 4)
    clear_grid()
    display_red_region(center_x, center_y, radius)
    canvas.update()  # Force an immediate update of the canvas
    update_info()
    root.after(
        1000, live_update
    )  # Schedule the next update after 1000 milliseconds (1 second)


# Function to clear the grid
def clear_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            change_color(x, y, DEFAULT_COLOR)


# Create the main window
root = tk.Tk()
root.title("Grid with Variable Colors")

# Create a canvas to draw the grid
canvas = tk.Canvas(
    root, width=GRID_SIZE * GRID_CELL_SIZE, height=GRID_SIZE * GRID_CELL_SIZE
)
canvas.pack()

# Create a 2D list to store the grid items
grid = []

# Initialize the grid
for y in range(GRID_SIZE):
    row = []
    for x in range(GRID_SIZE):
        cell = canvas.create_rectangle(
            x * GRID_CELL_SIZE,
            y * GRID_CELL_SIZE,
            (x + 1) * GRID_CELL_SIZE,
            (y + 1) * GRID_CELL_SIZE,
            fill=DEFAULT_COLOR,
            outline="black",
        )
        row.append(cell)
    grid.append(row)

# Initialize game variables
current_x, current_y = 0, 0
lives_left = MAX_LIVES
turns_left = MAX_TURNS

# Create a label for displaying information
info_label = tk.Label(root, text="")
info_label.pack()

# Start live updates
live_update()

root.mainloop()
