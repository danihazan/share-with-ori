import os
import re

# =============================================
# Sokoban Board Extraction Script
# =============================================
# This script reads a text file containing multiple Sokoban boards and 
# extracts each board into a separate .xsb file. Only lines containing 
# valid Sokoban characters (e.g., #, @, $, ., +, -, *) are included in 
# the output files. Each board is saved with a filename based on its 
# corresponding "Title:" line from the input file. The .xsb files are 
# saved in the same directory as the input file.
# =============================================


def extract_boards(input_file_path):
    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    board = []  # Start with an empty board list
    title = None  # Initialize title as None

    # Get the folder path of the input file
    output_folder = os.path.dirname(input_file_path)

    # Define a regex pattern to match lines that contain only valid xsb characters
    xsb_pattern = re.compile(r'^[#@$.+\-*]+$')

    for line in lines:
        line = line.rstrip()  # Remove trailing whitespace
        if line.startswith("Title:"):
            title = line.split(":")[1].strip()  # update title
            # Write the previous board to a .xsb file
            output_file_path = os.path.join(output_folder, f'board_{title}.xsb')
            with open(output_file_path, 'w') as output_file:
                output_file.write('\n'.join(board) + '\n')
            
            # Set the title for the next board and reset the board list
            board = []  # Reset board for the next set of lines
        else:
            # Add the line to the current board only if it contains only valid xsb characters
            if xsb_pattern.match(line):
                board.append(line)

    # Write the last board to a file if it exists
    if title and board:  # <-- Ensures the last board is written out
        output_file_path = os.path.join(output_folder, f'board_{title}.xsb')
        with open(output_file_path, 'w') as output_file:
            output_file.write('\n'.join(board) + '\n')
            
# Paths

# Get the script path
script_path = os.path.dirname(os.path.realpath(__file__))
# Move one folder back and then go to 'boards\Sokoban master levels xsb'
folder_name='original 1'
folder_path = os.path.join(os.path.dirname(script_path), 'boards', folder_name)

input_file_path = folder_path+'/DrFogh-Original01.txt'

# Create the output directory if it doesn't exist
os.makedirs(folder_path, exist_ok=True)

# Extract boards and write to .xsb files
extract_boards(input_file_path)

print(f"Boards have been extracted and saved in the {folder_path} directory.")
