import os

def frame_board_with_walls(board):
    """Modify the board to have a '#' frame."""
    rows = len(board)
    if rows == 0:
        return board
    
    cols = len(board[0])
    
    # Modify the first and last rows
    board[0] = '#' * cols
    board[-1] = '#' * cols
    
    # Modify the first and last columns of the remaining rows
    for i in range(1, rows - 1):
        board[i] = '#' + board[i][1:-1] + '#'
    
    return board

def process_boards_in_folder(folder_path):
    """Process all .xsb board files in the specified folder."""
    for filename in os.listdir(folder_path):
        if filename.endswith('.xsb'):  # Check if the file has .xsb extension
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    board = file.readlines()
                    # Strip newline characters and convert each line to a list
                    board = [line.strip() for line in board]

                # Frame the board with walls
                modified_board = frame_board_with_walls(board)

                # Write the modified board back to the file
                with open(file_path, 'w') as file:
                    for line in modified_board:
                        file.write(line + '\n')
                print(f"Processed {filename}")

# Example usage
folder_path = 'boards/original plus extra'
process_boards_in_folder(folder_path)
