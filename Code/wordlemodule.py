import numpy as np
import pandas as pd
from math import ceil
import re
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
import warnings

class WordleData:
    '''
    A class for manipulation of Wordle data and associated meta-data.
    '''
    def __init__(self,myData):
        '''
        Initializes the WordleData object by extracting data from myData, calculating various constants, and converting it to a numpy array.

        Parameters:
        myData (dict): a dictionary of player names, with a second level dictionary of their scores
        '''

        # Extract the int representation from dict
        self.extract_data(myData)

        # Clean names of senders
        self.clean_sender_names()
        
        # Convert dictionary to array of solve scores, with one column per sender
        self.MAX_PUZZ_NUM = self.num_puzzles()
        self.NUM_SENDERS = self.num_senders()
        self.convert_to_arr()



    
    # Class Methods ---------------------------------------

    def extract_data(self, myData):
        '''
        Save the integer representation of the wordle puzzles in its own dict

        Parameters:
        myData (dict): a dictionary of player names, with a second level dictionary of their scores

        Returns:
        self.data_dict (dict): a one-level dictionary of player scores
        '''
        self.data_dict = {}
        for sender in myData:
            self.data_dict[sender] = myData[sender]['0']
    

    def clean_sender_names(self):
        '''
        Opens a text file supplied by the user which specifies 
        names to use instead of email addresses in the data analysis.
        If no names are provided, the email address is used.

        Paramaters:
        name_dir (string): directory of .txt file with names:emails

        Returns:
        self.data_dict (dict): replaced old keys (email addresses) with names 
        '''

        # Create new dictionary to return with cleaned keys
        temp_dict = {}

        # Open user-supplied .txt file with desired names for each email address
        with open('Misc/Email names.txt','r') as file:
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


    def convert_to_arr(self):
        '''
        Save the int representation of puzzle solved score in a new numpy array,
        with each column corresponding to a sender

        Parameters:
        self.data_dict (dict): dictionary of player scores
        self.MAX_PUZZ_NUM (int): the highest numbered puzzle solved by any player
        self.NUM_SENDERS(int): the number of players

        Returns:
        self.data_arr (numpy arr): row index corresponds to puzzle number, columns
                                    correspond to players, values are solve scores 
        '''

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
        '''Calculate the number of players for which data is available'''
        num_senders = len(self.data_dict)
        return num_senders
    
    # Find how many puzzles are in the array
    '''Calculate the highest number puzzle solved by any player'''
    def num_puzzles(self):
        max_puzz_num = 0
        for sender in self.data_dict:
            curr_arr = self.data_dict[sender]
            curr_len = np.shape(curr_arr)[2]

            if curr_len > max_puzz_num:
                max_puzz_num = curr_len

        return max_puzz_num


    def weekly(self):
        '''
        This function uses the array of solve scores from each player to create
        a pandas dataframe, and adds an extra column to track day of the week.

        Returns:
        df_weekly_sum (dataframe): number of puzzles completed by each player for each day of the week
        df_weekly_score (dataframe): mean solve score for each player for each day of the week
        df_weekly_score_sem (dataframe): standard error of the mean
        '''
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
        df_weekly_score_sem = pd.DataFrame()

        for mykey in self.data_dict.keys():
            df_weekly_sum[mykey] = df[[mykey,'Day of the week']].dropna().groupby('Day of the week',sort=False).size()

            # Replace scores of 7 (failed wordle) with Nan, which will be ignored in calculating mean
            df_weekly_score[mykey] = df[[mykey,'Day of the week']].replace([7], np.nan).dropna().groupby('Day of the week',sort=False).mean()
            df_weekly_score_sem[mykey] = df[[mykey,'Day of the week']].replace([7], np.nan).dropna().groupby('Day of the week',sort=False).sem()

        # Reorder the dataframe Sun->Sat
        df_weekly_sum = df_weekly_sum.reindex(days,level='Day of the week')
        df_weekly_score = df_weekly_score.reindex(days,level='Day of the week')
        df_weekly_score_sem = df_weekly_score_sem.reindex(days,level='Day of the week')
        
        return df_weekly_sum, df_weekly_score, df_weekly_score_sem
    
    def rolling(self, mywindow):
        '''
        Calculates the rolling average solve score for each player

        Parameters:
        mywindow (int): the window size for the rolling average
        
        Returns:
        df_rolled (dataframe): the self.data_arr array, rolled
        '''
        # Create dataframe
        df = pd.DataFrame(self.data_arr, columns=self.data_dict.keys())
        df_rolled = pd.DataFrame(np.nan, index=df.index, columns=df.columns)


        # Each df column has different numbers of NA when they didn't complete the puzzle,
        # so in order to calculate the rolling average without including NA, 
        # go through each column individually and join them together afterward
        for mykey in df:
            data_to_roll = df[mykey].dropna()

            if data_to_roll.size <= mywindow:
                #warning
                warnings.warn(f'{mykey} only has {data_to_roll.size} values, which is not enough to calculate using a sliding widow size of {mywindow}')
                continue

            df_rolled[mykey] = data_to_roll.rolling(mywindow).mean().reindex(df.index, method='backfill')

        return df_rolled
    
    def corr_pvals(self):
        '''Calculates pearson's r-squared and p-values comparing each player to each other'''
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
    
    def as_df(self):
        '''Returns the score of the puzzles as a dataframe with a puzzle number column'''
        df = pd.DataFrame(self.data_arr, columns=self.data_dict.keys())
        df['Puzzle Number'] = df.index
        return df
    

    def linear_reg(self):
        '''Returns the data as a dataframe, but each score is replaced by the regression prediction'''
        df = self.as_df()
        df_predicted = pd.DataFrame(np.nan, index=df.index, columns=df.columns.drop('Puzzle Number'))

        for sender in df_predicted:

            # Save a dataframe without nan's
            df_no_na = df[[sender, 'Puzzle Number']].dropna()

            # Create and fit linear regression
            regressor = LinearRegression()
            y = df_no_na[[sender]]
            X = df_no_na[['Puzzle Number']]
            regressor.fit(X.values, y)

            # Use the regression to predict scores for all puzzles from this sender
            puzzle_range = np.arange(X.min().min(),X.max().max())
            temp = pd.DataFrame(regressor.predict(puzzle_range.reshape(-1,1)), columns=['Scores'], index=puzzle_range)
            df_predicted.loc[puzzle_range,sender] = temp['Scores']
        
        return df_predicted
    
    def stats(self):
        '''Calculates various general statistics (mean scores, std dev, etc) for each player'''
        # Create dataframe and empty df for storing values
        df = self.as_df().drop('Puzzle Number',axis=1)
        results = pd.DataFrame({'Person':df.columns,
                                'Mean solve score': np.nan,
                                'Solve score standard deviation': np.nan,
                                'Best solve score': np.nan,
                                'Puzzles attempted': np.nan,
                                'Puzzles not attempted': np.nan,
                                'Longest not attempted puzzle streak': np.nan,
                                'Longest attempted puzzle streak': np.nan,
                                'Mean days between puzzles': np.nan
                                })
        


        for person in df:
            # Drop nan or guesses
            df_dropna = df[person].dropna().index.to_numpy()
            df_dropguess = df[person].drop(df_dropna).index.to_numpy()
            
            # Person's row in results for storing results
            row = results['Person'] == person

            # Calculate number of puzzles not attempted within the period of time
            # that the person was submitting guesses
            results.loc[row,'Puzzles not attempted'] = df.loc[df_dropna.min():df_dropna.max(),person].isna().sum()

            # Calculate num of puzzles attempted
            results.loc[row, 'Puzzles attempted'] = df_dropna.size

            # Calculate longest not attempted streak
            diff_indices_dropna = df_dropna[1:] - df_dropna[:-1]
            results.loc[row, 'Longest not attempted puzzle streak'] = diff_indices_dropna.max()

            # Calculate longest attempted streak
            diff_indices_dropguess = df_dropguess[1:] - df_dropguess[:-1]
            results.loc[row, 'Longest attempted puzzle streak'] = diff_indices_dropguess.max()

            # Calculate best score
            results.loc[row, 'Best solve score'] = df[person].min()

            # Calculate solve score std dev
            results.loc[row, 'Solve score standard deviation'] = df[person].std()

            # Calculate mean solve score
            results.loc[row, 'Mean solve score'] = df[person].mean()

            # Calculate mean days between puzzles
            results.loc[row, 'Mean days between puzzles'] = diff_indices_dropna.mean()

        # Set dataframe properties
        results.set_index('Person', inplace=True)
        results['Best solve score'] = results['Best solve score'].map(int)
        results['Longest not attempted puzzle streak'] = results['Longest not attempted puzzle streak'].map(int)
        results['Longest attempted puzzle streak'] = results['Longest attempted puzzle streak'].map(int)
        results['Puzzles not attempted'] = results['Puzzles not attempted'].map(int)
        results['Puzzles attempted'] = results['Puzzles attempted'].astype(int)

        return results
    
    def puzz_avg(self):
        '''
        Calculates the mean int value for each position in the 5x6 puzzle grid
        across all puzzles and all players
        '''
        # Get data in dict format, and the puzzle solve score as well
        data = self.data_dict
        score = self.data_arr



        # Create empty dict to hold results and array to hold avg for each person
        results = {}
        accum = np.empty([6,5,data.keys().__len__()])
        
        # Find average across all puzzles for each person
        for i, person in enumerate(data):
            # Reduce all puzzle guesses to only puzzles attempted
            indeces_attempted = ~np.isnan(score[:,i])
            person_all_puzzles = data[person]
            person_attempted_puzzles = person_all_puzzles[:,:,indeces_attempted]

            # Replace 0s (which means no guess) with nan so it's not included in the mean
            indeces_letter_guessed = person_attempted_puzzles > 0
            person_attempted_puzzles_nan = np.where(person_attempted_puzzles == 0, np.nan, person_attempted_puzzles)

            # Find average for puzzles attempted
            person_avg= np.nanmean(person_attempted_puzzles_nan,axis=2)

            # Save results (with nan) in accum
            accum[:,:,i] = person_avg

            # Change nan to 0s for final results returned and save
            results[person] = np.nan_to_num(person_avg,copy=False)



        # Find average across all puzzles for all persons
        results['Average'] = np.nanmean(accum,axis=2)
        results['Average'] = np.nan_to_num(results['Average'],copy=False)
        

        return results
    
    def letter_patterns(self):
        '''
        Calculates the most frequent patterns of guess results for each of the 6 rows.

        Returns:
        results: the patterns of the most frequent results per row
        results_freq: the frequency (percentage) of each result, excluding the all 0s result
        '''
        # Create results variable to hold output of function, which will be a 6x5 array
        # for each of the 6 guess rows of the puzzle, containing the top most commonly
        # guessed patterns for that row
        results = np.empty([6,5,6])
        results_freq = np.empty([6,1,6])

        # Get data in dict format
        data = self.data_dict

        # Change to numpy array and concatenate all puzzle guesses
        arr = np.empty([6,5,self.MAX_PUZZ_NUM*self.NUM_SENDERS])

        for i,sender in enumerate(data):
            arr_range = range(self.MAX_PUZZ_NUM * i, self.MAX_PUZZ_NUM * (i+1))
            arr[:,:,arr_range] = data[sender]

        # For each guess row, count unique patterns
        for i in range(6):

            # Find unique patterns and their frequencies
            unique, unique_counts = np.unique(arr[i,:,:], axis=1, return_counts=True)

            # Remove the unique row where there are no guesses (6 0s in a row)
            idx_no_guesses = np.where(sum(unique) == 0)[0]
            unique = np.delete(unique,idx_no_guesses, axis=1)
            unique_counts = np.delete(unique_counts,idx_no_guesses)
            
            # Sort unique by frequency of unique_counts
            sorted_count_ind = np.argsort(-unique_counts)

            # Save the top 6 patterns
            results[:,:,i] = unique[:,sorted_count_ind[0:6]].T

            # Save the frequency of each pattern
            results_freq[:,0,i] = unique_counts[sorted_count_ind[0:6]] / np.sum(unique_counts)

        return results, results_freq
    
def int_to_char(input,freq=None):
    '''
    Converts unicode character codes to characters
    
    Parameters:
    input: ndarray of numerical unicode values
    freq: (optional) array same length as input with frequencies, which will
            format and output frequencies as percentages

    Returns:
    ndarray of characters where
    0 = space filler for unused guesses = 9744
    1 = gray box (wrong letter, not in word) = 11036
    2 = yellow box (wrong letter, but is in word) = 129000
    3 = green box (right letter) = 129001

    '''

    # Cast input as int and flatten
    int_arr = np.int32(input.flatten())

    # Replace ints with unicode char codes
    int_arr[int_arr==0] = 9744
    int_arr[int_arr==1] = 11036
    int_arr[int_arr==2] = 129000
    int_arr[int_arr==3] = 129001

    # Create char array using unicode char codes
    '''
    my_str = np.array2string(int_arr,
                           max_line_width=7,
                           formatter={'int':lambda x: chr(x)},
                           separator='')
    my_str = my_str.replace("[","").replace("]","").replace(" ","")   #get rid of brackets and spaces
    '''
    
    # Create char array using unicode char codes
    chr_ar = [chr(code) for code in int_arr]

    # Insert newline characters at every 6th position
    for count,listpos in enumerate(range(0,len(chr_ar),5)):
        if listpos==0:
            continue
        if listpos>0 and listpos % 5 == 0:
            chr_ar.insert(listpos+count-1,'\n')
    
    # Insert frequencies after '\n' if a freq var is passed 0 7 14
    if freq is not None:
        for count,currfreq in enumerate(freq):
            insertion = '%'+ "{:.2f}".format((currfreq[0]*100))
            if count == 0:
                chr_ar.insert(0,insertion)
            if count > 0:
                idx = chr_ar.index('\n',(count-1)*7) + 1
                chr_ar.insert(idx,insertion)
    
    # Join chars together
    #print("".join(chr_ar))
    return "".join(chr_ar)
        