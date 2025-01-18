# Wordle Analyzer
A practice project in python programming to analyze Wordle results. My overall goal in this project was to demonstrate ability to use common data analysis techniques in python, such as: using numpy, pandas, regular expressions, scipy stats, matplotlib, and seaborn, among other common packages; use of custom objects/classes and data engineering (in this case, extracting relevant email information from an email database and converting it to a useful python dictionary and array formats); as well as commonly used tools such as vscode, markdown files, working in both scripts and in Jupyter notebooks, and git/github.

## Background
Since the covid 2019 pandemic, my dad and I (and a few others) have been doing [NYT Wordle puzzles](https://www.nytimes.com/games/wordle/index.html) and sending each other the results using the share button on the Wordle website, which lets you email a visual representation of the puzzle results without the answer-revealing text characters.

<table align="center" border='0'>
    <tr>
        <td>Example Wordle result:</td>
        <td>Wordle 1,209 4/6  <br>🟨⬜⬜🟨⬜<br>⬜⬜🟨⬜🟩<br>🟩🟩🟩⬜🟩<br>🟩🟩🟩🟩🟩</td>
    </tr>

</table>

I built this python code project for fun, and to analyze the results of downloaded Wordle result emails to answer questions such as:
* Have I improved my average solve score over time?
* On average, do I solve puzzles faster than my dad?
* Do puzzles solved on weekends have higher scores than puzzles solved on weekdays?

## Code outline
The code is split into functional scripts, which operate on downloaded email files stored in a local directory. Follow the steps below to understand how the code works and to run it on your own Wordle results!

### 1. Download Wordle emails

The first step is to download your Wordle emails. In gmail, you can either download wordle emails one of two ways:
- Download emails one at a time: open the email &rarr; click the three dot menu in the upper right &rarr; download the email (this results in .eml format)
- Download all Wordle emails at once: set up a filter to add a label to all Wordle emails and then using Google Takeout to download emails with that label (this results in a .mbox file).

The data import script can handle both .eml and .mbox formats. Disclaimer: I have not test non-gmail email files with this code.

### 2. Import email data into a useable format (`Import email data.py`)

 This script scans the contents of each email in the downloaded email directory and extracts the Wordle puzzle number and the sender of the email (the `From:` field) and stores these in a python dictionary. The Wordle puzzle result characters (colored boxes) are contained in the body of the email, which the script decodes from base 64 (a common encoding for emails). 

<div  style="text-align:center">
<img src="Misc/Screenshot of Wordle email.png" width="400"/>
</div>
 
 As the program processes each email, data is stored as a nested dictionary structure using the extracted email addresses as the identity of the puzzle solver on the first level, and the puzzle numbers and wordle result (in unicode character bytes) as a key:value pair on the second level:
 
 ```
Dict
|
└─── Person 1 email
|    |
|    └─── '1208':'Wordle 1,208 4/6\r\n\r\n\u2b1c\u2b1c\u2b1c\u2b1c\u2b1c...'
|    └─── '1210':'Wordle 1,210 5/6\r\n\r\n\u2b1c\u2b1c\u2b1c\u2b1c\u2b1c...'
|
└─── Person 2 email
     |
     └─── '1210':'Wordle 1,210 6/6\r\n>\r\n>\u2b1c\u2b1c\u2b1c\u2b1c\ud83d...'
     └─── '1214':'Wordle 1,214 X/6\r\n\r\n\u2b1c\u2b1c\u2b1c\ud83d\udfe9...'
 ```

 In some cases, emails are replies, which means they have two Wordle results - the quoted text of the original email and the new text of the current email. In this situation both Wordle puzzles are analyzed and added to the appropriate person's dictionary of results.
 
 Finally, the data is saved as a .json file.
 
### 3. Convert Wordle results to int array for analysis (`Convert emails to ints.py`)

In order to quickly and cleanly run statistics on the data, the byte representations of the grey, yellow, and green boxes should be converted to an array of integers. The code in `Convert emails to ints.py` converts the 6 x 5 unicode character representations of each Wordle result into a 6 x 5 numpy array of integers using the following scheme:

<div align="center">

| Wordle result | Meaning |  | &rarr; Integer representation |
| :---: | :--- | :--- | :---: |
|   &#9744;    | Empty box: | space filler for unused guesses | 0
| ⬜    | Grey box: | letter is not in word | 1
| 🟨 | Yellow box: | letter is in word but not this position | 2
| 🟩 | Green box: | letter is in correct position | 3

</div>

As a result, a single Wordle puzzle would be converted as follows:

<table align="center" style="background-color:rgba(0, 0, 0, 0);" border='0'>
    <tr style="text-align: center">
    <th align='center'> 6 x 5 unicode chars
    </th>
    <th>
    </th>
    <th align='center'> 6 x 5 numpy integer array
    </th>
    </tr>
    <tr>
    <td  align='center'>
            🟨⬜⬜🟨⬜<br>
            ⬜⬜🟨⬜🟩<br>
            🟩🟩🟩⬜🟩<br>
            🟩🟩🟩🟩🟩<br>
            &thinsp;&#9744; &#9744; &#9744; &#9744; &#9744; &#9744;<br>
            &thinsp;&#9744; &#9744; &#9744; &#9744; &#9744; &#9744;</td>
    <td  align='center' style="font-size: 50px;"> &rarr;
    </td>
    <td  align='center'>    
            [[2&thinsp; 1&thinsp; 1&thinsp; 2&thinsp; 1]<br>
            &nbsp;[1&thinsp; 1&thinsp; 2&thinsp; 1&thinsp; 3]<br>
            &nbsp;[3&thinsp; 3&thinsp; 3&thinsp; 1&thinsp; 3]<br>
            &nbsp;[3&thinsp; 3&thinsp; 3&thinsp; 3&thinsp; 3]<br>
            &nbsp;[0&thinsp; 0&thinsp; 0&thinsp; 0&thinsp; 0]<br>
            &nbsp;[0&thinsp; 0&thinsp; 0&thinsp; 0&thinsp; 0]]</td>
    </tr>

</table>

Finally, the integer array for each puzzle is stored in a $R \times C \times P$ multi-dimensional numpy array, where $R$ is the row, $C$ is the column, and $P$ is the puzzle number. Therefore, to access the first row of guesses in puzzle 1210, you would slice the array by using `[1,:,1210]`, or to return the entire puzzle as a 6 x 5 array you would use `[:,:,1210]`.


### 4. Data analysis (`Data Analysis.ipynb`)

Data analysis is executed through a combination of the `Data Analysis.ipynb` Jupyter notebook and `wordlemodule.py` custom python module. `wordlemodule.py` defines a custom class (the 'WordleData' class) for handling Wordle data, and well as related methods for calculations, data engineering, and analysis. The `Data Analysis.ipynb` Jupyter notebook creates a WordleData object and handles graphing and explanations.

[GO TO DATA ANALYSIS](https://github.com/craneab/Wordle-Analyzer/blob/main/Data%20Analysis.ipynb)

To make the analysis clearer, email addresses extracted from the original Wordle emails can be converted into shorthand names. To do this, the WordleData object searches for a text file (/Misc/Email names.txt) containing the email addresses and the names. Multiple email addresses can be linked to the same name. For example:

HPotter456@aol.com:Harry <br>
Herm.Granger@yahoo.com:Hermione <br>
unicorn_princess_666@yahoo.com:Hermione <br>
rweas1@gmail.com:Ron

To protect the privacy of my family and friends I haven't included this file in github, and I have used alternative names for the analysis.