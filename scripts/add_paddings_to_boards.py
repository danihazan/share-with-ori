import os
# =============================================
# Sokoban Board Line Padding Script
# =============================================
# This script pads each line in Sokoban board files (.xsb) so that all 
# lines within a board have the same length. The script traverses a 
# specified folder, finds all .xsb files, and adjusts each line by 
# padding it with '-' characters to match the length of the longest 
# line in that board. The files are then overwritten with the padded 
# lines.
# =============================================

def pad_board_lines(file_path):
    with open(file_path, 'r') as file:
        lines = [line.rstrip() for line in file.readlines()]
        
    if not lines:
        return  # Skip empty files
    
    max_columns = max(len(line) for line in lines)
    
    # Pad lines with '-' to match the max_columns length
    padded_lines = [line.ljust(max_columns, '-') for line in lines]
    
    # Write the padded board back to the file
    with open(file_path, 'w') as file:
        file.write('\n'.join(padded_lines) + '\n')

def pad_boards_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.xsb'):
            file_path = os.path.join(folder_path, filename)
            pad_board_lines(file_path)

# Example usage
# Get the script path
script_path = os.path.dirname(os.path.realpath(__file__))

# Move one folder back and then go to 'boards\Sokoban master levels xsb'
folder_name='It is all greek'
folder_path = os.path.join(os.path.dirname(script_path), 'boards', folder_name)
pad_boards_in_folder(folder_path)

print(f"All boards in {folder_path} have been padded to the maximum line length.")
