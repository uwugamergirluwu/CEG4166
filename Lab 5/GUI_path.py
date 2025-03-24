from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import datetime

#Dimensions of grid maze
CELL_SIZE = 40 #size of each cell in pixels
GRID_WIDTH = 6
GRID_HEIGHT = 12

class GUI:
    def __init__(self, root):
        self.root=root
        self.root.title("Grid Maze")

        self.canvas = tk.Canvas(root, width=GRID_WIDTH*CELL_SIZE, height=GRID_HEIGHT*CELL_SIZE, bg='white')
        self.canvas.pack(padx=10, pady=10)

        self.maze = [
            [0, 0, 0, 0, 0, 2],
            [0, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [1, 1, 0, 1, 0, 0],
            [1, 1, 0, 1, 0, 0],
            [1, 1, 0, 1, 0, 0],
            [1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [3, 0, 0, 0, 0, 0]
        ]
        #starting position of the pointer (row, col)
        self.pointer_pos = [0, 5]
        self.direction = "down"
        self.obstacle_detected = False
        self.obstacle_list = []
        self.draw_maze()
        self.draw_pointer()
        self.root.bind("<Up>", self.move_forward)
        self.root.bind("<Down>", self.move_backward)
        self.root.bind("<Left>", self.turn_left)
        self.root.bind("<Right>", self.turn_right)

    def obstacle_detection(self):
        self.obstacle_detected = True
        timestamp = datetime.datetime.now()
        detected_object = (timestamp, self.pointer_pos, self.direction)
        print("Object Detected: ", detected_object)
        self.obstacle_list.append(detected_object)

    def save_file(self):
        file = filedialog.asksaveasfile(initialdir=r"C:\Users\jumbo\Desktop\ML_2025\Lab5", defaultextension='.txt',
                                 filetypes=[("Text file",".txt"), 
                                            ("HTML file", ".html"),
                                            ("All files", ".*")])
        if file is None:
            messagebox.showwarning(title='Notice', message = 'File was not saved.')
            return
        for obstacle in self.obstacle_list:
            obstacle_line = f"Obstacle detected - Timestamp: {obstacle[0]}, Position: {obstacle[1]}, Direction: {obstacle[2]}\n"
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


    def move_forward(self, event=None):
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
    
    def move_backward(self, event=None):
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

    def turn_right(self, event=None):
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

    def turn_left(self, event=None):
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

root=tk.Tk()
root.geometry("500x800")
root.title("Robot Path")
root.config(background="black")

title = Label(root, 
              text="Robot Path", font=('Arial', 20, 'bold'), fg='white', bg='black',
              relief = RAISED, bd=10,
              padx=10, pady=5)
title.place(x=160, y=0)
maze = GUI(root)
save_button = Button(root, text='save', command=maze.save_file, font=('Arial', 14), bg='green', fg='white')
save_button.pack(pady=10)
obstacle_button = Button(root, text='Obstacle', command=maze.obstacle_detection, font=('Arial', 14), bg='red', fg='white')
obstacle_button.pack(pady=10, padx=10)
root.mainloop()
