# TextWiz

![alt text](https://github.com/asadamir21/TextWiz/blob/master/venv/Images/TextWizLogo.ico)

A Qualitative Data Analysis Software. This project’s main purpose is to provide an open source software to analyze text documents to understand perceptions, identify concepts, key ideas, interesting patterns and extract useful knowledge to support decision makings for the user.

Main Features Include:

- Import data/text using different file formats, web and social media
- Study word frequency, distributions and patterns.
- Find key words in context.
- Tag/annotate text.
- Sentiment Analysis
- Explore connections between sources for insights and meaning.
- Visualizations include tables, graphs, word clouds and trees.
- Survey Analysis

## Requirements
0. Python 3.x
1. Internet Connection

## Setup and Install requirements
Enter these commands on cmd to install all required dependencies
 
1. python -m pip install –upgrade pip' command
2. pip install -r requirements.txt 
3. python -m nltk.downloader all
4. python -m spacy download en_core_web_sm

- If you want to use social network analysis you will need an api key for google and twitter. You can obtain the api keys from Google Developer and Twitter Developer and enter the keys in the following file and line numbers.

# For Twitter

File Name: DataSource.py

Line 521:  Consumer Key
Line 522:  Consumer Secret
Line 523:  Access Token
Line 524:  Access Token Secret 

# For Youtube

File Name: DataSource.py

Line 580: Youtube API key

## How to use this software
1. Clone the repo
3. Open cmd and change path to current directory
4. Run the following command:
	python TextWiz.py


# Got a question?
If you have any questions please contact me on my <a href = "https://www.facebook.com/asad.amir.167">facebook profile</a>. 
If you have any suggestions please send me a message or make a pull request.

# How to cite 
Asad Amir (2020, May 30). TextWiz (Version 1.0.0). 

# Website Link
https://mfarmalkhan.github.io/TextWiz_Website/
