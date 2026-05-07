# Lab 45 Sudoku Solver

This project is a Python Sudoku solver and playable Sudoku GUI. It was built for an Artificial Intelligence lab to demonstrate how Sudoku can be represented as a Constraint Satisfaction Problem (CSP) and solved with search techniques.

The project has two main ways to use it:

- A graphical Sudoku game in `sudoku_gui.py`.
- A command-line batch solver in `Lab45-Sudoku/sudoku.py` or through `sudoku_gui.py --cli`.

The solver reads Sudoku boards as 81-character strings, where digits `1` to `9` are fixed clues and `0` means an empty cell. It then solves each puzzle and writes solved boards to `Lab45-Sudoku/output.txt`.

## Project Structure

```text
Lab45/
+-- README.md
+-- sudoku_gui.py
+-- Lab45-Sudoku/
    +-- csp.py
    +-- search.py
    +-- sudoku.py
    +-- util.py
    +-- output.txt
    +-- data/
        +-- euler.txt
        +-- magictour.txt
```

## File Descriptions

`sudoku_gui.py`

Runs the Tkinter graphical interface. The GUI can generate playable puzzles from the available data files, let the user select difficulty levels, check entries, request hints, reveal the solution, and track elapsed time. It also supports command-line solving with the `--cli` option.

`Lab45-Sudoku/sudoku.py`

Original command-line entry point. It reads puzzles from an input file, solves them one by one, prints solving time for each board, displays solved boards in the terminal, and writes the solved strings to `output.txt`.

`Lab45-Sudoku/csp.py`

Defines the Sudoku CSP representation. Each board has 81 variables named by row and column, such as `A1`, `A2`, ..., `I9`. Each variable has a domain of possible digits. Filled cells have a single-value domain, while empty cells begin with the domain `123456789`.

`Lab45-Sudoku/search.py`

Contains the search and constraint propagation logic, including backtracking search, recursive backtracking, forward checking, the Minimum Remaining Values heuristic, consistency checking, display helpers, and an AC-3 implementation.

`Lab45-Sudoku/util.py`

Stores shared constants and helper functions, including row labels, column labels, digit labels, and the `cross()` function used to build Sudoku square names.

`Lab45-Sudoku/data/euler.txt` and `Lab45-Sudoku/data/magictour.txt`

Input puzzle collections. Each line is one Sudoku puzzle in 81-character format.

## Sudoku as a CSP

Sudoku is a good example of a Constraint Satisfaction Problem because the task is to assign values to variables while respecting constraints.

In this project:

- Variables: the 81 cells of the Sudoku grid.
- Domains: possible values for each cell, usually digits `1` through `9`.
- Constraints: cells in the same row, column, or 3x3 box must contain different digits.

For example, cell `A1` is constrained by:

- Every other cell in row `A`.
- Every other cell in column `1`.
- Every other cell in the top-left 3x3 box.

The code builds these relationships in `csp.py`:

- `unitlist` stores all 27 units: 9 rows, 9 columns, and 9 boxes.
- `units` maps each cell to the row, column, and box it belongs to.
- `peers` maps each cell to all other cells that directly constrain it.

## Algorithms Used

### Backtracking Search

The main solving method is backtracking search. Backtracking tries to assign a digit to an empty cell, checks whether the assignment is valid, and then recursively continues with the next cell. If a contradiction appears, it undoes the last assignment and tries another value.

The solving flow is:

1. Start with an empty assignment.
2. Choose an unassigned cell.
3. Try a possible digit for that cell.
4. Check whether the digit conflicts with assigned peer cells.
5. Apply inference to reduce neighboring domains.
6. Continue recursively until all 81 cells are assigned.
7. If a branch fails, restore the previous state and try another digit.

### Minimum Remaining Values (MRV)

The function `Select_Unassigned_Variables()` uses the Minimum Remaining Values heuristic. Instead of choosing the next empty cell randomly or from left to right, it chooses the unassigned cell with the smallest current domain.

This is useful because cells with fewer legal choices are more likely to expose contradictions early. That reduces wasted search.

### Forward Checking

The function `Inference()` performs forward checking. After assigning a value to one cell, the solver removes that value from the domains of all unassigned peer cells.

For example, if `A1 = 5`, then no other cell in row `A`, column `1`, or the top-left box can be `5`. If removing `5` leaves any peer with an empty domain, the solver knows that branch cannot lead to a solution.

### AC-3

The file `search.py` also includes an `AC3()` implementation. AC-3 stands for Arc Consistency Algorithm 3. It repeatedly checks arcs between neighboring variables and removes values that cannot satisfy the all-different constraint.

In this codebase, the main command-line solver uses `Backtracking_Search()`. AC-3 is available as an additional constraint propagation algorithm and can be used to reduce domains before or during search.

## Exercise 1: CSP Sudoku Solver

Exercise 1 focuses on the Artificial Intelligence part of the project: representing Sudoku as a CSP and solving it by search.

The most important files for this exercise are:

- `Lab45-Sudoku/csp.py`
- `Lab45-Sudoku/search.py`
- `Lab45-Sudoku/sudoku.py`
- `Lab45-Sudoku/util.py`

### Building the Sudoku Variables

In `util.py`, the project defines the row names, column names, and square names:

```python
digits = cols = "123456789"
rows = "ABCDEFGHI"

def cross(A, B):
    return [a + b for a in A for b in B]

squares = cross(rows, cols)
```

This creates cell names such as `A1`, `A2`, `A3`, ..., `I9`. These 81 names become the variables of the CSP.

### Creating the CSP Model

In `csp.py`, the constructor creates the row, column, and box units:

```python
self.unitlist = (
    [cross(r, cols) for r in rows] +
    [cross(rows, c) for c in cols] +
    [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
)
```

This produces:

- 9 row units.
- 9 column units.
- 9 box units.

Then the code builds `units` and `peers`:

```python
self.units = dict((s, [u for u in self.unitlist if s in u]) for s in self.variables)
self.peers = dict((s, set(sum(self.units[s], [])) - set([s])) for s in self.variables)
```

For every square, `units` tells which row, column, and box it belongs to. `peers` tells which other cells cannot have the same value.

### Reading a Puzzle

The function `getDict()` converts an 81-character puzzle string into a dictionary:

```python
if grid[i] != '0':
    values[cell] = grid[i]
else:
    values[cell] = digits
```

If the input character is a digit from `1` to `9`, the cell is already fixed. If it is `0`, the cell is empty, so its domain is all possible digits: `123456789`.

### Running Backtracking

The solver starts from `Backtracking_Search()` in `search.py`:

```python
def Backtracking_Search(csp):
    assignment = {}
    return Recursive_Backtracking(assignment, csp)
```

The recursive function then chooses a variable, tries values, checks consistency, applies inference, and backtracks if needed:

```python
for value in Order_Domain_Values(var, assignment, csp):
    if isConsistent(var, value, assignment, csp):
        old_values = deepcopy(csp.values)
        assignment[var] = value
        csp.values[var] = value
        inference_result = Inference(assignment, inferences, csp, var, value)
```

The `old_values` copy is important because it lets the solver restore the previous board state when a choice fails.

### Selecting the Next Cell with MRV

The MRV heuristic is implemented in `Select_Unassigned_Variables()`:

```python
unassigned_variables = dict((s, len(csp.values[s])) for s in csp.values if s not in assignment.keys())
mrv = min(unassigned_variables, key=unassigned_variables.get)
return mrv
```

This chooses the cell with the fewest remaining possible values. It usually makes the solver faster because difficult cells are handled earlier.

### Forward Checking

Forward checking is implemented in `Inference()`:

```python
for neighbor in csp.peers[var]:
    if neighbor not in assignment and value in csp.values[neighbor]:
        if len(csp.values[neighbor]) == 1:
            return "FAILURE"

        remaining = csp.values[neighbor] = csp.values[neighbor].replace(value, "")
```

After assigning a value, the same value is removed from all peer domains. If a peer has no possible value left, the branch fails immediately.

## Exercise 2: GUI Sudoku Application

Exercise 2 extends the solver into a playable application using Tkinter. The main file is `sudoku_gui.py`.

The GUI is not a separate solver. It imports and reuses the same CSP solver:

```python
from csp import csp
from search import Backtracking_Search, display, write
```

### Solving One Grid for the GUI

The function `solve_grid()` receives one 81-character puzzle string, solves it, and returns the solved string:

```python
def solve_grid(grid):
    sudoku = csp(grid=grid)
    solved = Backtracking_Search(sudoku)
    if solved == "FAILURE":
        return None

    solution = write(solved)
    if len(solution) == 81 and all(char in "123456789" for char in solution):
        return solution

    return None
```

This function is useful for the GUI because the interface needs a completed solution in order to check user moves, give hints, and reveal the answer.

### Puzzle Generation by Difficulty

The GUI uses a `PuzzleFactory` class to load puzzle data and create playable boards:

```python
LEVEL_SETTINGS = {
    "Easy": {"givens": 46, "accent": "#2f9e44"},
    "Medium": {"givens": 38, "accent": "#1971c2"},
    "Hard": {"givens": 31, "accent": "#e67700"},
    "Expert": {"givens": 24, "accent": "#c92a2a"},
}
```

The `givens` value controls how many cells are visible at the start. Easy puzzles show more fixed cells, while Expert puzzles show fewer cells.

### User Interaction

The GUI keeps track of:

- Fixed cells that came from the original puzzle.
- User-entered cells.
- Wrong cells found by checking.
- Hint cells.
- Selected and related cells.
- Timer and number of hints used.

When the user changes a cell, the GUI compares the typed value with the solution string:

```python
if self.vars[row][col].get() != self.solution[row * 9 + col]:
    self.hint_cells.discard((row, col))
```

This lets the GUI update colors, remove old hint marks, and decide whether the puzzle has been completed.

## Requirements

- Python 3.x
- Tkinter for the GUI

Tkinter is included with many standard Python installations. If the GUI does not open, install a Python distribution that includes Tkinter or install the Tkinter package for your operating system.

This project does not require external Python packages.

## How to Compile

Python is an interpreted language, so there is no separate compile step like in C, C++, or Java.

To check that the source files can be parsed successfully, you can run:

```bash
python -m py_compile sudoku_gui.py Lab45-Sudoku/sudoku.py Lab45-Sudoku/csp.py Lab45-Sudoku/search.py Lab45-Sudoku/util.py
```

If the command finishes without errors, the files compiled successfully to Python bytecode.

## How to Run the GUI

From the project root directory:

```bash
python sudoku_gui.py
```

The GUI starts with a launcher window. Choose a difficulty level and start a puzzle. The GUI uses puzzles from the data files in `Lab45-Sudoku/data/`. If the data files are missing, it falls back to a small built-in puzzle list.

## How to Run the Command-Line Solver

### Option 1: Run the original solver

From the project root directory:

```bash
python Lab45-Sudoku/sudoku.py --inputFile data/euler.txt
```

The input path is resolved relative to the `Lab45-Sudoku` folder, so `data/euler.txt` points to:

```text
Lab45-Sudoku/data/euler.txt
```

### Option 2: Run the CLI mode from the GUI entry point

From the project root directory:

```bash
python sudoku_gui.py --cli --inputFile data/euler.txt
```

You can also solve another puzzle file:

```bash
python sudoku_gui.py --cli --inputFile data/magictour.txt
```

## Input Format

Each puzzle must be written on one line as exactly 81 characters.

- Use digits `1` to `9` for fixed cells.
- Use `0` for blank cells.
- Do not include spaces inside a puzzle line.

Example:

```text
003020600900305001001806400008102900700000008006708200002609500800203009005010300
```

This represents a 9x9 board read from left to right and top to bottom.

## Output

After solving, the command-line solver writes solved puzzles to:

```text
Lab45-Sudoku/output.txt
```

Each solved puzzle is written as one 81-character line. The solver also prints each solved board and timing information to the terminal.

Example terminal output:

```text
The board -  1  takes  0.0069811344146728516  seconds
After solving:
4  8  3   |  9   2  1   |  6   5  7
9  6  7   |  3   4  5   |  8   2  1
2  5  1   |  8   7  6   |  4   9  3
-------------------------------------------
5  4  8   |  1   3  2   |  9   7  6
7  2  9   |  5   6  4   |  1   3  8
1  3  6   |  7   9  8   |  2   4  5
-------------------------------------------
3  7  2   |  6   8  9   |  5   1  4
8  1  4   |  2   5  3   |  7   6  9
6  9  5   |  4   1  7   |  3   8  2
Number of problems solved is:  1
Time taken to solve the puzzles is:  0.007978439331054688
```

Example `output.txt` content:

```text
483921657967345821251876493548132976729564138136798245372689514814253769695417382
```

## Notes for Development

- The core solver logic is in `Lab45-Sudoku/search.py`.
- The CSP model is in `Lab45-Sudoku/csp.py`.
- The GUI imports the solver by adding `Lab45-Sudoku` to `sys.path`.
- The current solver uses backtracking with MRV and forward checking as its main path.
- AC-3 is implemented but is not automatically called by the current `Backtracking_Search()` function.

## Example Workflow

1. Add or edit puzzles in `Lab45-Sudoku/data/euler.txt`.
2. Run the command-line solver:

```bash
python sudoku_gui.py --cli --inputFile data/euler.txt
```

1. Check solved results in `Lab45-Sudoku/output.txt`.
2. Launch the GUI:

```bash
python sudoku_gui.py
```

1. Play generated puzzles using the same solver backend.
