# This script imports emails (.eml) downloaded from gmail containing wordle results

# Import necessary libraries
from os import listdir
from base64 import b64decode
import json



# Open wordle email directory and get list of email files
email_list_dir = 'Data/Wordle emails'
email_list = listdir(email_list_dir)


# Def function to import wordle data from each email
def import_wordle_emails(email_list):

  # Create dictionary to hold results
  wordle_result_dict = {}

  # For each email in the upload
  for email in email_list:
    # Open the file
    f = open(email_list_dir + '\\' + email, 'r',encoding='utf-8')

    # Get the body of the email in str format
    body = f.read()
    #body = body.decode('UTF-8')

    # Get the wordle results
    wordleStart = body.find('base64')+6
    wordleEnd = body.find('--' or 'on', wordleStart) - 1
    wordleResult = body[wordleStart:wordleEnd]
    
    # Decode the wordle result and store in variable
    wordleResult = b64decode(wordleResult).decode('UTF-8')

    # Find the sender of the email (email address)
    senderStart = body.find('From: ') + 6
    senderEnd = body.find('To:', senderStart)
    sender = body[senderStart:senderEnd]
    senderEmail = sender[sender.find('<')+1 : sender.find('>')]  

    # Find the wordle puzzle number and save as int
    puzzleNumber = wordleResult[7:12]
    puzzleNumber = int(puzzleNumber.replace(',',''))
    print(puzzleNumber)

    def store_wordle_in_dict(wordleResult):
    # Separately save wordle results for each email address
    # as nested dictionaries
      if senderEmail not in wordle_result_dict:
        wordle_result_dict[senderEmail] = {puzzleNumber: wordleResult}
      else:
        wordle_result_dict[senderEmail][puzzleNumber] = wordleResult

    # If message contains replies, split wordleResult and analyze each
    if body.find('In-Reply-To:') > -1:  # Message contains replies

      next_email_start = wordleResult.find('On ')
      wordleResult1 = wordleResult[:next_email_start]
      # Save
      store_wordle_in_dict(wordleResult1)

      wordleResult2 = wordleResult[next_email_start:]

      # Find the email address of the reply email
      senderStart = wordleResult2.find('<')
      senderEnd = wordleResult2.find('>', senderStart)+1
      sender = wordleResult2[senderStart:senderEnd]
      senderEmail = sender[sender.find('<')+1 : sender.find('>')]  

      # Find beginning of wordle puzzle
      puzzle_start = wordleResult2.find("Wordle")
      wordleResult2 = wordleResult2[puzzle_start:]

      # Save
      store_wordle_in_dict(wordleResult2)

    else:
      # Save
      store_wordle_in_dict(wordleResult)

    # Close the file
    f.close()

  return wordle_result_dict

# Use the import_wordle_emails function to import relevant email data
wordle_result_dict = import_wordle_emails(email_list)

#print(wordle_result_dict)

# Save extracted email data as json file
with open("Data/Script data/Imported_email_data.json", "w") as outfile: 
    json.dump(wordle_result_dict, outfile, indent=4)



  

  



