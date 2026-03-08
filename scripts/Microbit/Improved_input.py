def improved_input(prompt, list_ans, ans_type):
    
    while True:
        ans = input(prompt).lower()
        
        if ans_type is not None:
            if ans_type == "int":
                try:
                    ans = int(ans)
                except:
                    print("Please enter an integer")
                    continue
            elif ans_type == "float":
                try:
                    ans = float(ans)
                except:
                    print("Please enter a number")
                    continue
                
        if list_ans is not None:
            if ans not in list_ans:
                print("Input not valid, try again")
                continue
        
        return ans