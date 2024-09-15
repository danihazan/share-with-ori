import os

def process_xsb_file(file_path):
    """Process a single .xsb file to replace chars before the first #, spaces with #, and pad rows"""
    with open(file_path, 'r') as f:
        board = [list(line.rstrip()) for line in f.readlines()]  # Read the board into a list of lists

    # Find the length of the longest row
    max_length = max(len(row) for row in board)

    # Process each row to modify characters
    for row in board:
        first_hash = None

        # Find the index of the first '#' in the row
        for i, char in enumerate(row):
            if char == '#':
                first_hash = i
                break

        # Replace all characters before the first '#' with '#'
        if first_hash is not None:
            for i in range(first_hash):
                row[i] = '#'

        # Replace all ' ' (spaces) with '#'
        for i, char in enumerate(row):
            if char == ' ':
                row[i] = '#'

        # Pad the row with '#' to match the longest row
        if len(row) < max_length:
            row.extend(['#'] * (max_length - len(row)))

    # Overwrite the same file with the modified board
    with open(file_path, 'w') as f:
        for row in board:
            f.write(''.join(row) + '\n')

def process_xsb_directory(directory_path):
    """Process all .xsb files in a given directory"""
    for filename in os.listdir(directory_path):
        if filename.endswith(".xsb"):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file: {file_path}")
            process_xsb_file(file_path)

# Example usage:
directory_path = 'boards/original 1'  # Replace with the path to your directory containing .xsb files
process_xsb_directory(directory_path)
