import os
# =============================================
# Sokoban Board Size Extraction Script
# =============================================
# This script calculates the size (rows x columns) of each Sokoban 
# board stored in .xsb files within a specific folder. The script 
# traverses the folder, computes the dimensions of each board, and 
# writes the results to a 'board_sizes.txt' file. The folder path is 
# dynamically generated based on the script's location.
# =============================================

def get_board_size(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        rows = len(lines)
        columns = max(len(line.rstrip()) for line in lines)
        return rows, columns

def count_goals_and_boxes(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        goals = content.count('.')
        boxes = content.count('$')
        bog=content.count('*')
        goals=goals+bog
        boxes=boxes+bog
        return goals, boxes

def generate_sizes_file(folder_path):
    output_file = os.path.join(folder_path, 'boards_properties.txt')
    with open(output_file, 'w') as output:
        for filename in os.listdir(folder_path):
            if filename.endswith('.xsb'):
                file_path = os.path.join(folder_path, filename)
                rows, columns = get_board_size(file_path)
                goals, boxes = count_goals_and_boxes(file_path)
                output.write(f'{filename}: {rows} x {columns}, Goals: {goals}, Boxes: {boxes}\n')

# Get the script path
script_path = os.path.dirname(os.path.realpath(__file__))

# Move one folder back and then go to 'boards\Sokoban master levels xsb'
folder_name='simple boards'
folder_path = os.path.join(os.path.dirname(script_path), 'boards', folder_name)

# Generate the sizes file
generate_sizes_file(folder_path)

print(f'Sizes of boards written to {os.path.join(folder_path, "boards_properties.txt")}')
