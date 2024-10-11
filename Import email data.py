# This script imports emails (.eml) downloaded from gmail containing wordle results. Wordle results from each email are stored as integers along with the puzzle number.

# Import necessary libraries
import os
import base64
import numpy as np
import pandas as pd
#from google.colab import files


# Open wordle emails
email_list_dir = '.\Wordle emails'
email_list = os.listdir(email_list_dir)


## Extract wordle data from each email

# Create array to hold results
guesses_int_arr = np.zeros([6,5,2000], dtype='uint8')

# For each email in the upload
for email in email_list:
  # Open the file
  f = open(email_list_dir + '\\' + email, 'r',encoding='utf-8')

  # Get the body of the email in str format
  body = f.read()
  #body = body.decode('UTF-8')

  # Find the sender of the email (email address)
  senderStart = body.find('From: ') + 6
  senderEnd = body.find('\r', senderStart)
  sender = body[senderStart:senderEnd]
  senderEmail = sender[sender.find('<')+1 : sender.find('>')]

  # Get the wordle results
  wordleStart = body.find('base64')+6
  wordleEnd = body.find('--', wordleStart) - 1
  wordleResult = body[wordleStart:wordleEnd]

  # Decode the wordle result and store in variable
  wordleResult = base64.b64decode(wordleResult).decode('UTF-8')
  #print(wordleResult)





  # Extract wordle number to int
  puzzleNumber = wordleResult[7:12]
  puzzleNumber = int(puzzleNumber.replace(',',''))
  print(puzzleNumber)

  # Get wordle guesses in string
  guesses = wordleResult[17:]
  print("Guesses: ", guesses)

  # Create array of zeros to hold guesses
  guesses_int = np.zeros(30)

  # Convert wordle guesses to int
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



  # Reshape the array to the common wordle box shape
  guesses_int = guesses_int.astype(np.uint8).reshape(6,5)

  # Save int representation into 3-d array
  guesses_int_arr[:,:,puzzleNumber] = guesses_int

  print("guesses_int: \n\n",guesses_int)

  # Close the file
  f.close()

# Save int representations as numpy file
np.save('Wordle guesses as ints',guesses_int_arr)