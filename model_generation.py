# update worker_row, worker_col according to movement
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
    down_push := worker_row<{rows-2} & board[worker_row+1][worker_col] & !walls[worker_row+2][worker_col] & !board[worker_row+2][worker_col];

    right_step := worker_col<{columns-1} & !walls[worker_row][worker_col+1] & !board[worker_row][worker_col+1];
    right_push := worker_col<{columns-2} & board[worker_row][worker_col+1] & !walls[worker_row][worker_col+2] & !board[worker_row][worker_col+2];

    left_step := worker_col>0 & !walls[worker_row][worker_col - 1] & !board[worker_row][worker_col - 1];
    left_push := worker_col>1 & board[worker_row][worker_col - 1] & !walls[worker_row][worker_col - 2] & !board[worker_row][worker_col - 2];

    up_step := worker_row>0 & !walls[worker_row - 1][worker_col] & !board[worker_row - 1][worker_col];
    up_push := worker_row>1 & board[worker_row - 1][worker_col] & !walls[worker_row - 2][worker_col] & !board[worker_row - 2][worker_col];
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
    deadlock_matrix=get_deadlock_matrix(board_content)

    model_content += f'''
deadlock :='''
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


    model_content+=f"\nINVARSPEC"
    model_content+=f"\n\t"
    for i in range(rows):
        for j in range(columns):
            if deadlock_matrix[i][j] == True:
                model_content += f"!board[{i}][{j}] & "
    model_content = model_content[:-3]  # remove the last " & "
    model_content+=f";\n"


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

def parse_board(board_str):
    """ Parses the board string into a 2D list. """
    return [list(row) for row in board_str.strip().split('\n')]

def is_corner(board, x, y):
    """ Checks if the cell at (x, y) is a corner cell. """
    max_x = len(board) - 1
    max_y = len(board[0]) - 1

    # Boundary check to prevent index errors
    if x == 0 or x == max_x or y == 0 or y == max_y or board[x][y]=='#' or board[x][y]=='.':
        return False  # Edges but not corners

    # Check for corners
    top_left = (board[x-1][y] == '#' and board[x][y-1] == '#')
    top_right = (board[x-1][y] == '#' and board[x][y+1] == '#')
    bottom_left = (board[x+1][y] == '#' and board[x][y-1] == '#')
    bottom_right = (board[x+1][y] == '#' and board[x][y+1] == '#')

    return top_left or top_right or bottom_left or bottom_right

def check_corners(board):
    """ Returns a matrix indicating whether each cell is a corner. """
    rows = len(board)
    cols = len(board[0])
    corner_matrix = [[False] * cols for _ in range(rows)]

    for x in range(1, rows - 1):  # Avoid the edges
        for y in range(1, cols - 1):  # Avoid the edges
            corner_matrix[x][y] = is_corner(board, x, y)

    return corner_matrix

def check_row_deadlocks(board):
    rows = len(board)
    cols = len(board[0])
    deadlock_matrix = [[False for _ in range(cols)] for _ in range(rows)]
    
    for i in range(rows):
        start = -1  # Start of a potential deadlock segment
        for j in range(cols):
            if board[i][j] == '#':
                if start != -1:  # There was a segment before this wall
                    if '.' not in board[i][start:j]:  # Check for no goals in the segment
                        all_above_blocked = all(board[k][m] == '#' for m in range(start, j) for k in range(i))
                        all_below_blocked = all(board[k][m] == '#' for m in range(start, j) for k in range(i+1, rows))
                        if all_above_blocked or all_below_blocked:
                            for k in range(start, j):
                                deadlock_matrix[i][k] = True
                start = j + 1  # Update start to the position after the wall
            elif board[i][j] == '.':
                start = -1  # Reset start because a goal disrupts the potential deadlock segment

    return deadlock_matrix

def check_column_deadlocks(board):
    rows = len(board)
    cols = len(board[0])
    deadlock_matrix = [[False for _ in range(cols)] for _ in range(rows)]
    
    for j in range(cols):
        start = -1  # Start of a potential deadlock segment
        for i in range(rows):
            if board[i][j] == '#':
                if start != -1:  # There was a segment before this wall
                    if '.' not in [board[k][j] for k in range(start, i)]:  # Check for no goals in the segment
                        # Check if all cells to the immediate left are walls
                        all_left_blocked = j > 0 and all(board[k][j-1] == '#' for k in range(start, i))
                        # Check if all cells to the immediate right are walls
                        all_right_blocked = j < cols-1 and all(board[k][j+1] == '#' for k in range(start, i))
                        
                        if all_left_blocked or all_right_blocked:
                            for k in range(start, i):
                                deadlock_matrix[k][j] = True
                start = i + 1  # Update start to the position after the wall
            elif board[i][j] == '.':
                start = -1  # Reset start because a goal disrupts the potential deadlock segment

    return deadlock_matrix

def combine_deadlocks(*matrices):
    """Combine multiple deadlock matrices into one by performing an element-wise logical OR."""
    rows = len(matrices[0])
    cols = len(matrices[0][0])
    combined_matrix = [[False] * cols for _ in range(rows)]
    
    for i in range(rows):
        for j in range(cols):
            # Apply logical OR across the same element in all matrices
            combined_matrix[i][j] = any(matrix[i][j] for matrix in matrices)
    
    return combined_matrix

def get_deadlock_matrix(board_str):
    board = parse_board(board_str)
    col_deadlock_matrix = check_column_deadlocks(board)
    row_deadlock_matrix=check_row_deadlocks(board)
    corner_deadlock_matrix=check_corners(board)
    # Combine all deadlock matrices into one
    deadlock_matrix = combine_deadlocks(col_deadlock_matrix, row_deadlock_matrix, corner_deadlock_matrix)
    return deadlock_matrix
