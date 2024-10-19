import pickle
import numpy as np
import matplotlib.pyplot as plt

# Open pickle file
with open('Data/Script data/Imported_email_data_with_ints.pkl','rb') as file:
    data = pickle.load(file)

# Split the data into the number of senders
num_senders = len(data)

# Set up variables to store plotting values
puzzle_solved_row = {}
overall_mean = {}

# Run calculations
for sender in data:

    # Get array of integers
    all_puzzles_arr = data[sender]['0']

    # Sum across all rows
    all_puzzles_arr_rowsum = np.sum(all_puzzles_arr, axis=1)

    # Find row at which puzzle is solved (all 3s, rowsum=3*5=15)
    puzzle_solved_row[sender] = np.argwhere(all_puzzles_arr_rowsum == 15)

    # Calculate average solve row
    overall_mean[sender] = np.mean(puzzle_solved_row[sender][:,0],axis=0)

# Plot barchart for average solve score
fig, ax = plt.subplots()

x = overall_mean.keys()
y = overall_mean.values()
bar_colors = ['tab:red', 'tab:blue']

ax.bar(x, y, color=bar_colors)

ax.set_ylabel('Mean Wordle solve score')
ax.set_title('Mean Wordle solve score')

plt.show()

# Plot scatterplot for solve score over time