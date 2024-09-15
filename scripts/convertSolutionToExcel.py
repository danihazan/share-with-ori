import pandas as pd

def parse_solver_section(section):
    """Parses a section of the text corresponding to a solver and returns a dictionary with the details."""
    lines = section.strip().splitlines()
    solver_name = lines[0].replace('----------', '').strip()
    solution = ''
    time = ''
    memory = ''
    
    for line in lines:
        if line.startswith('Solution:'):
            solution = line.split(':', 1)[1].strip()
        elif 'Simulation Time:' in line:
            time = line.split(':', 1)[1].strip()
        elif 'Peak Memory Usage:' in line:
            memory = line.split(':', 1)[1].strip()

    return {
        'Solver': solver_name,
        'Solution': solution,
        'Simulation Time': time,
        'Peak Memory Usage': memory
    }

def process_text_file(file_path):
    """Processes the input text file and converts it to an Excel file."""
    with open(file_path, 'r') as file:
        content = file.read()

    sections = content.split('----------')[1:]  # Split the content by solver sections
    data = []
    
    for section in sections:
        parsed_data = parse_solver_section(section)
        data.append(parsed_data)
    
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(data)
    
    # Write the DataFrame to an Excel file
    output_excel_file = file_path.replace('.txt', '.xlsx')
    df.to_excel(output_excel_file, index=False)
    print(f"Excel file created: {output_excel_file}")

# Example usage
file_path = 'simple boards/solutions/board1_output_summarized.txt'
process_text_file(file_path)
