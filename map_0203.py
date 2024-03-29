'''
Authors:       Kahang Ngau
               Yan He
               Ann James
               Sophie Muro
Organization:  GW
Updated:       02-10-2021
-------------------------------------------------------------------------------
SUMMARY:
This file is the main runner for the Streamlit app that uses the data from the
Chinese digital collections csv file. It is a searching engine for researchers
to explore Chinese digital collections that are located in US and Canada.
-------------------------------------------------------------------------------
VERSION        Date            Comments
1.1            02-03-2021      Initial release
-------------------------------------------------------------------------------
'''
############
# Built-In #
############
import re
import string
import time

###############
# Third-Party #
###############

import numpy as np
import pandas as pd
import pydeck as pdk
import webbrowser
import streamlit as st
from collections import Counter

import nltk
from nltk.stem import *
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

###############
# Set Page Layout & Title #
###############

st.set_page_config(
    page_title="Collection Exploration",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🌍 Digital Collections on Chinese Studies in the United States and Canada")
st.sidebar.markdown('''
    # Navigation Bar for Multiple Searching

''')

###############
# Set Sidebar checkbox for Project Members and Feedback Info #
###############

group_info = st.sidebar.checkbox('Project Members')
if group_info:
    st.sidebar.markdown('''

        #### Dr. Yan He (PI),
        China Documentation Center Librarian
    ''')

    st.sidebar.markdown('''
        #### Dr. Ann James (Co-PI),
        Data Science Libraian
    ''')

    st.sidebar.markdown('''
    Mr. Kahang Ngau, MS student

    Ms. Sophie Muro, MA student
    ''')

feedback_info = st.sidebar.checkbox('Feedback!')
Form = 'https://docs.google.com/forms/d/e/1FAIpQLSf83PHe3WHt6O7OuT7ZuE65HOQ8EN_EGuxiINidZbZ8IMzNyw/viewform'
if feedback_info:
    st.sidebar.markdown('''
    We love to have your feedback! If you can click the following and complete the form, we will greatly appreciate!

    ''')
    st.sidebar.markdown(Form, unsafe_allow_html=True)

st.sidebar.subheader("Multiple Filtering")

###############
# Set Main Page Info #
###############

st.markdown('''
    #### This website offers Multiple Filtering functions for our database of Chinese Digital Collections.\n

''')

dashboard_info = st.checkbox('Dashboard Link')
dashboard_link = 'https://esrifed-comm.maps.arcgis.com/apps/opsdashboard/index.html#/31c48340b5ab426c8416446f04954471'
if dashboard_info:
    st.markdown('''
    The dashboard link for the project is here:

    ''')
    st.markdown(dashboard_link, unsafe_allow_html=True)
  
st.markdown('''
    #### Choose the desired fields for each categories on the left sidebar, click the "Search" button, and we'll get to work! (You can also conduct a singular search by only entering one input.)\n

''')

###############
# Data Loaded #
###############

### First of all, define a load_data function to read the csv file we want to use
def load_data():
    map_df = pd.read_csv("Final_Metadata_Final.csv", encoding='latin1')
    return map_df

data = load_data()

###############
# NLP Analysis #
###############

### Natural Language Processing
### Conduct NLP in applying 'Stopwords' and 'Lemmatizer' functions to get rid of some of the redundant words
wordnet_lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

### Function to only include processed words but not words in stop_words
def process(line):
    return([wordnet_lemmatizer.lemmatize(t) for t in tokenizer.tokenize(line) if t not in stop_words])

### Function to get rid of numeric value in text searching
def numeric(line):
    return([ele for ele in line if ele.isnumeric()==False])  
  
### Created column 'tokens' to contains all tokenized words from Description column
tokenizer = RegexpTokenizer(r'\w+')
data['token'] = data['Description'].str.lower().apply(process)
data['tokens'] = data['token'].apply(numeric)

### Created column 'words' to split the 'tokens' column into string separated by comma
def split_list(text):
    return ",".join(text)

data['words'] = data['tokens'].apply(lambda x: split_list(x))

###############
# Functions #
###############

### Create a function to return the state name from the address column
### It uses the the third last element from each collections' address.
def split_word(text):
    States = text.split(',')[-3]
    state = States.strip()
    return state

### This function finds the value in a row of a column that separated by comma
def get_unique_value(df):

    uni_list = []
    for i in range(len(df)):
        list_1 = df[i].split (",")
        uni_list += list_1
    uni_list_final = [x.strip(' ') for x in uni_list]

    return uni_list_final

### This function finds the unique value of a list
def get_unique_numbers(numbers):

    list_of_unique_numbers = []
    unique_numbers = set(numbers)
    for number in unique_numbers:
        list_of_unique_numbers.append(number)

    return list_of_unique_numbers

###############
# Calling Functions #
###############

sub_list = get_unique_value(data['Subject'])
format_list = get_unique_value(data['Format'])
word_list = get_unique_value(data['words'])

final = get_unique_numbers(sub_list)
format_final = get_unique_numbers(format_list)
word_final = get_unique_numbers(word_list)

final.sort()
format_final.sort()
word_final.sort()

data['State'] = data['Address'].apply(lambda x: split_word(x))
state_final = data['State'].unique()
state_final.sort()

school_final = data['Institution'].unique()

combined_list = []
for i in range(len(data['tokens'])):
    combined_list += data['tokens'][i]

rslt = pd.DataFrame(Counter(combined_list).most_common(10),
                    columns=['Word', 'Frequency']).set_index('Word')

###############
# Sidebar Selections #
###############

state_SELECTED = st.sidebar.multiselect('Enter State Names', state_final)
school_SELECTED = st.sidebar.multiselect('Enter School Names', school_final)
subject_SELECTED = st.sidebar.multiselect('Enter Subject Fields', final)
format_SELECTED = st.sidebar.multiselect('Enter Format Fields', format_final)
number = st.sidebar.number_input('Enter a Year')
word_SELECTED = st.sidebar.multiselect('Enter Key Words', word_final)

common_word = st.sidebar.checkbox('Top 10 Most Common Words')
if common_word:
    st.sidebar.write(rslt)

###############
# Sidebar Button #
###############

if st.sidebar.button("Search"):

    progress_bar = st.progress(0)

    lir_state = []
    for sub in state_SELECTED:
        lir_state.append(sub)

    def prepross_state (text):
        # initialize an empty string
        str_state = ""

        # traverse in the string
        for i in text:
            str_state = i+'|'+str_state

        str_state_final = str_state[:-1]

        # return string
        return data[data['State'].str.contains(str_state_final, case=False, regex=True)]

    preprossing_state = prepross_state(lir_state)

    lir_school = []
    for sub in school_SELECTED:
        lir_school.append(sub)

    def prepross_school (text):
        # initialize an empty string
        str_school = ""

        # traverse in the string
        for i in text:
            str_school = i+'|'+str_school

        str_school_final = str_school[:-1]

        # return string
        return preprossing_state[preprossing_state['Institution'].str.contains(str_school_final, case=False, regex=True)]

    preprossing_school = prepross_school(lir_school)

    lir_2 = []
    for sub in subject_SELECTED:
        lir_2.append(sub)

    def prepross(text):
        # initialize an empty string
        str1 = ""

        # traverse in the string
        for i in text:
            str1 = i+'|'+str1

        str2 = str1[:-1]

        # return string
        return preprossing_school[preprossing_school['Subject'].str.contains(str2, case=False, regex=True)]

    processing_for = prepross(lir_2)

    lir_format = []
    for sub in format_SELECTED:
        lir_format.append(sub)

    def prepross_format(text):
        # initialize an empty string
        str_for = ""

        # traverse in the string
        for i in text:
            str_for = i+'|'+str_for

        str_final = str_for[:-1]

        # return string
        return processing_for[processing_for['Format'].str.contains(str_final, case=False, regex=True)]

    def make_clickable(link):
        return f'<a href="{link}">{link}</a>'

    processing_text = prepross_format(lir_format)
    
    # create a list to store all the input words from users 
    lir_word = []
    for sub in word_SELECTED:
        lir_word.append(sub)

    def prepross_word(text):
        # for loop to iterate through the list lir_word
        for i in lir_word:
            if i in text:
                return True
                continue

    processing_text['check'] = processing_text['tokens'].apply(lambda x: prepross_word(x))
    
    # Determine if the list of text input is empty
    if len(lir_word) == 0:
        processing_sub = processing_text
    else:
        processing_sub = processing_text[processing_text['check']==True]
        
    # Determine if the number input for year is empty
    if number == 0:
        data_input = processing_sub.sort_values(by=['Start Year'])
    else:
        data_input = processing_sub[
            (processing_sub["Start Year"] <= number) & (data["End Year"] >= number)
        ].sort_values(by=['Start Year'])

    data_input['Links'] = data_input['URL'].apply(lambda x: make_clickable(x))

    data_final = data_input[['Collection Title', 'Institution', 'Library', 'Format', 'Subject', 'Start Year', 'End Year', 'State']]
    data_des = data_input[['Collection Title', 'Description', 'Address']]

    st.write(f"Number of Collections: {len(data_final)}", data_final)
    progress_bar.progress(0.25)

    st.markdown("""
    ---
    """)

    st.table(data_des)
    progress_bar.progress(0.50)

    st.markdown('''
        ### Here is the URL, please Right-Click to open links\n
---
    ''')

    data_ht = pd.DataFrame(data_input[['Collection Title', 'Links']])
    st.write(data_ht.to_html(escape=False, index=False), unsafe_allow_html=True)
    progress_bar.progress(0.75)

    st.markdown(f'''
---
    ''')

    st.markdown('''
        ### Below is the corresponding map\n
---
    ''')

    st.map(data_input)
    progress_bar.progress(1.0)

    st.balloons()

st.sidebar.markdown('''
---
''')

st.sidebar.subheader('''
    Contact Information
''')

st.sidebar.markdown('''
#### For content questions, please contact: Yan He - The Project Leader

    hey@gwu.edu

#### For technical issues, please contact: Kahang Ngau - The Website Developer

    kngau@gwu.edu

---
''')
