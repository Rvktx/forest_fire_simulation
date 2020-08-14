# TODO DOCUMENTATION AND AUTOMODE

# Left click to next frame, right click to plot a graph

import tkinter as tk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

INITIAL_FOREST_DENSITY, INITIAL_FIRE_DENSITY = (0.55, 0.0004)
SPREAD_DIRECT_PROB, SPREAD_DIAGONAL_PROB = (0.92, 0.82)
NEW_FIRE_PROB, NEW_TREE_PROB = (0, 0)
TREE, FIRE, EMPTY = ('green', 'red', 'white')


class ForestFireWindow:
    def __init__(self, master, canvas_dimensions=(960, 960),
                 box_count=(120, 120)):
        self.canvas_width, self.canvas_height = canvas_dimensions
        self.box_count = box_count
        self.box_dimensions = (canvas_dimensions[0] // box_count[0],
                               canvas_dimensions[1] // box_count[1])
        self.current_frame = 1
        self.data = {
            'Frame': [0],
            'Trees': [0],
            'Burning': [0],
            'Burned': [0],
            'Empty': [0]
            }

        self.master = master
        self.frame = tk.Frame(self.master)
        self.canvas = tk.Canvas(self.master, width=self.canvas_width,
                                height=self.canvas_height)
        self.canvas.bind('<Button-1>', self.next_frame)
        self.canvas.bind('<Button-2>', self.plot_data)
        self.canvas.pack()
        self.frame.pack()

        self.grid = self.init_grid()
        self.data_update()

    def init_box(self, coords, color):
        """ Create rectangle on canvas. """
        x, y = coords
        width, height = self.box_dimensions
        x2 = x + width
        y2 = y + height

        box = self.canvas.create_rectangle(x, y, x2, y2, fill=color)
        return box

    def init_grid(self):
        """ Turn canvas into grid of boxes. """
        horizontal_count, vertical_count = self.box_count
        width, height = self.box_dimensions

        grid = [[None for _ in range(vertical_count)]
                for _ in range(horizontal_count)]

        for x in range(horizontal_count):
            for y in range(vertical_count):
                coords = (x * width, y * height)
                if np.random.rand() <= INITIAL_FOREST_DENSITY:
                    if np.random.rand() <= INITIAL_FIRE_DENSITY:
                        grid[x][y] = self.init_box(coords, FIRE)
                    else:
                        grid[x][y] = self.init_box(coords, TREE)
                else:
                    grid[x][y] = self.init_box(coords, EMPTY)
        return grid

    def get_status(self):
        """ Return state of the grid. """
        horizontal_count, vertical_count = self.box_count
        trees = burning = empty = 0

        for x in range(horizontal_count):
            for y in range(vertical_count):
                status = self.canvas.itemcget(self.grid[x][y], 'fill')

                if status == TREE:
                    trees += 1
                elif status == FIRE:
                    burning += 1
                else:
                    empty += 1
        return trees, burning, empty

    def data_update(self):
        """Update dataframe and print current state."""
        t, b, e = self.get_status()
        self.data['Frame'].append(self.current_frame)
        self.data['Trees'].append(t)
        self.data['Burning'].append(b)
        self.data['Burned'].append(self.data['Burned'][-1] + b)
        self.data['Empty'].append(e)

        print('{} trees, {} burning and {} empty '
              'in frame {}'.format(t, b, e, self.current_frame))

    def next_frame(self, _):
        """Generate next frame of the simulation."""
        self.current_frame += 1

        horizontal_count, vertical_count = self.box_count
        new_grid = [[None for _ in range(vertical_count)]
                    for _ in range(horizontal_count)]

        for x in range(horizontal_count):
            for y in range(vertical_count):
                current_box = self.grid[x][y]
                def status(box): return self.canvas.itemcget(box, 'fill')

                # This is kinda dumb. There has to be a better way of doing this.
                if status(current_box) == TREE:
                    if (x > 0 and y > 0
                            and status(self.grid[x - 1][y - 1]) == FIRE
                            and np.random.rand() <= SPREAD_DIAGONAL_PROB):
                        new_grid[x][y] = FIRE
                    elif (y > 0 and status(self.grid[x][y - 1]) == FIRE
                            and np.random.rand() <= SPREAD_DIRECT_PROB):
                        new_grid[x][y] = FIRE
                    elif (y > 0 and x < horizontal_count - 1
                            and status(self.grid[x + 1][y - 1]) == FIRE
                            and np.random.rand() <= SPREAD_DIAGONAL_PROB):
                        new_grid[x][y] = FIRE
                    elif (x > 0 and status(self.grid[x - 1][y]) == FIRE
                            and np.random.rand() <= SPREAD_DIRECT_PROB):
                        new_grid[x][y] = FIRE
                    elif (x < horizontal_count - 1
                            and status(self.grid[x + 1][y]) == FIRE
                            and np.random.rand() <= SPREAD_DIRECT_PROB):
                        new_grid[x][y] = FIRE
                    elif (x > 0 and y < vertical_count - 1
                            and status(self.grid[x - 1][y + 1]) == FIRE
                            and np.random.rand() <= SPREAD_DIAGONAL_PROB):
                        new_grid[x][y] = FIRE
                    elif (y < vertical_count - 1
                            and status(self.grid[x][y + 1]) == FIRE
                            and np.random.rand() <= SPREAD_DIRECT_PROB):
                        new_grid[x][y] = FIRE
                    elif (x < horizontal_count - 1 and y < vertical_count - 1
                            and status(self.grid[x + 1][y + 1]) == FIRE
                            and np.random.rand() <= SPREAD_DIAGONAL_PROB):
                        new_grid[x][y] = FIRE
                    elif np.random.rand() <= NEW_FIRE_PROB:
                        new_grid[x][y] = FIRE
                elif status(current_box) == FIRE:
                    new_grid[x][y] = EMPTY
                elif np.random.rand() <= NEW_TREE_PROB:
                    new_grid[x][y] = TREE

        for x in range(horizontal_count):
            for y in range(vertical_count):
                self.canvas.itemconfig(self.grid[x][y], fill=new_grid[x][y])

        self.data_update()

    def plot_data(self, _):
        """Make a plot of current data on right-click."""
        df = pd.DataFrame(self.data)

        ax = df.plot(kind='line', x='Frame', y='Trees', color='green')
        df.plot(kind='line', x='Frame', y='Burning', color='red', ax=ax)
        df.plot(kind='line', x='Frame', y='Burned', color='black', ax=ax)
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    forest = ForestFireWindow(root)
    root.mainloop()
