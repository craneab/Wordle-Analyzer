# This script converts Wordle results to integer representation for downstream analysis

# Import necessary libraries
import json
import numpy as np
import pickle

# Load imported emails
with open('Data/Script data/Imported_email_data.json', 'r') as file:
    input_data_dict = json.load(file)

# Def function to find the highest puzzle number completed
def max_puzzle_num(input_data_dict):

    # Collect puzzle numbers (1st level dict keys) in list
    puzzle_nums_list = set().union(*input_data_dict.values())

    # Calculate and return max puzzle number
    max_puzzle_num_int = int(max(puzzle_nums_list))
    return max_puzzle_num_int


# Def function to convert each imported email to int representation
def convert_emails_to_int(input_data_dict):


    # Loop through each sender email address in the data
    for sender in input_data_dict:

        # Create array of zeros to hold results
        wordle_int_arr = np.zeros([6,5,max_puzzle_num(input_data_dict)+1], dtype='uint8')

        # For each wordle_puzz puzzle, turn str into int
        for wordle_puzz in input_data_dict[sender]:

            # This wordle_puzz's guesses
            guesses = input_data_dict[sender][wordle_puzz]
            print(guesses)

            # Create array of zeros to hold guesses
            guesses_int = np.zeros(30)


            # Convert wordle_puzz guesses to int
            # 0 = space filler for unused guesses
            # 1 = gray box (wrong letter, not in word) 11036
            # 2 = yellow box (wrong letter, but is in word) 129000
            # 3 = green box (right letter) 129001

            guess_idx = 0 #keeps track of how many true guesses (not newline chars, for ex) have been converted to ints
            for guess in guesses:
                guess_int = ord(guess)
                match guess_int:
                    case 11036:
                        guesses_int[guess_idx] = 1
                        guess_idx += 1
                    case 129000:
                        guesses_int[guess_idx] = 2
                        guess_idx += 1
                    case 129001:
                        guesses_int[guess_idx] = 3
                        guess_idx += 1



            # Reshape the array to the common wordle_puzz box shape
            guesses_int = guesses_int.astype(np.uint8).reshape(6,5)

            # Save int representation into 3-d array
            wordle_int_arr[:,:,int(wordle_puzz)] = guesses_int

            print("guesses_int: \n\n",guesses_int)

        # Save int representation into dictionary with key "puzzle_as_int"
        input_data_dict[sender]['0'] = wordle_int_arr

convert_emails_to_int(input_data_dict)


# Save int representations as pickle file
with open('Data/Script data/Imported_email_data_with_ints.pkl','wb') as file:
    pickle.dump(input_data_dict, file)