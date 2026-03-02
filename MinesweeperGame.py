import tkinter as tk
from tkinter import messagebox
import random
import time

class cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_mine = False
        self.revealed = False
        self.flagged = False
        self.adjacent_mines = 0

class Minesweeper:
    def __init__(self, master, rows=10, cols=10, mines=20):# Default values for rows, cols, and mines
        self.master = master
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.first_click = True
        self.board = [[cell(r, c) for c in range(cols)] for r in range(rows)] # Create a 2D list of cell objects
        self.buttons = [[None for _ in range(cols)] for _ in range(rows)]
        self.start_time = None
        self.elapsed_time = 0
        self.timer_running= False
        self.create_widgets()
        self.place_mines()
        self.calculate_adjacent_mines()

        self.master.title("Minesweeper")

        # top control frame
        top = tk.Frame(self.master)
        top.pack(padx=5 , pady= 5 ,anchor='nw')

        tk.Label(top, text= 'Rows:').grid(row=0, column=0)
        self.row_entry = tk.Entry(top, width=5)
        tk.Spinbox(top, from_=5, to=30, width=5, textvariable=tk.IntVar(value=self.rows)).grid(row=0, column=1)# Spinbox for rows

        tk.Label(top, text= 'Cols:').grid(row=0, column=2)
        self.col_entry = tk.Entry(top, width=5)
        tk.Spinbox(top, from_=5, to=30, width=5, textvariable=tk.IntVar(value=self.cols)).grid(row=0, column=3)# Spinbox for cols

        tk.Label(top, text= 'Mines:').grid(row=0, column=4)
        self.mines_var = tk.IntVar(value=self.mines)
        tk.Spinbox(top, from_=1, to=100, width=5, textvariable=self.mines_var).grid(row=0, column=5)# Spinbox for mines

        self.mines_label = tk.Label(top, text=f'Mines: {self.mines}')
        self.mines_label.grid(row=0, column=6, padx=10)
        
        self.timer_label = tk.Label(top, text='Time: 0s')
        self.timer_label.grid(row=0, column=7, padx=10)

        tk.Button(top, text='New Game', command=self.new_game).grid(row=0, column=8, padx=10)

        # Board frame
        self.board_frame = tk.Frame(self.master)
        self.board_frame.pack(padx=5, pady=5)

        self._create_board()

    def _update_size(self):
       try:
           r = int(self.row_entry.get())
           c = int(self.col_entry.get())
           m = int(self.mines_var.get())
       except ValueError:
           messagebox.showerror("Invalid Input", "Please enter valid numbers")

           return
       self.rows = max(5, min(30, r))
       self.cols = max(5, min(30, c))
       max_mines = self.rows * self.cols - 1
       m = max(1, min(max_mines, m))
       self.mines = m
       self.mines_label.config(text=f'Mines: {self.mines}')
       self.restart()

    def _create_board(self):
        self.cells = [[cell(r, c) for c in range(self.cols)] for r in range(self.rows)]
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.cols):
                b = tk.Button(self.board_frame, width=2, height=1, font=('TKDefaultFont', 12, 'bold'))
                b.grid(row=r, column=c)
                b.bind('<Button-1>', lambda e, row=r, col=c: self.on_left_click(row, col))# Bind left-click for revealing
                b.bind('<Button-3>', lambda e, row=r, col=c: self.on_right_click(row, col))# Bind right-click for flagging
                self.buttons[r][c] = b

        
        #resize the window to fit the new board
        self.master.update_idletasks()
        w = self.board_frame.winfo_width() + 20
        h = self.board_frame.winfo_height() + 80
        self.master.geometry(f"{w}x{h}")
    def place_mines(self, safe_row=None, safe_col=None):
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]

        safe = set()
        if safe_row is not None and safe_col is not None:
            for rr in range(safe_row-1, safe_row+2):
                for cc in range(safe_col-1, safe_col+2):
                    if 0 <= rr < self.rows and 0 <= cc < self.cols:
                        safe.add((rr, cc))
        choices = [p for p in positions if p not in safe]
        mines_to_place = min(self.mines, len(choices))
        mines = random.sample(choices, mines_to_place)
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c].is_mine = (r, c) in mines
                if 0 <= r < self.rows and 0 <= c < self.cols and self.cells[r][c].is_mine:
                    count = 0
                    for rr in range(r-1, r+2):
                        for cc in range(c-1, c+2):
                            if 0 <= rr < self.rows and 0 <= cc < self.cols:
                                self.cells[rr][cc].adjacent_mines += 1

    def on_left_click(self, row, col):
        if self.first_click:
            self.place_mines(safe_row=row, safe_col=col)
            self.first_click = False
            self.start_timer()
        cell = self.cells[row][col]
        if cell.flagged or cell.revealed:
            return
        cell.revealed = True
        if cell.is_mine:
            self.buttons[row][col].config(text='*', bg='red')
            self.game_over(False)
        else:
            self.buttons[row][col].config(text=str(cell.adjacent_mines) if cell.adjacent_mines > 0 else '', relief=tk.SUNKEN, bg='lightgrey')
            if cell.adjacent_mines == 0:
                for rr in range(row-1, row+2):
                    for cc in range(col-1, col+2):
                        if 0 <= rr < self.rows and 0 <= cc < self.cols and not self.cells[rr][cc].revealed:
                            self.on_left_click(rr, cc)
            if self.check_win():
                self.game_over(True)

    def on_right_click(self, row, col):
        cell = self.cells[row][col]
        if cell.revealed:
            return
        cell.flagged = not cell.flagged
        b = self.buttons[row][col]
        if cell.flagged:
            b.config(text='F', fg='red')
        else:
            b.config(text='', fg='black') 
                    
    def reveal_cell(self, row, col):
        cell = self.cells[row][col]
        b = self.buttons[row][col] 
        if cell.revealed or cell.flagged:
            return
        cell.revealed = True
        b.config(releif=tk.SUNKEN)
        if cell.adjacent > 0:
            b.config(text=str(cell.adjacent), disabledforeground=self._color_for_number(cell.adjacent))
        else:
            b.config(text='')
            b.config(state=tk.DISABLED)

        if cell.adjacent == 0:
        
        
         for rr in range(r-1, r+2):
              for cc in range(c-1, c+2):
                 if 0 <= rr < self.rows and 0 <= cc < self.cols:
                     if not self.cells[rr][cc].revealed:
                         self.reveal_cell(rr, cc)

    def reveal
