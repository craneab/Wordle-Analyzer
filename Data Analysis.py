import pickle

# Open pickle file
with open('Data/Script data/Imported_email_data_with_ints.pkl','rb') as file:
    data = pickle.load(file)

# Split the data into the number of senders
num_senders = len(data)

# Plot average solve score
for sender in data:

    # Get array of integers
    curr_arr = data[sender]['0']

    # Find row at which puzzle is solved (all 3s)
    