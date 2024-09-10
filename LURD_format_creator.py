# extracts the LURD format from the nuxmv .out file
import os

def extract_LURD(stdout, input_file_name, folder_name, steps, iterative_check=None):
    # check if not solveable
    last_line = stdout.strip().split('\n')[-2]
    
    output_filename = os.path.join(folder_name, input_file_name+"_LURD.out")
    # check for SAT with a bound on steps
    if steps!=None:
        check_test = "-- no counterexample found with bound "+steps
    else:
        check_test = "-- no counterexample found with bound 10"
        if check_test in last_line:
            print("The board is not solveable")
            with open(output_filename, "w") as f:
                f.write("Board is not solveable")
                f.write(f"\n")
            return output_filename, None
        
    lines = stdout.split('\n')

    for line in lines:
        if "-- specification  G !reach  is true" in line:
            print("The board is not solveable")
            with open(output_filename, "w") as f:
                f.write("Board is not solveable")
                f.write(f"\n")
            return output_filename, None


    current_index=-1
    size=0
    # setting list size
    for line in lines:
        if 'Loop' in line:
            break
        elif '-> State:' in line:
            size+=1
            
    movements_pushes_list = [["N/A"] * size for i in range(2)] # 2d list of size 2xsize

    # filling list with movements and pushes
    for line in lines:
        if 'Loop' in line:
            break
        if '-> State:' in line:
            current_index+=1
        elif 'movement = ' in line:
            movement = line.split('=')[1].strip()
            movements_pushes_list[0][current_index]=movement
            
        elif '_push' in line:
            direction = line.split('_')[0].strip()[0]
            value = line.split('=')[1].strip()
            # adds the direction as an upper letter if push=TRUE, and as lower letter if push=FALSE
            if movements_pushes_list[1][current_index]=="N/A": 
              if value=="TRUE":
                movements_pushes_list[1][current_index]=direction.upper()
              else:
                movements_pushes_list[1][current_index]=direction
            else:
              if value=="TRUE":
                movements_pushes_list[1][current_index]+=direction.upper()
              else:
                movements_pushes_list[1][current_index]+=direction


    # filling N/A movements
    for i in range(len(movements_pushes_list[0])):
        if movements_pushes_list[0][i]=="N/A":
            movements_pushes_list[0][i]=movements_pushes_list[0][i-1]

    # filling pushes
    directions = ['u', 'd', 'l', 'r']
    for i in range(len(movements_pushes_list[1])):
        if movements_pushes_list[1][i]=="N/A":
            movements_pushes_list[1][i]=movements_pushes_list[1][i-1]
        for dir in directions: # will add pushes if they existed beforehand, if the lowercase letter isnt present
          if dir.upper() in movements_pushes_list[1][i-1] and  dir.upper() not in movements_pushes_list[1][i] and dir not in movements_pushes_list[1][i]:
            movements_pushes_list[1][i]+=dir.upper()
  
    # comparing the 2 lists, changing to upper case if needed:
    for i in range(len(movements_pushes_list[0])):
      # if the uppercase letter is in the list, and the lowercase letter isnt in the list
        if ((movements_pushes_list[0][i].upper() in movements_pushes_list[1][i]) and (movements_pushes_list[0][i] not in movements_pushes_list[1][i])):
            movements_pushes_list[0][i]=movements_pushes_list[0][i].upper()
            
    if movements_pushes_list and len(movements_pushes_list[0]) > 1:
        # cut useless movements from start and end
        movements_pushes_list[0] = movements_pushes_list[0][1:]
        if iterative_check=="iterative" and movements_pushes_list[0][-1].islower():
                movements_pushes_list[0]=movements_pushes_list[0][:-1]
        elif iterative_check!="iterative" and movements_pushes_list[0][-1].islower():
                movements_pushes_list[0]=movements_pushes_list[0][:-1]

    
    LURD_format = "".join(movements_pushes_list[0]) # convert list to string
    print("The board is solveable. Solution:")
    print(LURD_format)
    
    return output_filename, LURD_format