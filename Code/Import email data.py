# This script imports emails (.eml) downloaded from gmail containing wordle results

# Import necessary libraries
from os import listdir
from base64 import b64decode
import json
import mailbox
import quopri
import email

# Def function to import wordle data from each email in mbox format
def import_mbox_format():

  # Def function to trim message contents to just wordle results
  def trim_results(input):
    puzz_end = input.find('<')
    content_trimmed = input[:puzz_end]
    return content_trimmed

  # Create mailbox object
  mxbox_dir = 'Data/Wordle emails/Wordle.mbox'
  my_mailbox = mailbox.mbox(mxbox_dir, create=False)

  # Create dictionary to hold results
  wordle_result_dict = {}

  # Iterate through mbox messages
  for idx, message in enumerate(my_mailbox):

    print(idx)

    # Get message content, combine parts if multipart message
    if message.is_multipart():
        try:
          content = ''.join(part.get_payload(decode=False) for part in message.get_payload())
        except:
          print('Skipped', 'Subject: ', message['subject'],'\n','From: ', message['from'])
          continue
    else:
        content = message.get_payload(decode=False)
    

    # Get encoding
    encoding = message['Content-Transfer-Encoding']
    mailer = message['X-Mailer']
    if mailer != None:
      if mailer[0:10] == 'Apple Mail':
        encoding = '7bit'

    # Decode message
    if encoding in (None, 'base64'):
      try:
        content_decoded = b64decode(content).decode('UTF-8')
      except:
        try:
          content_decoded = b64decode(content[0:content.find('<')]).decode('UTF-8')
        except:
          content_decoded = quopri.decodestring(content).decode('UTF-8')
    elif encoding == '7bit':
      content_decoded = quopri.decodestring(content).decode('UTF-8')

    # If this email doesn't contain a puzzle, skip it
    if content_decoded[0:6] != 'Wordle':
      continue

    # Get puzzle number from decoded message
    puzzleNumber = content_decoded[7:12]
    puzzleNumber = puzzleNumber.replace(',','') #delete commas in numbers >999
    space_idx = puzzleNumber.find(' ')
    if space_idx > -1: #space present, so number is < 1,000
      puzzleNumber = puzzleNumber[:space_idx]

    # Message content cleaning (Delete any non-Wordle puzzle parts of the message content)
    puzz_start = content_decoded.find('/6')+2
    puzz_end = content_decoded.rfind(chr(129001), puzz_start, puzz_start+46)+1  #46 is max length of wordle
    content_trimmed = content_decoded[puzz_start:puzz_end]

    # Get message sender
    sender = message['from']

    # Store message and info into dictionary
    if sender not in wordle_result_dict:
      wordle_result_dict[sender] = {puzzleNumber: content_trimmed}
    else:
      wordle_result_dict[sender][puzzleNumber] = content_trimmed
  
  return wordle_result_dict

# Def function to import wordle data from each email in eml format
def import_eml_format(email_list):

  # Open wordle email directory and get list of email files
  email_list_dir = 'Data/Wordle emails'
  email_list = listdir(email_list_dir)

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
#wordle_result_dict = import_eml_format(email_list)
wordle_result_dict = import_mbox_format()
#print(wordle_result_dict)

# Save extracted email data as json file
with open("Data/Script data/Imported_email_data.json", "w") as outfile: 
    json.dump(wordle_result_dict, outfile, indent=4)



  

  



