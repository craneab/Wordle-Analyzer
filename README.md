# Wordle Analyzer
A practice project in python programming to analyze Wordle results.

## Background
Since the covid 2019 pandemic, my dad and I have been doing [NYT Wordle puzzles](https://www.nytimes.com/games/wordle/index.html) and sending each other the results using the share button on the Wordle website, which lets you email a visual representation of the puzzle results without the answer-revealing text characters.

<table align="center">
    <tr>
        <td>Example Wordle result:</td>
        <td>Wordle 1,209 4/6  <br>🟨⬜⬜🟨⬜<br>⬜⬜🟨⬜🟩<br>🟩🟩🟩⬜🟩<br>🟩🟩🟩🟩🟩</td>
    </tr>

</table>

I built this python code project for fun, and to analyze the results of downloaded Wordle result emails to answer questions such as:
* Have I improved my average solve score over time?
* On average, do I solve puzzles faster than my dad?
* Am I more likely to solve a puzzle than my dad if I have a certain number of correct letters after a particular guess?

## Code outline
The code is split into three scripts, which operate on downloaded email (.eml) files stored in a local directory. Follow the steps below to understand how the code works and to run it on your own Wordle results!

### 1. Download Wordle emails

The first step is to download your Wordle emails. In gmail, you can either download emails individually by opening the email &rarr; clicking the three dot menu in the upper right &rarr; click download email, or you can download all Wordle emails at once by setting up a filter to add a label to all Wordle emails and then using Google Takeout to download all your email with that label. Disclaimer: I have not test non-gmail email files with this code.

### 2. Import email data into a useable format (`Import email data.py`)

 This script scans the contents of each .eml file in the downloaded email directory and extracts the Wordle puzzle number and the sender of the email (the `From:` field) and stores these in a python dictionary. The body of the email is decoded from the base 64 encoding commonly used to ensure quality of email transmissions. 

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
 
 ```
{
    "person1email@gmail.com": {
        "1208": "Wordle 1,208 4/6\r\n\r\n\u2b1c\u2b1c\u2b1c\u2b1c\u2b1c...",
        "1210": "Wordle 1,210 5/6\r\n\r\n\u2b1c\u2b1c\u2b1c\u2b1c\u2b1c..."
    },
    "person2email@gmail.com": {
        "1154": "Wordle 1,154 5/6\r\n\r\n\ud83d\udfe8\u2b1c\u2b1c\ud83d..."",
        "1209": "Wordle 1,209 4/6\r\n\r\n\ud83d\udfe8\u2b1c\u2b1c\ud83d...",
        "1210": "Wordle 1,210 6/6\r\n>\r\n> \u2b1c\u2b1c\u2b1c\u2b1c\ud83d...",
        "1214": "Wordle 1,214 X/6\r\n\r\n\u2b1c\u2b1c\u2b1c\ud83d\udfe9..."
    }
}
 ```
 
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

<table align="center" >
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


### 4. Data analysis