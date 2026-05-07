# THE FUNCTION WHICH SOLVES ALL THE SUDOKU PROBLEMS
# IN THE INPUT FILE USING BACKTRACKING AND WRITES THE OUTPUT TO THE OUTPUT FILE

import argparse
import os
import random
import sys
import time
import tkinter as tk
from tkinter import messagebox, ttk

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SOLVER_DIR = os.path.join(APP_DIR, "Lab45-Sudoku")
if not os.path.isdir(SOLVER_DIR):
    SOLVER_DIR = APP_DIR

if SOLVER_DIR not in sys.path:
    sys.path.insert(0, SOLVER_DIR)

from csp import csp
from search import Backtracking_Search, display, write


SCRIPT_DIR = SOLVER_DIR
DEFAULT_INPUT_FILE = os.path.join("data", "euler.txt")
FALLBACK_PUZZLES = [
    "003020600900305001001806400008102900700000008006708200002609500800203009005010300",
    "200080300060070084030500209000105408000000000402706000301007040720040060004010003",
    "000000907000420180000705026100904000050000040000507009920108000034059000507000000",
]

LEVEL_SETTINGS = {
    "Easy": {"givens": 46, "accent": "#2f9e44"},
    "Medium": {"givens": 38, "accent": "#1971c2"},
    "Hard": {"givens": 31, "accent": "#e67700"},
    "Expert": {"givens": 24, "accent": "#c92a2a"},
}


def resolve_input_path(input_file):
    if input_file is None:
        input_file = DEFAULT_INPUT_FILE

    if os.path.isabs(input_file):
        return input_file

    return os.path.join(SCRIPT_DIR, input_file)


def read_puzzle_file(input_file):
    filename = resolve_input_path(input_file)
    puzzles = []

    with open(filename, "r", encoding="utf-8") as ins:
        for line in ins:
            grid = line.strip()
            if len(grid) == 81 and all(char in "0123456789" for char in grid):
                puzzles.append(grid)

    return puzzles


def solve_grid(grid):
    sudoku = csp(grid=grid)
    solved = Backtracking_Search(sudoku)
    if solved == "FAILURE":
        return None

    solution = write(solved)
    if len(solution) == 81 and all(char in "123456789" for char in solution):
        return solution

    return None


def solve_file(input_file=None):
    """
    Original command-line behavior: solve every board in an input file and
    write the solved strings to output.txt.
    """
    filename = resolve_input_path(input_file)
    array = []
    with open(filename, "r", encoding="utf-8") as ins:
        for line in ins:
            array.append(line.strip())

    solved_count = 0
    boardno = 0
    start = time.time()
    output_path = os.path.join(SCRIPT_DIR, "output.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        for grid in array:
            startpuzle = time.time()
            boardno = boardno + 1
            sudoku = csp(grid=grid)
            solved = Backtracking_Search(sudoku)
            print("The board - ", boardno, " takes ", time.time() - startpuzle, " seconds")
            if solved != "FAILURE":
                print("After solving: ")
                display(solved)
                f.write(write(solved) + "\n")
                solved_count = solved_count + 1

    print("Number of problems solved is: ", solved_count)
    print("Time taken to solve the puzzles is: ", time.time() - start)


class PuzzleFactory:
    def __init__(self):
        self.puzzles = self._load_puzzles()
        self.solution_cache = self._load_solution_cache()

    def _load_puzzles(self):
        data_paths = [
            os.path.join("data", "euler.txt"),
            os.path.join("data", "magictour.txt"),
        ]

        for path in data_paths:
            full_path = resolve_input_path(path)
            if not os.path.exists(full_path):
                continue
            try:
                puzzles = read_puzzle_file(path)
            except OSError:
                continue
            if puzzles:
                return puzzles

        return FALLBACK_PUZZLES[:]

    def _load_solution_cache(self):
        output_path = os.path.join(SCRIPT_DIR, "output.txt")
        if not os.path.exists(output_path):
            return {}

        try:
            with open(output_path, "r", encoding="utf-8") as output:
                solutions = [line.strip() for line in output if line.strip()]
        except OSError:
            return {}

        cache = {}
        for puzzle, solution in zip(self.puzzles, solutions):
            valid_solution = len(solution) == 81 and all(char in "123456789" for char in solution)
            fits_puzzle = all(given == "0" or given == solution[index] for index, given in enumerate(puzzle))
            if valid_solution and fits_puzzle:
                cache[puzzle] = solution

        return cache

    def make_puzzle(self, level):
        level = level if level in LEVEL_SETTINGS else "Easy"
        givens = LEVEL_SETTINGS[level]["givens"]
        candidates = [grid for grid in self.puzzles if self._given_count(grid) <= givens]
        if not candidates:
            candidates = self.puzzles[:]
        random.shuffle(candidates)

        for base_grid in candidates:
            solution = self._solution_for(base_grid)
            if solution:
                return self._fill_to_level(base_grid, solution, givens), solution

        raise RuntimeError("Could not create a Sudoku puzzle from the available data.")

    def _solution_for(self, grid):
        if grid not in self.solution_cache:
            self.solution_cache[grid] = solve_grid(grid)
        return self.solution_cache[grid]

    def _fill_to_level(self, base_grid, solution, givens):
        visible = {index for index, value in enumerate(base_grid) if value != "0"}
        hidden = [index for index in range(81) if index not in visible]
        random.shuffle(hidden)

        for index in hidden:
            if len(visible) >= givens:
                break
            visible.add(index)

        return "".join(solution[index] if index in visible else "0" for index in range(81))

    def _given_count(self, grid):
        return sum(value != "0" for value in grid)


class SudokuLauncher:
    def __init__(self, root):
        self.root = root
        self.factory = PuzzleFactory()
        self.game = None
        self._configure_root()
        self._build()

    def _configure_root(self):
        self.root.title("Sudoku")
        self.root.geometry("680x460")
        self.root.minsize(620, 420)
        self.root.configure(bg="#eef2f7")

        try:
            style = ttk.Style()
            style.theme_use("clam")
        except tk.TclError:
            pass

    def _build(self):
        shell = tk.Frame(self.root, bg="#eef2f7")
        shell.pack(fill="both", expand=True, padx=42, pady=38)

        card = tk.Frame(
            shell,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#d7deea",
            highlightcolor="#d7deea",
        )
        card.pack(fill="both", expand=True)

        header = tk.Frame(card, bg="#1f2937", height=120)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Sudoku",
            bg="#1f2937",
            fg="#ffffff",
            font=("Segoe UI", 31, "bold"),
        ).pack(anchor="w", padx=34, pady=(24, 0))

        tk.Label(
            header,
            text="Backtracking solver with a playable puzzle board",
            bg="#1f2937",
            fg="#cbd5e1",
            font=("Segoe UI", 12),
        ).pack(anchor="w", padx=36, pady=(2, 0))

        body = tk.Frame(card, bg="#ffffff")
        body.pack(fill="both", expand=True, padx=34, pady=28)

        tk.Label(
            body,
            text="Choose Run to start the Sudoku game!",
            bg="#ffffff",
            fg="#334155",
            font=("Segoe UI", 14),
            wraplength=470,
            justify="left",
        ).pack(anchor="w")

        badges = tk.Frame(body, bg="#ffffff")
        badges.pack(anchor="w", pady=(24, 8))
        for text, color in [
            ("4 levels", "#e7f5ff"),
            ("Hints", "#fff4d6"),
            ("Live check", "#e6fcf5"),
        ]:
            tk.Label(
                badges,
                text=text,
                bg=color,
                fg="#1f2937",
                font=("Segoe UI", 10, "bold"),
                padx=14,
                pady=7,
            ).pack(side="left", padx=(0, 10))

        tk.Button(
            body,
            text="Run",
            command=self.open_game,
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 16, "bold"),
            padx=44,
            pady=12,
            cursor="hand2",
        ).pack(anchor="w", pady=(26, 0))

    def open_game(self):
        if self.game and self.game.exists():
            self.game.window.lift()
            self.game.window.focus_force()
            return

        self.game = SudokuGameWindow(self.root, self.factory)


class SudokuGameWindow:
    BOARD_BG = "#111827"
    PAGE_BG = "#f6f8fb"
    PANEL_BG = "#ffffff"
    GIVEN_BG = "#dbeafe"
    GIVEN_FG = "#111827"
    CELL_BG = "#ffffff"
    RELATED_BG = "#eef6ff"
    SELECTED_BG = "#dbeafe"
    HINT_BG = "#fff2b8"
    CHECKED_BG = "#dcfce7"
    ERROR_BG = "#fee2e2"
    ERROR_FG = "#b91c1c"
    SOLVED_FG = "#0f766e"

    def __init__(self, master, factory):
        self.master = master
        self.factory = factory
        self.window = tk.Toplevel(master)
        self.window.title("Sudoku Game")
        self.window.geometry("940x720")
        self.window.minsize(840, 660)
        self.window.configure(bg=self.PAGE_BG)

        self.level_var = tk.StringVar(value="Easy")
        self.status_var = tk.StringVar(value="")
        self.timer_var = tk.StringVar(value="00:00")
        self.empty_var = tk.StringVar(value="Empty: 0")
        self.hint_var = tk.StringVar(value="Hints: 0")

        self.cells = []
        self.vars = []
        self.fixed_cells = set()
        self.hint_cells = set()
        self.checked_cells = set()
        self.error_cells = set()
        self.selected = None
        self.solution = ""
        self.puzzle = ""
        self.hints_used = 0
        self.elapsed_seconds = 0
        self.timer_job = None
        self.loading = False
        self.completed = False

        self._build()
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.new_puzzle()
        self._tick()

    def exists(self):
        return bool(self.window.winfo_exists())

    def close(self):
        if self.timer_job:
            self.window.after_cancel(self.timer_job)
        self.window.destroy()

    def _build(self):
        header = tk.Frame(self.window, bg="#1f2937")
        header.pack(fill="x")

        title_area = tk.Frame(header, bg="#1f2937")
        title_area.pack(side="left", padx=26, pady=18)

        tk.Label(
            title_area,
            text="Sudoku Game",
            bg="#1f2937",
            fg="#ffffff",
            font=("Segoe UI", 23, "bold"),
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="Fill the board so every row, column, and box has 1-9.",
            bg="#1f2937",
            fg="#cbd5e1",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 0))

        controls = tk.Frame(header, bg="#1f2937")
        controls.pack(side="right", padx=26, pady=18)

        tk.Label(
            controls,
            text="Level",
            bg="#1f2937",
            fg="#cbd5e1",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(0, 8))

        self.level_box = ttk.Combobox(
            controls,
            textvariable=self.level_var,
            values=tuple(LEVEL_SETTINGS.keys()),
            state="readonly",
            width=11,
            font=("Segoe UI", 10),
        )
        self.level_box.pack(side="left", padx=(0, 12), ipady=4)
        self.level_box.bind("<<ComboboxSelected>>", lambda _event: self.new_puzzle())

        self._make_header_button(controls, "New Puzzle", self.new_puzzle).pack(side="left")

        content = tk.Frame(self.window, bg=self.PAGE_BG)
        content.pack(fill="both", expand=True, padx=26, pady=24)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=0)
        content.rowconfigure(0, weight=1)

        board_shell = tk.Frame(content, bg=self.BOARD_BG, padx=8, pady=8)
        board_shell.grid(row=0, column=0, sticky="nsew")
        for index in range(9):
            board_shell.columnconfigure(index, weight=1, uniform="board")
            board_shell.rowconfigure(index, weight=1, uniform="board")

        validate_command = (self.window.register(self._validate_entry), "%P")

        for row in range(9):
            cell_row = []
            var_row = []
            for col in range(9):
                value_var = tk.StringVar()
                value_var.trace_add(
                    "write",
                    lambda *_args, current_row=row, current_col=col: self._on_cell_change(
                        current_row,
                        current_col,
                    ),
                )
                entry = tk.Entry(
                    board_shell,
                    textvariable=value_var,
                    width=2,
                    justify="center",
                    font=("Segoe UI", 22, "bold"),
                    relief="flat",
                    bd=0,
                    bg=self.CELL_BG,
                    fg="#1f2937",
                    insertbackground="#2563eb",
                    validate="key",
                    validatecommand=validate_command,
                    readonlybackground=self.GIVEN_BG,
                    disabledforeground=self.GIVEN_FG,
                    highlightthickness=1,
                    highlightbackground="#d1d5db",
                    highlightcolor="#2563eb",
                )
                entry.bind(
                    "<FocusIn>",
                    lambda _event, current_row=row, current_col=col: self._select_cell(
                        current_row,
                        current_col,
                    ),
                )

                padx = (4 if col % 3 == 0 else 1, 4 if col == 8 or col % 3 == 2 else 1)
                pady = (4 if row % 3 == 0 else 1, 4 if row == 8 or row % 3 == 2 else 1)
                entry.grid(row=row, column=col, sticky="nsew", padx=padx, pady=pady)
                cell_row.append(entry)
                var_row.append(value_var)

            self.cells.append(cell_row)
            self.vars.append(var_row)

        panel = tk.Frame(
            content,
            bg=self.PANEL_BG,
            highlightthickness=1,
            highlightbackground="#d7deea",
            highlightcolor="#d7deea",
            width=245,
        )
        panel.grid(row=0, column=1, sticky="ns", padx=(22, 0))
        panel.grid_propagate(False)

        stats = tk.Frame(panel, bg=self.PANEL_BG)
        stats.pack(fill="x", padx=18, pady=(20, 12))

        self._stat_label(stats, "Time", self.timer_var).pack(fill="x", pady=(0, 10))
        self._stat_label(stats, "Progress", self.empty_var).pack(fill="x", pady=(0, 10))
        self._stat_label(stats, "Help", self.hint_var).pack(fill="x")

        button_area = tk.Frame(panel, bg=self.PANEL_BG)
        button_area.pack(fill="x", padx=18, pady=(16, 12))

        self._panel_button(button_area, "Hint", self.give_hint, "#f59e0b").pack(fill="x", pady=5)
        self._panel_button(button_area, "Check", self.check_board, "#0f766e").pack(fill="x", pady=5)
        self._panel_button(button_area, "Reset", self.reset_board, "#475569").pack(fill="x", pady=5)
        self._panel_button(button_area, "Solve", self.solve_board, "#b91c1c").pack(fill="x", pady=5)

        status_box = tk.Frame(panel, bg="#f8fafc", padx=12, pady=12)
        status_box.pack(fill="both", expand=True, padx=18, pady=(10, 18))

        tk.Label(
            status_box,
            textvariable=self.status_var,
            bg="#f8fafc",
            fg="#334155",
            font=("Segoe UI", 10),
            justify="left",
            anchor="nw",
            wraplength=185,
        ).pack(fill="both", expand=True)

    def _make_header_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="#ffffff",
            fg="#1f2937",
            activebackground="#e5e7eb",
            activeforeground="#111827",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=7,
            cursor="hand2",
        )

    def _panel_button(self, parent, text, command, color):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="#ffffff",
            activebackground=color,
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=10,
            cursor="hand2",
        )

    def _stat_label(self, parent, title, text_var):
        frame = tk.Frame(parent, bg="#f8fafc", padx=12, pady=10)
        tk.Label(
            frame,
            text=title.upper(),
            bg="#f8fafc",
            fg="#64748b",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            frame,
            textvariable=text_var,
            bg="#f8fafc",
            fg="#111827",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", pady=(2, 0))
        return frame

    def _validate_entry(self, proposed):
        return proposed == "" or (len(proposed) == 1 and proposed in "123456789")

    def new_puzzle(self):
        level = self.level_var.get()
        self.status_var.set("Preparing a new puzzle...")
        self.window.update_idletasks()

        try:
            puzzle, solution = self.factory.make_puzzle(level)
        except RuntimeError as error:
            messagebox.showerror("Sudoku", str(error), parent=self.window)
            return

        self.loading = True
        self.puzzle = puzzle
        self.solution = solution
        self.fixed_cells.clear()
        self.hint_cells.clear()
        self.checked_cells.clear()
        self.error_cells.clear()
        self.selected = None
        self.hints_used = 0
        self.elapsed_seconds = 0
        self.completed = False

        for row in range(9):
            for col in range(9):
                index = row * 9 + col
                entry = self.cells[row][col]
                value_var = self.vars[row][col]
                value = puzzle[index]

                entry.configure(state="normal")
                value_var.set("" if value == "0" else value)

                if value != "0":
                    self.fixed_cells.add((row, col))
                    entry.configure(state="readonly", cursor="arrow")
                else:
                    entry.configure(state="normal", cursor="xterm")

        self.loading = False
        accent = LEVEL_SETTINGS.get(level, LEVEL_SETTINGS["Easy"])["accent"]
        self.status_var.set(f"{level} puzzle ready.")
        self.level_box.configure(foreground=accent)
        self._sync_metrics()
        self._paint_all()

    def reset_board(self):
        if self.completed:
            return

        self.loading = True
        for row in range(9):
            for col in range(9):
                if (row, col) not in self.fixed_cells:
                    self.vars[row][col].set("")
        self.loading = False

        self.hint_cells.clear()
        self.checked_cells.clear()
        self.error_cells.clear()
        self.selected = None
        self.hints_used = 0
        self.elapsed_seconds = 0
        self.status_var.set("Board reset.")
        self._sync_metrics()
        self._paint_all()

    def give_hint(self):
        if self.completed:
            return

        target = self._hint_target()
        if target is None:
            self.status_var.set("No hint needed. The board is complete.")
            return

        row, col = target
        index = row * 9 + col
        correct_value = self.solution[index]
        self.vars[row][col].set(correct_value)
        self.hint_cells.add((row, col))
        self.error_cells.discard((row, col))
        self.hints_used += 1
        self.status_var.set(f"Hint placed at row {row + 1}, column {col + 1}.")
        self._sync_metrics()
        self._paint_all()
        self._maybe_finish()

    def _hint_target(self):
        if self.selected and self.selected not in self.fixed_cells:
            row, col = self.selected
            if self.vars[row][col].get() != self.solution[row * 9 + col]:
                return self.selected

        empty_cells = []
        wrong_cells = []
        for row in range(9):
            for col in range(9):
                if (row, col) in self.fixed_cells:
                    continue

                value = self.vars[row][col].get()
                correct = self.solution[row * 9 + col]
                if value == "":
                    empty_cells.append((row, col))
                elif value != correct:
                    wrong_cells.append((row, col))

        if empty_cells:
            return random.choice(empty_cells)
        if wrong_cells:
            return random.choice(wrong_cells)
        return None

    def check_board(self):
        if self.completed:
            messagebox.showinfo("Check", "This puzzle is already complete.", parent=self.window)
            return

        self.error_cells.clear()
        self.checked_cells.clear()
        empty = 0
        user_entries = 0
        for row in range(9):
            for col in range(9):
                value = self.vars[row][col].get()
                if value == "":
                    empty += 1
                    continue

                if (row, col) not in self.fixed_cells:
                    user_entries += 1

                if value != self.solution[row * 9 + col]:
                    self.error_cells.add((row, col))
                elif (row, col) not in self.fixed_cells:
                    self.checked_cells.add((row, col))

        if self.error_cells:
            message = f"{len(self.error_cells)} incorrect cell(s) found."
            self.status_var.set(message)
        elif empty:
            if user_entries:
                message = f"No mistakes found. {empty} cell(s) left."
            else:
                message = "No entries to check yet. Fill a cell first or use Hint."
            self.status_var.set(message)
        else:
            self.status_var.set("Puzzle solved.")
            self._finish_game(show_message=True)
            self._sync_metrics()
            self._paint_all()
            return

        self._sync_metrics()
        self._paint_all()
        self.window.update_idletasks()

        if self.error_cells:
            messagebox.showwarning("Check", message, parent=self.window)
        else:
            messagebox.showinfo("Check", message, parent=self.window)

    def solve_board(self):
        if self.completed:
            return

        if not messagebox.askyesno(
            "Solve puzzle",
            "Reveal the full solution?",
            parent=self.window,
        ):
            return

        self.loading = True
        for row in range(9):
            for col in range(9):
                if (row, col) not in self.fixed_cells:
                    self.vars[row][col].set(self.solution[row * 9 + col])
        self.loading = False

        self.error_cells.clear()
        self.hint_cells.clear()
        self.checked_cells.clear()
        self.status_var.set("Solution revealed.")
        self._finish_game(show_message=False)
        self._sync_metrics()
        self._paint_all()

    def _select_cell(self, row, col):
        self.selected = (row, col)
        self._paint_all()

    def _on_cell_change(self, row, col):
        if self.loading:
            return

        self.error_cells.discard((row, col))
        self.checked_cells.discard((row, col))
        if self.vars[row][col].get() != self.solution[row * 9 + col]:
            self.hint_cells.discard((row, col))
        self.status_var.set("Keep going.")
        self._sync_metrics()
        self._paint_all()
        self._maybe_finish()

    def _sync_metrics(self):
        empty = 0
        for row in range(9):
            for col in range(9):
                if self.vars[row][col].get() == "":
                    empty += 1

        self.empty_var.set(f"Empty: {empty}")
        self.hint_var.set(f"Hints: {self.hints_used}")

    def _tick(self):
        if not self.completed:
            minutes, seconds = divmod(self.elapsed_seconds, 60)
            self.timer_var.set(f"{minutes:02d}:{seconds:02d}")
            self.elapsed_seconds += 1
        self.timer_job = self.window.after(1000, self._tick)

    def _maybe_finish(self):
        if self.completed:
            return

        for row in range(9):
            for col in range(9):
                if self.vars[row][col].get() != self.solution[row * 9 + col]:
                    return

        self._finish_game(show_message=True)

    def _finish_game(self, show_message):
        self.completed = True
        minutes, seconds = divmod(max(0, self.elapsed_seconds - 1), 60)
        self.status_var.set(
            f"Solved in {minutes:02d}:{seconds:02d} with {self.hints_used} hint(s)."
        )
        if show_message:
            messagebox.showinfo("Sudoku", "Puzzle solved.", parent=self.window)

    def _paint_all(self):
        for row in range(9):
            for col in range(9):
                self._paint_cell(row, col)

    def _paint_cell(self, row, col):
        entry = self.cells[row][col]
        value = self.vars[row][col].get()
        position = (row, col)
        fg = "#1f2937"
        bg = self.CELL_BG

        if position in self.fixed_cells:
            bg = self.GIVEN_BG
            fg = self.GIVEN_FG
        elif position in self.error_cells:
            bg = self.ERROR_BG
            fg = self.ERROR_FG
        elif position in self.hint_cells:
            bg = self.HINT_BG
            fg = "#854d0e"
        elif position in self.checked_cells:
            bg = self.CHECKED_BG
            fg = self.SOLVED_FG
        elif self.selected == position:
            bg = self.SELECTED_BG
        elif self.selected and self._is_related(position, self.selected):
            bg = self.RELATED_BG

        if position not in self.fixed_cells and value:
            if value == self.solution[row * 9 + col]:
                fg = self.SOLVED_FG

        entry.configure(
            bg=bg,
            fg=fg,
            readonlybackground=bg,
            highlightbackground="#2563eb" if self.selected == position else "#d1d5db",
            highlightthickness=2 if self.selected == position else 1,
        )

    def _is_related(self, position, selected):
        row, col = position
        selected_row, selected_col = selected
        same_row = row == selected_row
        same_col = col == selected_col
        same_box = row // 3 == selected_row // 3 and col // 3 == selected_col // 3
        return same_row or same_col or same_box


def launch_gui():
    root = tk.Tk()
    SudokuLauncher(root)
    root.mainloop()


# THE MAIN FUNCTION GOES HERE
if __name__ == "__main__":
    """
    GUI:
    python sudoku.py

    Command-line solver:
    python sudoku.py --cli --inputFile data/euler.txt
    """
    argument_parser = argparse.ArgumentParser(description="Sudoku Solving Problem")
    argument_parser.add_argument("--inputFile", type=str, default=None, help="Sudoku Input File")
    argument_parser.add_argument(
        "--cli",
        action="store_true",
        help="Run the original command-line batch solver instead of the GUI",
    )
    args = argument_parser.parse_args()

    if args.cli or args.inputFile:
        solve_file(args.inputFile)
    else:
        launch_gui()
