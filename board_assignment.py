# translates XSB symbols to those used in the .smv file
def assign_board(board):
    rows = board.strip().split('\n')
    symbol_map = {'@': '_', '+': '_', '$': 'b', '*': 'b', '#': 'x', '.': '.', '_': '_','-':'_'}
    board_list = [list(row) for row in rows]
    
    for i, row in enumerate(rows):
        for j, char in enumerate(row):
            if char in symbol_map:
                value = symbol_map[char]
                board_list[i][j] = value
                if char == '@':
                    worker_holder = [i, j]
            else:
                print(f"WRONG SYMBOL EXISTS char={char} i={i} j={j}")

    return worker_holder, board_list