import numpy as np
import pandas as pd
from math import ceil
import re
from scipy.stats import pearsonr

class WordleData:
    def __init__(self,myData):

        # Extract the int representation from dict
        self.extract_data(myData)

        # Clean names of senders
        self.clean_sender_names()
        
        # Convert dictionary to array, with one column per sender
        self.MAX_PUZZ_NUM = self.num_puzzles()
        self.NUM_SENDERS = self.num_senders()
        self.convert_to_arr()



    
    # Class Methods ---------------------------------------

    # Save the integer representation of the wordle puzzles in its own dict
    def extract_data(self, myData):
        self.data_dict = {}
        for sender in myData:
            self.data_dict[sender] = myData[sender]['0']
    
    # Clean names opens a text file supplied by the user which specifies 
    # people's names to use instead of email addresses in the data analysis
    def clean_sender_names(self):

        # Create new dictionary to return with cleaned keys
        temp_dict = {}

        # Open user-supplied .txt file with desired names for each email address
        with open('Misc/email names.txt','r') as file:
            user_supplied_email_names = {}
            for line in file:
                user_supplied_e_address = re.search('.*:',line.rstrip())
                user_supplied_name = re.search(':.*',line.rstrip())
                user_supplied_email_names[user_supplied_e_address.group()[0:-1]] = user_supplied_name.group()[1:]

        # For each sender, get their email address and replace it with user-chosen name.
        # If no user supplied name exists, the email address is used
        for old_key in self.data_dict:

            # Extract email address from old key
            email_address = re.search('<(.*)>',old_key)
            if email_address == None:
                email_address = old_key
            else:
                email_address = email_address.group()
                email_address = email_address[1:len(email_address)-1]

            # If user supplied name, then replace the old key with the user_supplied_email_names
            if email_address in user_supplied_email_names:
                name = user_supplied_email_names[email_address]
            else:
                name = email_address
            
            # Copy Wordle score information from old dictionary to new one
            temp_dict[name] = self.data_dict[old_key]
        self.data_dict = temp_dict

    # Save the int representation of puzzle solved score in its own array,
    # with each column corresponding to a sender
    def convert_to_arr(self):

        #self.data_arr = np.zeros([self.MAX_PUZZ_NUM, self.NUM_SENDERS])

        # Create an array of not a number, which will store puzzle solve scores
        self.data_arr = np.full([self.MAX_PUZZ_NUM, self.NUM_SENDERS], np.nan)

        for idx, sender in enumerate(self.data_dict):
            # Sum across all rows
            all_puzzles_arr_rowsum = np.sum(self.data_dict[sender], axis=1)

            # If the sum across all rows is 0, then the puzzle was not attempted,
            # and the value will remain as nan
            puzzle_not_attempted = np.sum(all_puzzles_arr_rowsum, axis=0) == 0

            # If the sum across all rows is 3*5=15, puzzle is solved at that row
            # puzzle_solved_row is an array of [row of solving, puzzle number]
            puzzle_solved_row = np.argwhere(all_puzzles_arr_rowsum == 15)
            puzzle_solved_row[:,0] += 1     #convert 0-based array to 1-based wordle row

            # Store puzzle solved row in col per sender
            cols = puzzle_solved_row[:,1]
            self.data_arr[cols,idx] = puzzle_solved_row[:,0]

            # If was attempted but not solved, then assign row=7
            idx_puzz_solved = ~np.isnan(self.data_arr[:,idx])
            attempted_not_solved = ~puzzle_not_attempted & ~idx_puzz_solved
            self.data_arr[attempted_not_solved,idx] = 7

        return self.data_arr
         
    def num_senders(self):
        num_senders = len(self.data_dict)
        return num_senders
    
    # Find how many puzzles are in the array
    def num_puzzles(self):
        max_puzz_num = 0
        for sender in self.data_dict:
            curr_arr = self.data_dict[sender]
            curr_len = np.shape(curr_arr)[2]

            if curr_len > max_puzz_num:
                max_puzz_num = curr_len

        return max_puzz_num

    # Make pandas dataframe with days of the week to match array of guesses
    def weekly(self):
        # Create dataframe
        df = pd.DataFrame(self.data_arr, columns=self.data_dict.keys())

        # Find puzzle number of known day of the week
        # Puzzle # 0 --> Saturday, 19 June 2021
        days = ['Saturday',
                'Sunday',
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday']
        days_repeated = days*ceil((len(self.data_arr)/7))
        days_forpd = days_repeated[0:len(self.data_arr)]

        # Add days to dataframe
        df['Day of the week'] = days_forpd

        # Calculate how many puzzles were solved each day of the week
        df_weekly_sum = pd.DataFrame()
        df_weekly_score = pd.DataFrame()

        for mykey in self.data_dict.keys():
            df_weekly_sum[mykey] = df[[mykey,'Day of the week']].dropna().groupby('Day of the week',sort=False).size()

            # Replace scores of 7 (failed wordle) with Nan, which will be ignored in calculating mean
            df_weekly_score[mykey] = df[[mykey,'Day of the week']].replace([7], np.nan).dropna().groupby('Day of the week',sort=False).mean()

        #pd.DataFrame.reindex()
        df_weekly_sum = df_weekly_sum.reindex(days,level='Day of the week')
        df_weekly_score = df_weekly_score.reindex(days,level='Day of the week')
        return df_weekly_sum, df_weekly_score
    
    def rolling(self, mywindow):
        # Create dataframe
        df = pd.DataFrame(self.data_arr, columns=self.data_dict.keys())
        df2 = pd.DataFrame()


        # Each df column has different numbers of NA when they didn't complete the puzzle,
        # so in order to calculate the rolling average without including NA, 
        # go through each column individually and join them together afterward
        for mykey in df:
            df2[mykey] = df[mykey].dropna().rolling(mywindow).mean().reindex(df.index, method='pad')

        # Create column to track puzzle number
        #df.insert(0,'Puzzle Number',range(self.MAX_PUZZ_NUM), False) 

        #df2 = df['Doug'].dropna().rolling(mywindow).mean().reindex(df.index, method='pad')
        #df2 = df['Doug'].rolling(window=mywindow).mean()

        return df2
    
    def corr_pvals(self):
        df = pd.DataFrame(self.data_arr, columns=self.data_dict.keys())

        df_rsq = pd.DataFrame() # Correlation matrix
        df_p = pd.DataFrame()  # Matrix of p-values

        for idx1,col1 in enumerate(df):
            for idx2,col2 in enumerate(df):
                temp = df[[col1, col2]].dropna()
                corr = pearsonr(temp[col1], temp[col2])
                df_rsq.loc[idx1,idx2] = np.power(corr[0],2)
                df_p.loc[idx1,idx2] = corr[1]
        
        return df_rsq, df_p