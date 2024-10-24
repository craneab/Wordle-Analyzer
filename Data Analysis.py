import pickle
import numpy as np
import matplotlib.pyplot as plt
import wordlemodule

# Open pickle file
with open('Data/Script data/Imported_email_data_with_ints.pkl','rb') as file:
    full_data = pickle.load(file)

# Create custom wordle object with input data
data = wordlemodule.WordleData(full_data)

# Split the data into the number of senders
num_senders = data.num_senders()





# Plot histogram for average solve score
fig, ax = plt.subplots()

ax.hist(data.data_arr, bins=np.arange(0.5,8.5,1))

ax.set_ylabel('Number of occurences')
ax.set_title('Histogram of Wordle solve score')
ax.legend(data.data_dict.keys())

plt.show()

# By week-day: avg num games played, average solve score

# Plot scatterplot for solve score over time