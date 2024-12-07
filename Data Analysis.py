import pickle
import numpy as np
import matplotlib.pyplot as plt
import wordlemodule

# Open pickle file
with open('Data/Script data/Imported_email_data_with_ints.pkl','rb') as file:
    full_data = pickle.load(file)

# Create custom wordle object with input data
data = wordlemodule.WordleData(full_data)
#df = data.linear_reg()
#df1,df2,df3 = data.weekly()
#df = data.rolling(20)
df = data.stats()

