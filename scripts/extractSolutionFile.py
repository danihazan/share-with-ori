import glob
import os
import re


def extract_solutions_for_directory(directory_path):
    # Create the search pattern
    pattern="output.txt"
    search_pattern = os.path.join(directory_path, f"*{pattern}*")

    # Find all files matching the pattern
    solution_files = glob.glob(search_pattern)

    # Remove each file
    for file_path in solution_files:
        try:
            if os.path.isfile(file_path):
                # Run the extract_solution function on each file
                solution = create_summarized_solution_file(file_path)
        except Exception as e:
            print(f"Failed to remove {file_path}: {e}")

def create_summarized_solution_file(input_file):
        # Get the directory and base name of the input file
    input_dir = os.path.dirname(input_file)
    input_basename = os.path.basename(input_file)
    
    # Create the output file name with "_sol" before the file extension
    output_basename = re.sub(r'(\.[^\.]+)$', r'_summarized\1', input_basename)
    output_file = os.path.join(input_dir, output_basename)

    
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        outfile.write("Summarized Solutions:\n")
        
        # Step 1: Write "Board:" and extract lines until the first "-----"
        outfile.write("Board:\n")
        outfile.write(input_file+"\n")
        for line in infile:
            if line.strip() == "------------------------------------------------------":
                break

        # Step 2:Copy board to file Extract lines until the line containing "Time"
        for line in infile:
            if "Time" in line:
                break
            outfile.write(line)
        # Step 3: Write "Takaken solver" and extract lines until the second "-----"
        outfile.write("----------Takaken solver----------\n")
        for line in infile:
            if line.strip() == "------------------------------------------------------":
                break
            if not "Time:" in line:
                outfile.write(line)

        #Copy Takaken simulation Data:    
        for line in infile:
            if line.strip() == "--- YASS Solver Results ---":
                break
            if "Simulation Time:" or "Peak Memory" in line:
                outfile.write(line)
        #Copy YASS  Data:    
        outfile.write("----------YASS solver Optimize Pushes----------\n")
        for line in infile:
            if line.strip() == "Solution" or "No log File" in line:  # Check if the line is exactly "Solution"
                break  # Stop processing when "Solution" is found
            if any(keyword in line for keyword in ["Pushes","pushes"]):
                outfile.write(line)
        for line in infile:
            if line.strip() == "--- YASS Solver Results ---":
                break
            outfile.write(line)
        #Copy YASS  Data:    
        outfile.write("----------YASS solver Optimize Moves----------\n")
        for line in infile:
            if line.strip() == "Solution" or "No log File" in line:  # Check if the line is exactly "Solution"
                break  # Stop processing when "Solution" is found
            if any(keyword in line for keyword in ["pushes","Pushes"]):
                outfile.write(line)
        for line in infile:
            if line.strip() == "--- nuXmv Sokoban Solver Results ---":
                break
            outfile.write(line)
        outfile.write("----------Nuxmv Solver Dynamic Deadlocks----------\n")
        for line in infile:
            if line.strip() == "--- nuXmv Sokoban Solver Results ---":
                break
            outfile.write(line)
        outfile.write("----------Nuxmv Solver Static Dlocks----------\n")
        for line in infile:
            if line.strip() == "--- nuXmv Sokoban Solver Results ---":
                break
            outfile.write(line)

        outfile.write("----------Nuxmv Solver no Ddlcks ----------\n")
        for line in infile:
            if "Execution time:" in line:
                break
        for line in infile:
            outfile.write(line)


# Example usage
directory_path = 'boards/simple boards/solutions'
create_summarized_solution_file('boards/simple boards/solutions/board3_output.txt')
