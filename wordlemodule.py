import numpy as np

class WordleData:
    def __init__(self,myData):

        # Extract the int representation from dict
        self.extract_data(myData)
        
        # Convert dictionary to array, with one column per sender
        self.MAX_PUZZ_NUM = self.num_puzzles()
        self.NUM_SENDERS = self.num_senders()
        self.convert_to_arr()



    
    # Class Initialization Methods ---------------------------------------

    # Save the integer representation of the wordle puzzles in its own dict
    def extract_data(self, myData):
        self.data_dict = {}
        for sender in myData:
            self.data_dict[sender] = myData[sender]['0']
    
    # Find how many puzzles are in the array
    def num_puzzles(self):
        max_puzz_num = 0
        for sender in self.data_dict:
            curr_arr = self.data_dict[sender]
            curr_len = np.shape(curr_arr)[2]

            if curr_len > max_puzz_num:
                max_puzz_num = curr_len

        return max_puzz_num
        
    # Save the int representation of puzzles in its own array,
    # with each column corresponding to a sender
    def convert_to_arr(self):

        self.data_arr = np.zeros([self.MAX_PUZZ_NUM, self.NUM_SENDERS])

        for idx, sender in enumerate(self.data_dict):
            # Sum across all rows
            all_puzzles_arr_rowsum = np.sum(self.data_dict[sender], axis=1)

            # Find row at which puzzle is solved (all 3s, rowsum=3*5=15)
            puzzle_solved_row = np.argwhere(all_puzzles_arr_rowsum == 15)
            # Store puzzle solved row in col per sender
            cols = puzzle_solved_row[:,1]
            self.data_arr[cols,idx] = puzzle_solved_row[:,0]

            # If there is no row == 15, then assign row=7 to indicate puzzle was attempted but not solved
            idx_unsolved = puzzle_solved_row[:,0] == 0
            self.data_arr[puzzle_solved_row[idx_unsolved,1],idx] = 7

        return self.data_arr
         

    # Class Methods  -----------------------------------------------------
    def num_senders(self):
        num_senders = len(self.data_dict)
        return num_senders

# Explicit functions