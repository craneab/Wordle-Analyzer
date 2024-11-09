import pickle
import numpy as np
import matplotlib.pyplot as plt
import wordlemodule

# Open pickle file
with open('Data/Script data/Imported_email_data_with_ints.pkl','rb') as file:
    full_data = pickle.load(file)

# Create custom wordle object with input data
data = wordlemodule.WordleData(full_data)
df1,df2 = data.weekly()
df = data.rolling(20)





# Plot histogram for average solve score
#fig, ax = plt.subplots()
hist_solve_score = plt.figure(1)
ax = hist_solve_score.subplots()

ax.hist(data.data_arr, bins=np.arange(0.5,8.5,1))

ax.set_ylabel('Number of occurences')
ax.set_xlabel('Number of guesses')
ax.set_title('Histogram of Wordle solve score')
ax.legend(data.data_dict.keys())

#plt.show()

# By week-day: avg num games played, average solve score

# Plot scatterplot for solve score over time
score_over_time = plt.figure(2)
ax = score_over_time.subplots()
plot = df.plot(title="Score over time",subplots=True,ax=ax)
plt.show()
print('test')