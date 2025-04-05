from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import datetime

#Dimensions of grid maze
CELL_SIZE = 18 #size of each cell in pixels
GRID_WIDTH = 7
GRID_HEIGHT = 8



class GUI:
    def __init__(self, root, display_distance):
        self.display_distance = display_distance
        self.root=root
        self.root.title("Grid Maze")

        self.canvas = tk.Canvas(root, width=GRID_WIDTH*CELL_SIZE, height=GRID_HEIGHT*CELL_SIZE, bg='white')
        self.canvas.pack(padx=10, pady=80)

        self.maze = [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 2, 1],
            [1, 0, 0, 0, 1, 0, 0],
            [1, 1, 1, 0, 1, 0, 0],
            [3, 0, 0, 0, 1, 0, 0],
            [1, 1, 1, 1, 1, 0, 0]
        ]
        #starting position of the pointer (row, col)
        self.pointer_pos = [3, 5]
        self.distance = 0.0
        self.direction = "up"
        self.end_reached = False
        self.obstacle_list = []
        self.draw_maze()
        self.draw_pointer()
        self.root.bind("<Up>", self.move_forward)
        self.root.bind("<Down>", self.move_backward)
        self.root.bind("<Left>", self.turn_left)
        self.root.bind("<Right>", self.turn_right)
        
    def set_end_reached(self):
        self.end_reached=True

    def obstacle_detection(self, distance_to_obstacle):
        timestamp = datetime.datetime.now()
        detected_object = (timestamp, self.pointer_pos, self.direction, distance_to_obstacle)
        print(f"Object Detected - Time: {detected_object[0]}, Position: {detected_object[1]}, Direction: {detected_object[2]}, Distance: {detected_object[3]}")
        self.obstacle_list.append(detected_object)

    def save_file(self):
        file = filedialog.asksaveasfile(defaultextension='.txt',
                                 filetypes=[("Text file",".txt"), 
                                            ("HTML file", ".html"),
                                            ("All files", ".*")])
        if file is None:
            messagebox.showwarning(title='Notice', message = 'File was not saved.')
            return
        for obstacle in self.obstacle_list:
            obstacle_line = f"Obstacle detected - Timestamp: {obstacle[0]}, Position: {obstacle[1]}, Direction: {obstacle[2]}, Distance to Obstacle: {obstacle[3]}\n"
            file.write(obstacle_line)
        file.close()

    def draw_maze(self):
        for row in range(GRID_HEIGHT):
            for col in range (GRID_WIDTH):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                if self.maze[row][col] == 3:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='red')
                elif self.maze[row][col] == 2:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='green')
                elif self.maze[row][col] == 1:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='gray')
                elif self.maze[row][col] == 0:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")

    def draw_pointer(self):
        self.canvas.delete("pointer")
        x = self.pointer_pos[1] * CELL_SIZE + CELL_SIZE//2
        y = self.pointer_pos[0] * CELL_SIZE + CELL_SIZE//2

        if self.direction == "up":
            self.canvas.create_line(x, y, x, y - CELL_SIZE // 4, width=3, arrow="last", tags="pointer")
        elif self.direction == "down":
            self.canvas.create_line(x, y, x, y + CELL_SIZE // 4,  width=3, arrow="last", tags="pointer")
        elif self.direction == "left":
            self.canvas.create_line(x , y, x - CELL_SIZE // 4, y,  width=3, arrow="last", tags="pointer")
        elif self.direction == "right":
            self.canvas.create_line(x, y, x + CELL_SIZE // 4, y,  width=3, arrow="last", tags="pointer")

    def update_label(self):
        self.distance = self.distance+0.355
        self.display_distance.set(f"Distance Travelled: {self.distance:.2f}m")
        self.root.update_idletasks()

    def move_forward(self):
        timestamp = datetime.datetime.now()
        row, col = self.pointer_pos
        new_row, new_col = row, col

        if self.direction =="up":
            new_row -=1
        elif self.direction == "down":
            new_row +=1
        elif self.direction == "left":
            new_col -= 1
        elif self.direction == "right":
            new_col +=1

        if 0 <= new_row < GRID_HEIGHT and 0 <= new_col < GRID_WIDTH and self.maze[new_row][new_col]!=1:
            #Record previous position
            prev_x = col * CELL_SIZE + CELL_SIZE // 2
            prev_y = row * CELL_SIZE + CELL_SIZE // 2

            #Update to new position
            self.pointer_pos = [new_row, new_col]
            
            #Draw line between previous and new positions
            new_x = new_col * CELL_SIZE + CELL_SIZE // 2
            new_y = new_row * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_line(prev_x, prev_y, new_x, new_y, width=2)

            self.draw_pointer()
            print(f"{timestamp} [Event] Moved forward")
            self.update_label()
            if self.pointer_pos == [6, 0]:
                set_end_reached()
    
    def move_backward(self):
        timestamp = datetime.datetime.now()
        row, col = self.pointer_pos
        new_row, new_col = row, col

        if self.direction == "up":
            new_row +=1
        elif self.direction == "down":
            new_row -=1
        elif self.direction == "left":
            new_col += 1
        elif self.direction == "right":
            new_col -=1
            
        if 0 <= new_row < GRID_HEIGHT and 0 <= new_col < GRID_WIDTH and self.maze[new_row][new_col]!=1:
            #Record previous position
            prev_x = col * CELL_SIZE + CELL_SIZE // 2
            prev_y = row * CELL_SIZE + CELL_SIZE // 2

            #Update to new position
            self.pointer_pos = [new_row, new_col]
            
            #Draw line between previous and new positions
            new_x = new_col * CELL_SIZE + CELL_SIZE // 2
            new_y = new_row * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_line(prev_x, prev_y, new_x, new_y, width=2)

            self.draw_pointer()
            print(f"{timestamp} [Event] Reversed")
            self.update_label()

    def turn_right(self):
        timestamp = datetime.datetime.now()
        current_direction = self.direction
        if current_direction == "up":
            self.direction = "right"
        elif current_direction =="down":
            self.direction = "left"
        elif current_direction =="left":
            self.direction = "up"
        elif current_direction =="right":
            self.direction = "down"
        
        self.draw_pointer()
        print(f"{timestamp} [Event] Turned right")

    def turn_left(self):
        timestamp = datetime.datetime.now()
        current_direction = self.direction
        if current_direction == "up":
            self.direction = "left"
        elif current_direction =="down":
            self.direction = "right"
        elif current_direction =="left":
            self.direction = "down"
        elif current_direction =="right":
            self.direction = "up"
        
        self.draw_pointer()
        print(f"{timestamp} [Event] Turned left")
