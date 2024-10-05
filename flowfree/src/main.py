import copy
import Grid
import Csp
import timeit
import math
from collections import ChainMap
import tkinter as tk
import tkinter.font as tkFont

# Define colors for terminal output
class Colors:
    W_COLOR = '\033[97m'
    Y_COLOR = '\033[93m'
    B_COLOR = '\033[94m'
    R_COLOR = '\033[91m'
    G_COLOR = '\033[92m'
    P_COLOR = '\033[95m'
    O_COLOR = '\033[48;5;214m'
    M_COLOR = '\033[35m'
    K_COLOR = '\033[33m'
    Q_COLOR = '\033[34m'
    D_COLOR = '\033[30m'
    A_COLOR = '\033[36m'
    C_COLOR = '\033[32m'
    E_COLOR = '\033[95m'
    F_COLOR = '\033[90m'
    H_COLOR = '\033[96m'
    I_COLOR = '\033[91m'
    J_COLOR = '\033[92m'
    L_COLOR = '\033[93m'
    N_COLOR = '\033[94m'
    T_COLOR = '\033[95m'
    U_COLOR = '\033[30m'
    V_COLOR = '\033[35m'
    X_COLOR = '\033[31m'
    Z_COLOR = '\033[36m'
    ENDC = '\033[0m'

# Define colors for Tkinter output
HTML_COLORS = {
    'A': 'aqua',
    'B': 'blue',
    'C': 'lightgreen',
    'D': 'black',
    'E': 'purple',
    'F': 'orange',
    'G': 'green',
    'H': 'yellow',
    'I': 'indigo',
    'J': 'green',
    'K': 'brown',
    'L': 'lemon',
    'M': 'magenta',
    'N': 'navy',
    'O': 'orange',
    'P': 'pink',
    'Q': 'grey',
    'R': 'red',
    'S': 'lightgreen',
    'T': 'purple',
    'U': 'ultramarine',
    'V': 'violet',
    'W': 'white',
    'X': 'black',
    'Y': 'yellow',
    'Z': 'cyan',
}

def colorize_text_terminal(text):
    colored_text = ""
    for char in text:
        if char in HTML_COLORS:
            colored_text += f"{getattr(Colors, f'{char}_COLOR')}{char}{Colors.ENDC}"
        else:
            colored_text += char
    return colored_text


def show_output_window(solution, attempts, time_taken):
    output_window = tk.Tk()
    output_window.title("Puzzle Output")

    # Create a larger font
    font_style = tkFont.Font(family="Helvetica", size=32)  # Increase the size here

    text_widget = tk.Text(output_window, wrap='word', width=80, height=30, bg='black', fg='white', font=font_style)
    text_widget.pack(expand=True, fill='both')

    # Insert attempts and time taken
    text_widget.insert(tk.END, f"Attempts: {attempts}\n", "attempts")
    text_widget.insert(tk.END, f"Time taken: {time_taken:.2f} s\n", "time")

    # Insert the solution with colors
    for row in solution:
        for char in row:
            color = HTML_COLORS.get(char, 'black')
            text_widget.insert(tk.END, char, char)  # Insert character with tag
            text_widget.tag_config(char, foreground=color, font=font_style)  # Create tag for color
        text_widget.insert(tk.END, "\n")  # New line after each row

    text_widget.tag_config("attempts", foreground='orange', font=font_style)
    text_widget.tag_config("time", foreground='gold', font=font_style)
    text_widget.config(state=tk.DISABLED)  # Make it read-only

    output_window.geometry("800x600")  # Set window size

    output_window.mainloop()



start = timeit.default_timer()
ini_square = []

print(">>> Welcome to Flow Free Game\n")
print(">>> Choose the size of Puzzle:")
print("1. 7×7\t2. 8×8\t3. 9×9\t4. 10×10")
size = input("\n>>> Enter number: ")
if size == "1":
    size = 77
elif size == "2":
    size = 88
elif size == "3":
    size = 99
elif size == "4":
    size = 1010
else:
    print("\n>>> Enter valid number ! ! !\n")
    exit()

input_file = f'./input/input{size}.txt'
output_file = f"./output/output{size}.txt"

# Read and display the input file
with open(input_file, 'r') as file:
    f = file.read().splitlines()
    for line in f:
        print(colorize_text_terminal(line))  # Print colored line
        ini_square.append(list(line))
    size = len(ini_square)

print("\n>>> The puzzle is:\n")
with open(input_file, 'r') as file:
    puzzle = file.read()
print(puzzle)

square = Grid.Square(size)
una_var = []
una_pos = set()
value_domain = set()
value_info = dict()
domain = dict()

for i in range(size):
    for j in range(size):
        if ini_square[i][j] == '_':
            square[i][j] = Grid.Grid(i, j, Grid.Type.U)
            una_var.append(square[i][j])
            domain[(i, j)] = None
            una_pos.add((i, j))
        else:
            square[i][j] = Grid.Grid(i, j, Grid.Type.S, ini_square[i][j])
            value_domain.add(ini_square[i][j])
            if ini_square[i][j] not in value_info.keys():
                value_info[ini_square[i][j]] = [(i, j)]
            else:
                value_info[ini_square[i][j]].append((i, j))
                head = value_info[ini_square[i][j]][0]
                tail = value_info[ini_square[i][j]][1]
                dis = int(math.fabs(head[0] - tail[0]) + math.fabs(head[1] - tail[1]))
                value_info[ini_square[i][j]].append(dis)
        square[i][j].set_nei(size)

for i in range(size):
    for j in range(size):
        if (i, j) in una_pos:
            domain[(i, j)] = copy.deepcopy(value_domain)
            square[i][j].set_domain(domain[(i, j)], square)
            domain[(i, j)] = list(domain[(i, j)])
        else:
            square[i][j].set_domain(set(), square)

for x, y in una_pos:
    square[x][y].set_aff_nei(square)

chain_domain = ChainMap(domain)
solution, att = Csp.backtracking(una_var, square, chain_domain, value_info)

# Get the end time
end = timeit.default_timer()

# Prepare output data
output_data = {
    'attempts': att,
    'solution': [['_' if isinstance(cell, Grid.Grid) and cell.value == '_' else cell.value for cell in row] for row in square],
    'time': end - start
}

with open(output_file, 'w') as file:
    file.write(f"Attempts: {att}\n")
    for row in output_data['solution']:
        file.write(''.join(row) + "\n")  # Write row directly to file
    file.write(f"Time taken: {end - start:.2f} s")

# Show output window
show_output_window(output_data['solution'], output_data['attempts'], output_data['time'])
