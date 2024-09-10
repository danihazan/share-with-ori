# update worker_row, worker_col according to movement
import copy


def worker_location_change(rows, columns):
    model_content = f'''
next(worker_row):=
case
    movement = u & (up_step | up_push): worker_row - 1;
    movement = d & (down_step | down_push): worker_row + 1;
    TRUE: worker_row;
esac;

next(worker_col):=
case
    movement = r & (right_step | right_push): worker_col + 1;
    movement = l & (left_step | left_push): worker_col - 1;
    TRUE: worker_col;
esac;
    '''
    return model_content


# board FDS
def moves(i,j, rows, columns, board):
    model_content=""
    # right
    if i>=0 and j-2>=0 and board[i][j-2]!="x":
        model_content+=f"\tmovement=r & right_push & worker_row={i} & worker_col={j-2} : TRUE;\n"
    if i>=0 and j-1>=0 and board[i][j-1]!="x":
        model_content+=f"\tmovement=r & right_push & worker_row={i} & worker_col={j-1} : FALSE;\n"
    
    # down
    if i-2>=0 and j>=0 and board[i-2][j]!="x":
        model_content+=f"\tmovement=d & down_push & worker_row={i-2} & worker_col={j} : TRUE;\n"
    if i-1>=0 and j>=0 and board[i-1][j]!="x":
        model_content+=f"\tmovement=d & down_push & worker_row={i-1} & worker_col={j} : FALSE;\n"

    # left
    if i>=0 and j+2<columns and board[i][j+2]!="x":
        model_content+=f"\tmovement=l & left_push & worker_row={i} & worker_col={j+2} : TRUE;\n"
    if i>=0 and j+1<columns and board[i][j+1]!="x":
        model_content+=f"\tmovement=l & left_push & worker_row={i} & worker_col={j+1} : FALSE;\n"

    # up
    if i+2<rows and j>=0 and board[i+2][j]!="x":
        model_content+=f"\tmovement=u & up_push & worker_row={i+2} & worker_col={j} : TRUE;\n"
    if i+1<rows and j>=0 and board[i+1][j]!="x":
        model_content+=f"\tmovement=u & up_push & worker_row={i+1} & worker_col={j} : FALSE;\n"
    model_content+=f"\n"    

    return model_content


# main function to generate the .smv file
def generate_nusmv_model(rows ,columns,board_content, board, worker_holder):
    model_content = f'''
MODULE main
DEFINE rows:={rows}; columns:={columns};
-- new  XSB     definition
-- a      @      warehouse keeper
-- o      +      warehouse keeper on goal
-- b      $      box
-- v      *      box on goal
-- x      #      wall
-- g      .      goal
-- _      _      floor
VAR
    worker_row : 0..{rows-1}; --current worker row
    worker_col : 0..{columns-1}; --current worker col
    movement : {{u, d, l, r, 0}};
    board : array 0..{rows-1} of array 0..{columns-1} of boolean;
    
ASSIGN
'''
    for i in range(rows):
        for j in range(columns):
            if board[i][j]=='b':
                model_content+=f"init(board[{i}][{j}]):=TRUE;\t"
            else:
                model_content+=f"init(board[{i}][{j}]):=FALSE;\t"
        model_content+=f"\n"

    model_content+=f'''
init(movement) := 0;

init(worker_row) := {worker_holder[0]}; init(worker_col) := {worker_holder[1]};
'''

    model_content += worker_location_change(rows, columns)
    model_content+=f"next(movement):={{u, d ,l ,r}};"
    for i in range(rows):
        for j in range(columns):
            if board[i][j]=='x': # state 'x' cant change
                model_content += f"\nnext(board[{i}][{j}]):= board[{i}][{j}];\n"
            else:
                model_content+= f"\nnext(board[{i}][{j}]):=\ncase\n"
                model_content+=moves(i,j, rows, columns, board)
                model_content+= f"\tTRUE: board[{i}][{j}];\nesac;\n"


    model_content += f'''
    
DEFINE
    down_step := worker_row<{rows-1} & !walls[worker_row+1][worker_col] & !board[worker_row+1][worker_col];
    down_push := worker_row<{rows-2} & board[worker_row+1][worker_col] & !walls[worker_row+2][worker_col] & !board[worker_row+2][worker_col] & !deadlocks[worker_row+2][worker_col];

    right_step := worker_col<{columns-1} & !walls[worker_row][worker_col+1] & !board[worker_row][worker_col+1];
    right_push := worker_col<{columns-2} & board[worker_row][worker_col+1] & !walls[worker_row][worker_col+2] & !board[worker_row][worker_col+2] & !deadlocks[worker_row][worker_col+2];

    left_step := worker_col>0 & !walls[worker_row][worker_col - 1] & !board[worker_row][worker_col - 1];
    left_push := worker_col>1 & board[worker_row][worker_col - 1] & !walls[worker_row][worker_col - 2] & !board[worker_row][worker_col - 2] & !deadlocks[worker_row][worker_col - 2];

    up_step := worker_row>0 & !walls[worker_row - 1][worker_col] & !board[worker_row - 1][worker_col];
    up_push := worker_row>1 & board[worker_row - 1][worker_col] & !walls[worker_row - 2][worker_col] & !board[worker_row - 2][worker_col] & !deadlocks[worker_row - 2][worker_col];
'''

    model_content += f'''
walls :='''
    # creating the walls constant
    model_content += " [\n"
    for i in range(rows):
        model_content += "["
        for j in range(columns):
            if board[i][j] == 'x':
                model_content += " TRUE"
            else:
                model_content += "FALSE"
            if j < columns - 1:
                model_content += ", "
        model_content += "]"
        if i < rows - 1:
            model_content += ",\n"

    model_content += "];"

    deadlock_matrix=find_deadlock_squares(board_content)
    model_content += f'''
deadlocks :='''
    # creating the walls constant
    model_content += " [\n"
    for i in range(rows):
        model_content += "["
        for j in range(columns):
            if deadlock_matrix[i][j] == True:
                model_content += " TRUE"
            else:
                model_content += "FALSE"
            if j < columns - 1:
                model_content += ", "
        model_content += "]"
        if i < rows - 1:
            model_content += ",\n"

    model_content += "];"


    model_content += f"DEFINE\n"
    model_content +=f"\treach:= "
    for i in range(rows):
        for j in range(columns):
            if board[i][j]=='.':
                    model_content += f"board[{i}][{j}] & "
    model_content = model_content[:-3]  # remove the last " & "
    model_content+=";"
    
    model_content += f"\n\tLTLSPEC G(!reach)"
    
    return model_content

# Define Sokoban elements
WALL = '#'
FLOOR = '-'
BOX = '$'
GOAL = '.'
PLAYER = '@'
BOX_ON_GOAL = '*'
PLAYER_ON_GOAL = '+'

# Helper functions to process Sokoban board
def parse_xsb(xsb_str):
    """Parses the Sokoban board from XSB format string."""
    board = [list(line) for line in xsb_str.strip().splitlines()]
    return board

def clear_board(board):
    """Clears all boxes from the board to prepare for the pull algorithm."""
    cleared_board = copy.deepcopy(board)
    for y, row in enumerate(cleared_board):
        for x, cell in enumerate(row):
            if cell == BOX or cell == BOX_ON_GOAL:
                cleared_board[y][x] = GOAL if cell == BOX_ON_GOAL else FLOOR
            if cell == PLAYER or cell == PLAYER_ON_GOAL:
                cleared_board[y][x] = GOAL if cell == PLAYER_ON_GOAL else FLOOR

    return cleared_board

def find_goals(board):
    """Finds the coordinates of all goal squares."""
    goals = []
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell in [GOAL, PLAYER_ON_GOAL, BOX_ON_GOAL]:
                goals.append((y, x))
    return goals

def is_free_square(board, y, x):
    """Checks if a square is free (walkable) for the player."""
    return board[y][x] in [FLOOR, GOAL]

def pull_box(board, start_y, start_x, visited):
    """Performs the pull algorithm starting from a goal square."""
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    stack = [(start_y, start_x)]
    visited.add((start_y, start_x))
    
    while stack:
        y, x = stack.pop()
        
        for dy, dx in directions:
            new_y, new_x = y + dy, x + dx
            
            # Check if pulling is possible (opposite side is free)
            if (0 < new_y < (len(board)-1) and 0 < new_x < (len(board[0])-1) and 
                (new_y, new_x) not in visited and is_free_square(board, new_y, new_x)and is_free_square(board, new_y+dy, new_x+dx)):
                
                visited.add((new_y, new_x))
                stack.append((new_y, new_x))

def find_deadlock_squares(xsb_str):
    """Identifies simple deadlock squares on the Sokoban board."""
    board = parse_xsb(xsb_str)
    goals = find_goals(board)
    visited = set()
    
    # Clear the board of all boxes
    cleared_board = clear_board(board)
    
    # Iterate over all goal squares
    for goal_y, goal_x in goals:
        # Place a box at the goal square
        temp_board = copy.deepcopy(cleared_board)
        temp_board[goal_y][goal_x] = BOX
        
        # Perform the pull operation
        pull_box(temp_board, goal_y, goal_x, visited)
    
    #Creates a boolean matrix of the same size as the Sokoban board based on the visited set.
    # b
    deadlock_matrix = [[True for _ in row] for row in board]
    for (y, x) in visited:
        deadlock_matrix[y][x] = False
    return deadlock_matrix
