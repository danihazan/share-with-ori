import os
import time
import run_nuxmv
import model_generation
import board_assignment
import LURD_format_creator


def save_model_to_file(model_content, filename):
    with open(filename, 'w') as f:
        f.write(model_content)


def main(board, input_filename, solver_engine, steps=None):
    start_time = time.time()
    
    # Get the directory of the input file
    input_directory = os.path.dirname(input_filename)
    
    # Create the output folder name in the same directory as the input file
    base_name = os.path.splitext(os.path.basename(input_filename))[0]
    if solver_engine is None:
        folder_name = os.path.join(input_directory, base_name)
    else:
        folder_name = os.path.join(input_directory, f"{base_name}_{solver_engine}")
    
    # Ensure the output directory exists
    os.makedirs(folder_name, exist_ok=True)
    
    # Create the output filename in the same directory
    LURD_output_filename = os.path.join(folder_name, f"{base_name}_LURD.out")
    with open(LURD_output_filename, "w") as f:
        pass  # clears file
    
    lines_num = board.strip().split('\n')
    rows = len(lines_num)
    columns= len(lines_num[0])
    board_content=board
    worker_holder, board = board_assignment.assign_board(board) # translate board from XSB to format used in the .smv file
    model_content = model_generation.generate_nusmv_model(rows, columns,board_content, board, worker_holder) # create nusmv code
    
    smv_filename = os.path.join(folder_name, f"{base_name}.smv") # create output file name, according to input file name
    
    save_model_to_file(model_content, smv_filename) # save contents of code to .smv file
    
    _, stdout = run_nuxmv.run_nuxmv(base_name, folder_name, smv_filename, solver_engine, steps) # run nuXmv file 

    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time: ", execution_time, "seconds")
    
    LURD_file_name, LURD_format=  LURD_format_creator.extract_LURD(stdout, base_name, folder_name, steps, None) # create correct LURD format
    
    with open(LURD_file_name, "a") as f:
        if LURD_format!=None:
            f.write("Solution : ")
            f.write(LURD_format+f"\n")
        f.write("Execution time : ")
        f.write(str(execution_time))
        f.write(f" seconds\n")

        
if __name__=="__main__":
    main()
