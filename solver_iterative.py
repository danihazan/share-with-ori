import os
import time
import run_nuxmv
import model_generation
import board_assignment
import LURD_format_creator

def save_model_to_file(model_content, filename):
    with open(filename, 'w') as f:
        f.write(model_content)


def run_and_file_creation(board, input_file_name, folder_name, model_content, start_time, solver_engine, steps=None):
    smv_filename = os.path.join(folder_name, input_file_name.split(".")[0]+".smv")
    save_model_to_file(model_content, smv_filename) # save contents of code to .smv file
    _, stdout = run_nuxmv.run_nuxmv(input_file_name, folder_name, smv_filename, solver_engine, steps) # run nuXmv file 
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time: ", execution_time, "seconds")
    
    LURD_file_name, LURD_format=  LURD_format_creator.extract_LURD(stdout, input_file_name, folder_name, steps, "iterative") # create correct LURD format
    
    with open(LURD_file_name, "a") as f:
        if LURD_format!=None:
            f.write("Solution : ")
            f.write(LURD_format+f"\n")
        f.write("Execution time : ")
        f.write(str(execution_time))
        f.write(f" seconds\n")
        
    return stdout, LURD_format




def main(board, input_filename, solver_engine, steps=None):
    total_start_time=time.time()
    
    folder_name = os.path.join("./outputs", input_filename.split(".")[0]+"_iterative") # creates a folder for all the outputs inside ./outputs
    os.makedirs(folder_name, exist_ok=True)
    
    LURD_output_filename = os.path.join(folder_name, input_filename.split(".")[0]+"_LURD.out")
    with open(LURD_output_filename, "w") as f:
        pass  # clears file

    lines_num = board.strip().split('\n')
    rows = len(lines_num)
    columns= len(lines_num[0])

    worker_holder, original_board = board_assignment.assign_board(board)
    
    def manhattan_distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    goal_indices = [(i, j) for i, row in enumerate(original_board) for j, char in enumerate(row) if char == '.'] # sorts the distances for the iterative approach
    sorted_goal_indices = sorted(goal_indices, key=lambda index: manhattan_distance(worker_holder, index))
    
    
    new_board = [row[:] for row in original_board] # shallow copy
    
    # iterative run, for every goal at a time
    passed_indices = []
    for count, goal_index in enumerate(reversed(sorted_goal_indices)):
        start_time=time.time()
        print(f"solving for box number {str(count+1)} :")
        for i in range(rows):
            for j in range(columns):
                cur_index = (i,j)
                if original_board[i][j]=='.' and cur_index in passed_indices: # already done, make it x
                    new_board[i][j]='x'
                
                elif original_board[i][j]=='.' and (goal_index[0]!=i or goal_index[1]!=j):
                    new_board[i][j]='_'

        # finished creating board, create nusmv file and run it
        model_content = model_generation.generate_nusmv_model(rows, columns, new_board, worker_holder) # create nusmv code
        stdout, LURD = run_and_file_creation(new_board, input_filename, folder_name, model_content, start_time, solver_engine, steps=None)
            
        if LURD==None: # not solveable
            break
    
        # return board to original form, return the goals
        for i in range(rows):
            for j in range(columns):
                if original_board[i][j]=='.' and new_board[i][j]=='_':
                    new_board[i][j]='.'


        # filling the board after reaching a goal
        new_board=extract_new_board_formation(stdout, rows, columns, new_board)

        # updating the worker position to the new location, after he reached the goal
        last_move=LURD[-1].lower()     
        if last_move=='u':
            worker_holder[0]=goal_index[0]+1
            worker_holder[1]=goal_index[1]
        elif last_move=='d':
            worker_holder[0]=goal_index[0]-1
            worker_holder[1]=goal_index[1]
        elif last_move=='l':
            worker_holder[0]=goal_index[0]
            worker_holder[1]=goal_index[1]+1
        elif last_move=='r':
            worker_holder[0]=goal_index[0]
            worker_holder[1]=goal_index[1]-1
        
        passed_indices.append(goal_index)
        
    end_time = time.time()
    total_time = end_time - total_start_time
    print(f"Total Time : {total_time} seconds\n")
    with open(LURD_output_filename, "a") as f:
        f.write(f"\nTotal Time : {total_time} seconds\n")



# creates the new board, after a goal has been reached
def extract_new_board_formation(stdout, rows, columns, new_board):
    lines = stdout.split('\n')
    boolean_board = [[None for _ in range(columns)] for _ in range(rows)] # 2d array
    
    reach_count = 0
    reach_index = -1
    for line in lines[reach_index + 2:]:
        if "board" in line:
            parts = line.split()
            indices = parts[0][6:-1].split('][')
            i = int(indices[0])
            j = int(indices[1])
            value = parts[-1]
            boolean_board[i][j]=value
        if "reach = " in line:
            reach_count += 1
            if reach_count == 2:  # second reach occurrence
                break

    # creates a wall in the place of an already reached goal
    for i in range(rows):
        for j in range(columns):
            if new_board[i][j]=='.' and boolean_board[i][j]=="TRUE":
                new_board[i][j]='x'
            elif new_board[i][j]=='b' and boolean_board[i][j]=="FALSE":
                new_board[i][j]='_'
            elif boolean_board[i][j]=="TRUE":
                new_board[i][j]='b'
        
    return new_board


if __name__=="__main__":
    main()


