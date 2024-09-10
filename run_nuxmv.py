import os
import subprocess

# solves using BDD or SAT engine, according to input
def run_nuxmv(input_file_name, folder_name, smv_file_name, solver_engine, steps = None):
    if solver_engine == "BDD":
        nuxmvProcess = subprocess.Popen(["nuXmv.exe", "-int", smv_file_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True,  stderr=subprocess.DEVNULL)
        nuxmvProcess.stdin.write("go\n")
        nuxmvProcess.stdin.write("check_ltlspec\n")
        nuxmvProcess.stdin.write("quit\n")
    elif solver_engine == "SAT":
        nuxmvProcess = subprocess.Popen(["nuXmv.exe", "-int", smv_file_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True,  stderr=subprocess.DEVNULL)
        nuxmvProcess.stdin.write("go_bmc\n")
        if steps == None:
            nuxmvProcess.stdin.write(f"check_ltlspec_bmc\n")
        else:
            nuxmvProcess.stdin.write(f"check_ltlspec_bmc -k {steps}\n")
        nuxmvProcess.stdin.write("quit\n")
    else:
        nuxmvProcess = subprocess.Popen(["nuXmv.exe", smv_file_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.DEVNULL)
    
    
    output_filename = os.path.join(folder_name, input_file_name+".out")
    stdout, _ = nuxmvProcess.communicate()
    with open(output_filename, "w") as f:
        f.write(stdout)
    return output_filename, stdout
