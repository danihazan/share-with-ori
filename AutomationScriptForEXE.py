import glob
import shutil
import subprocess
import os
import psutil
import time
import psutil
import threading
import time

from scripts.extractSolutionFile import create_summarized_solution_file

def run_takaken_solver(solver_path, board_path, output_file, time_limit=600, level_number="all"):
    """
    Runs the takaken74 Sokoban solver with the specified parameters and monitors memory usage.
    """
    if not os.path.isfile(solver_path):
        print(f"File not found: {solver_path}")
        return

    if not os.path.isfile(board_path):
        print(f"Input file not found: {board_path}")
        return
    
    command = [solver_path, '-in', board_path, '-out', output_file, '-time', str(time_limit), '-level', level_number]

    try:
        simulation_start = time.time()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ps_process = psutil.Process(process.pid)
        peak_memory_usage = [0]  # Use a list to hold the peak memory usage as a mutable object

        # Monitor memory usage in a separate thread
        monitor_thread = threading.Thread(target=monitor_memory, args=(ps_process, peak_memory_usage))
        monitor_thread.start()

        stdout, stderr = process.communicate()  # Wait for the process to complete
        monitor_thread.join()  # Ensure the memory monitoring thread has completed

        simulation_end = time.time()
        simulation_time = simulation_end - simulation_start

        if process.returncode != 0:
            print(f"Errors from the takaken74 solver:\n{stderr}")
        else:
            print(f"Output from the takaken74 solver:\n{stdout if stdout else 'No output received.'}")
            with open(output_file, 'r') as f:
                print(f.read())  # Print the contents of the output file to the screen
            
            with open(output_file, 'a') as f:
                f.write(f"Simulation Time: {simulation_time:.5f} seconds\n")
                f.write(f"Peak Memory Usage: {peak_memory_usage[0]:.2f} MB\n")
            print(f"Simulation Time: {simulation_time:.5f} seconds\n")
            print(f"Peak Memory Usage: {peak_memory_usage[0]:.2f} MB\n")
    except Exception as e:
        print(f"Failed to run the takaken74 solver: {e}")

def run_nuxMv_solver(solver_path, board_path, output_file, iterative_mode=False, engine='SAT', steps_num=None):
    """
    Runs the nuXmv_solver.exe with the specified parameters directly and enforces a timeout using psutil.
    Monitors and records the peak memory usage of the subprocess.
    """
    if not os.path.isfile(solver_path):
        print(f"File not found: {solver_path}")
        return

    command = [solver_path, board_path]
    command.extend(['-ITERATIVE', str(iterative_mode)])
    command.extend(['-ENGINE', engine])
    if steps_num is not None:
        command.extend(['-STEPS', str(steps_num)])

    try:
        # Start the process and enforce a timeout with communicate()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ps_process = psutil.Process(process.pid)  # Get the psutil process object
        peak_memory_usage = 0  # Track peak memory usage

        try:
            # Capture the output and error (if any) from the process with a timeout
            stdout, stderr = process.communicate(timeout=600)
            return_code = process.returncode
        except subprocess.TimeoutExpired:
            print("The command exceeded the timeout of 10 minutes and was terminated.")
            
            # Kill the process and any child processes
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()

            with open(output_file, 'a') as f:
                f.write("\n--- nuXmv Sokoban Solver Results ---\n")
                f.write("nuXmv Solver cannot solve this board in 10 minutes.\n")
                f.write(f"Engine: {engine} Iterative Mode: {iterative_mode} Number of steps: {steps_num}\n")
                f.write(f"Peak Memory Usage: {peak_memory_usage:.2f} MB\n")
            return  # Exit the function

        # Monitor memory while the process is running
        while process.poll() is None:
            try:
                memory_info = ps_process.memory_info()
                memory_used = memory_info.rss / (1024 ** 2)  # Convert bytes to megabytes (MB)
                peak_memory_usage = max(peak_memory_usage, memory_used)

                # Check if the process has child processes and include their memory usage
                for child in ps_process.children(recursive=True):
                    child_memory_info = child.memory_info()
                    child_memory_used = child_memory_info.rss / (1024 ** 2)
                    peak_memory_usage = max(peak_memory_usage, child_memory_used)

                time.sleep(0.1)  # Shorter interval to capture fast changes
            except psutil.NoSuchProcess:
                break  # If the process finishes quickly

        if return_code != 0:
            print(f"Errors from the nuXmv_solver.exe:\n{stderr}")
        else:
            with open(output_file, 'a') as f:
                f.write("\n--- nuXmv Sokoban Solver Results ---\n")
                f.write(stdout if stdout else 'No output received.\n')
                f.write(f"Peak Memory Usage: {peak_memory_usage:.2f} MB\n")
            print(f"Output from the nuXmv_solver.exe:\n{stdout if stdout else 'No output received.'}")
            print(f"Peak Memory Usage: {peak_memory_usage:.2f} MB")

    except Exception as e:
        print(f"Failed to run the nuXmv_solver.exe: {e}")
    

def monitor_memory(ps_process, peak_memory):
    """ Monitors memory usage of the process and updates peak_memory """
    try:
        while ps_process.is_running():
            try:
                memory_info = ps_process.memory_info()
                memory_used = memory_info.rss / (1024 ** 2)  # Convert to MB
                peak_memory[0] = max(peak_memory[0], memory_used)

                # Check child processes
                for child in ps_process.children(recursive=True):
                    child_memory_info = child.memory_info()
                    child_memory_used = child_memory_info.rss / (1024 ** 2)
                    peak_memory[0] = max(peak_memory[0], child_memory_used)

                time.sleep(0.1)  # Check every 100ms
            except psutil.NoSuchProcess:
                break  # Process has terminated
    except Exception as e:
        print(f"Error in memory monitoring: {e}")

def run_fast_nuxMv_solver(solver_path, board_path, output_file, iterative_mode=False, bdd=False,steps=None):
    """
    Runs the nuXmv_solver.exe with the specified parameters directly and enforces a timeout using subprocess.
    """
    print(f"nuXmv iterative mode= {iterative_mode} bdd= {bdd} steps= {steps} ...")
    if not os.path.isfile(solver_path):
        print(f"File not found: {solver_path}")
        return

    command = [solver_path, board_path]
    if iterative_mode:
        command.append('-ITERATIVE')
        command.append('True')
    if bdd:
        command.append('-BDD')
        command.append('True')
    if not steps == None:
        command.append('-STEPS')
        command.append(steps)

    try:
        # Start the process and enforce a timeout with communicate()
        start_time = time.time()  # Start time
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ps_process = psutil.Process(process.pid)  # Get the psutil process object
        peak_memory_usage = [0]  # Use a list to hold peak memory usage (allows modification in a thread)

        # Start memory monitoring in a separate thread
        memory_thread = threading.Thread(target=monitor_memory, args=(ps_process, peak_memory_usage))
        memory_thread.start()

        try:
            # Capture the output and error (if any) from the process with a timeout
            stdout, stderr = process.communicate(timeout=9000)
            return_code = process.returncode
        except subprocess.TimeoutExpired:
            print("The command exceeded the timeout of 1.5 Hour and was terminated.")
            
            # Kill the process and any child processes
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()

            with open(output_file, 'a') as f:
                f.write("\n--- nuXmv Sokoban Solver Results ---\n")
                f.write("nuXmv Solver cannot solve this board in 1.5 Hour.\n")
                f.write(f"BDD: {bdd} Iterative Mode: {iterative_mode} steps:{steps}\n")
                f.write(f"Peak Memory Usage: {peak_memory_usage[0]:.2f} MB\n")
            return  # Exit the function

        memory_thread.join()  # Ensure the memory monitoring thread has finished
        end_time = time.time()  # End time
        elapsed_time = end_time - start_time  # Calculate the elapsed time

        if return_code != 0:
            print(f"Errors from the nuXmv_solver.exe:\n{stderr}")
        else:
            with open(output_file, 'a') as f:
                f.write("\n--- nuXmv Sokoban Solver Results ---\n")
                f.write(stdout if stdout else 'No output received.\n')
                f.write(f"Peak Memory Usage: {peak_memory_usage[0]:.2f} MB\n")
                f.write(f"Running Time: {elapsed_time:.5f} seconds\n")
            print(f"Output from the nuXmv_solver.exe:\n{stdout if stdout else 'No output received.'}")
            print(f"Peak Memory Usage: {peak_memory_usage[0]:.2f} MB")
            print(f"Running Time: {elapsed_time:.5f} seconds")

    except Exception as e:
        print(f"Failed to run the nuXmv_solver.exe: {e}")
    
    
def run_yass_solver(yass_exe_path, board_path, output_file, maxtime=600, optimize="pushes"):
    """
    Runs the YASS.exe solver with the specified parameters and appends the results to the output file.
    Includes time and memory monitoring.
    """
    if not os.path.isfile(yass_exe_path):
        print(f"File not found: {yass_exe_path}")
        return

    if not os.path.isfile(board_path):
        print(f"Puzzle file not found: {board_path}")
        return

    command = f'{yass_exe_path} "{board_path}" -log -maxtime {maxtime} -optimize {optimize} -prompt no'
    print(f"Running command: {command}")

    try:
        simulation_start = time.time()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        ps_process = psutil.Process(process.pid)
        peak_memory_usage = [0]  # Use a list to hold the peak memory usage as a mutable object

        # Monitor memory usage in a separate thread
        monitor_thread = threading.Thread(target=monitor_memory, args=(ps_process, peak_memory_usage))
        monitor_thread.start()

        stdout, stderr = process.communicate()  # Wait for the process to complete
        monitor_thread.join()  # Ensure the memory monitoring thread has completed

        simulation_end = time.time()
        simulation_time = simulation_end - simulation_start

        if process.returncode != 0:
            print(f"Errors from the YASS.exe solver:\n{stderr}")
        else:
            with open(output_file, 'a') as f:
                f.write("\n--- YASS Solver Results ---\n")
                f.write(stdout if stdout else 'No output received.\n')
                yas_result=get_YAS_Results_to_output(board_path)
                f.write(yas_result)
                f.write(f"Simulation Time: {simulation_time:.5f} seconds\n")
                f.write(f"Peak Memory Usage: {peak_memory_usage[0]:.2f} MB\n")

            print(f"Output from the YASS.exe solver:\n{stdout if stdout else 'No output received.'}")
    except Exception as e:
        print(f"Failed to run the YASS.exe solver: {e}")



def get_YAS_Results_to_output(board_path):
    """
    get the content of the log file, which is located in the same directory as board_path,
    to the specified output_file.
    """
    # Determine the log file path
    board_file_name = os.path.basename(board_path)
    board_file_name=os.path.splitext(board_file_name)[0]
    log_file_path = os.path.join(os.path.dirname(board_path), f"{board_file_name}, YASS 2.151 Solutions.sok")

    # Check if the log file exists
    if os.path.isfile(log_file_path):
        # Read the log file and append its content to the output file
        with open(log_file_path, 'r') as log_file:
            log_data=log_file.read()
            if "Solution" in log_data:
                return log_data
            else:
                return("No log File.\nSolution: No Solution, Board not solveable.\n")

    else:
        print(f"Log file not found: {log_file_path}\n")
        return("No log File.\nSolution: No Solution, Board not solveable.\n")

def remove_files_with_pattern(directory, pattern):
    """
    Removes files from the specified directory that contain the given pattern in their name.
    
    :param directory: The directory to search for files.
    :param pattern: The pattern to look for in file names.
    """
    # Create the search pattern
    search_pattern = os.path.join(directory, f"*{pattern}*")

    # Find all files matching the pattern
    files_to_remove = glob.glob(search_pattern)

    # Remove each file
    for file_path in files_to_remove:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Failed to remove {file_path}: {e}")

def runSolvers(board_path,output_file):
    # Paths to the solvers
    solver_takaken_path=os.path.join('exe_files', 'takaken74.exe')# Path to takaken74.exe
    solver_nuXmv_path = os.path.join('exe_files', 'sokoban_nuXmv_2.exe')  # Path to sokoban_solver.exe
    solver_YASS_path =os.path.join('exe_files', 'YASS.exe')# Path to YASS.exe
    solver_nuXmv_deadlock_path = os.path.join('exe_files', 'sokoban_deadlock_justice.exe')  # Path to sokoban_solver.exe

    # Run the takaken solver
    print("Running the takaken74 solver...")
    run_takaken_solver(solver_takaken_path, board_path, output_file, time_limit=600, level_number="1")
    
    # Run the YASS solver and append results to the output file not Optimize moves mode
    print("Running the YASS.exe solver...")
    run_yass_solver(solver_YASS_path, board_path, output_file, maxtime=600)

    # Run the YASS solver and append results to the output file Optimize moves mode
    print("Running the YASS.exe solver...")
    run_yass_solver(solver_YASS_path, board_path, output_file, maxtime=600,optimize="moves")
    
    #nuXmv solver    
    
    # Run the sokoban_nuXmv.exe BMC mode
    #print("Running the sokoban_nuXmv.exe SAT BMC mode...")
    #run_fast_nuxMv_solver(solver_nuXmv_path,board_path , output_file, iterative_mode=False, bdd=True)
    
    # Run the sokoban_nuXmv.exe BMC mode
    print("Running the sokoban_deadlock_justice.exe Deadlocks...")
    run_fast_nuxMv_solver(solver_nuXmv_deadlock_path,board_path , output_file, iterative_mode=False, bdd=True)

    # Run the sokoban_nuXmv.exe BMC mode
    print("Running the sokoban_nuXmv_2.exe  ...")
    run_fast_nuxMv_solver(solver_nuXmv_path,board_path , output_file, iterative_mode=False, bdd=True)

    board_directory=os.path.dirname(board_path)
    remove_files_with_pattern(board_directory,"YASS 2.151")
    remove_files_with_pattern(board_directory,".out")
    remove_files_with_pattern(board_directory,".smv")
    remove_files_with_pattern(board_directory,".log")
    remove_non_solution_folders(board_directory)
    create_summarized_solution_file(output_file)

def runSolversForDirectory(board_directory):
    
    # Define the board directory and solutions directory
    board_path_dir = os.path.join('boards', board_directory)
    solutions_dir = os.path.join(board_path_dir, 'solutions')
    
    # Create the solutions directory if it doesn't exist
    if not os.path.exists(solutions_dir):
        os.makedirs(solutions_dir)
        
    # Iterate over all files in the board directory
    for board_file in os.listdir(board_path_dir):
        # Process only files with .txt extension (you can modify the filter as needed)
        if board_file.endswith('.xsb'):
            board_path = os.path.join(board_path_dir, board_file)

            # Define the output file name and path
            output_file_name = f"{os.path.splitext(board_file)[0]}_output.txt"
            output_file = os.path.join(solutions_dir, output_file_name)

            # Run the solvers for this board file
            runSolvers(board_path, output_file)
    

def remove_non_solution_folders(parent_directory):
    """
    Removes all directories within the specified parent_directory that are not named 'solutions'.
    """
    try:
        # List all entries in the directory
        for entry in os.listdir(parent_directory):
            entry_path = os.path.join(parent_directory, entry)
            
            # Check if it is a directory and not named 'solutions'
            if os.path.isdir(entry_path) and entry.lower() != 'solutions':
                # Remove the folder
                shutil.rmtree(entry_path)
                print(f"Removed folder: {entry_path}")
            elif os.path.isdir(entry_path) and entry.lower() == 'solutions':
                print(f"Skipped folder: {entry_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

def runSolversForSingleBoard(board_directory,board_file):
    board_path=os.path.join('boards',board_directory, board_file)
    # Define the solutions directory
    solutions_dir = os.path.join('boards', board_directory, 'solutions')

    # Create the solutions directory if it doesn't exist
    if not os.path.exists(solutions_dir):
        os.makedirs(solutions_dir)

    # Define the output file name and path
    output_file_name = f"{os.path.splitext(board_file)[0]}_output.txt"
    output_file = os.path.join(solutions_dir, output_file_name)
    runSolvers(board_path,output_file)


def main():
    # Path to the Sokoban board file and output file
    board_directory='simple boards'
    
    #Run Solvers for directory
    runSolversForDirectory(board_directory)
    """
    #Run Solvers for single board
    board_file='board9.xsb'
    runSolversForSingleBoard(board_directory,board_file)
"""

if __name__ == "__main__":
    main()


