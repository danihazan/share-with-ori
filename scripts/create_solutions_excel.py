import os
import re
import pandas as pd

def extract_times(file_content):
    """Extracts running/simulation times and dynamically creates columns based on solver names"""
    times = {}

    # Regex patterns to match the time lines
    simulation_time_pattern = re.compile(r'Simulation Time:\s+([0-9.]+)\s+seconds')
    running_time_pattern = re.compile(r'Running Time:\s+([0-9.]+)\s+seconds')

    # Split the file content into lines
    lines = file_content.splitlines()

    current_solver = None

    # Iterate over each line in the file content
    for line in lines:
        # If the line contains a solver header (e.g., "Takaken solver", "YASS solver", etc.)
        if "solver" in line.lower():
            # Clean the solver name by removing any '-' or extra characters
            current_solver = line.replace('-', '').strip()
            if current_solver not in times:
                times[current_solver] = None  # Create the column for this solver

        # Check for simulation or running time if we're in a solver section
        if current_solver:
            simulation_match = simulation_time_pattern.search(line)
            running_match = running_time_pattern.search(line)
            if simulation_match:
                times[current_solver] = float(simulation_match.group(1))
            elif running_match:
                times[current_solver] = float(running_match.group(1))

    return times

def process_directory(directory_path):
    """Processes all solution files in the directory and extracts times"""
    data = []
    board_names = []

    for filename in os.listdir(directory_path):
        if filename.endswith("_summarized.txt"):
            file_path = os.path.join(directory_path, filename)
            board_name = filename.replace("_output_summarized.txt", "")
            board_names.append(board_name)

            # Read the file content
            with open(file_path, 'r') as file:
                content = file.read()

            # Extract times for the board
            times = extract_times(content)
            data.append(times)

    return board_names, data

def create_excel_report(directory_path):
    """Creates an Excel report from the extracted times and saves it in the directory"""
    board_names, data = process_directory(directory_path)
    
    # Create a DataFrame for the extracted data, filling any missing solver columns with None
    df = pd.DataFrame(data, index=board_names).fillna("")

    # Define the output file path within the directory
    output_file = os.path.join(directory_path, 'solver_times_report.xlsx')

    # Save the DataFrame to an Excel file in the given directory
    df.to_excel(output_file)

# Example usage
directory_path = 'boards/simple boards/solutions'  # Replace with the actual directory path containing the files
output_file = 'solver_times_report.xlsx'  # Replace with your desired output file name
create_excel_report(directory_path)
