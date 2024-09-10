import argparse
import sys
import solver
import solver_iterative

 # reads file content
def get_board(filename):
    try:
        with open(filename, 'r') as file:
            contents = file.read()
            return contents
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

#ARG [0]=Input Board
#Arg[1]
def main(board_path='boards/board4.txt',iterative = False , check_bdd = False ,steps=None):    

    file_contents = get_board(board_path) # reads file content
    if file_contents:
        print("INPUT BOARD : ")
        print(file_contents)
    if(check_bdd == True):
        solver_engine='BDD'
    else:
        solver_engine='SAT'
    if(iterative== True):
        solver_engine=="iterative"
    solver.main(file_contents, board_path, solver_engine, steps) # default
    


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Sokoban Solver")

    # Required positional argument for the board path
    parser.add_argument('board_path', type=str, help='Path to the board file')

    # Optional arguments with enforced choices
    parser.add_argument('-ITERATIVE', '--iterative_mode', type=str, choices=['True', 'False'], default='False', help='Enable iterative mode (true or false)')
    parser.add_argument('-BDD', '--bdd', type=str, choices=['True', 'False'], default='False', help='Run BDD engine (true or false)')
    parser.add_argument('-STEPS', '--steps', type=int, default=None, help='Number of steps (integer value)')

    args = parser.parse_args()

    # Convert 'true'/'false' string to a boolean
    iterative_mode = args.iterative_mode.lower() == 'true'
    # Convert 'true'/'false' string to a boolean
    bdd = args.bdd.lower() == 'true'
    steps=args.steps
    # Call main with the parsed arguments
    main(args.board_path, iterative_mode, bdd,steps)
