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
1.12           03-04-2021      Initial release
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
import SessionState

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

st.title("🌍 Digital Collections on Chinese Studies in the Uniteds States and Canada")
st.sidebar.markdown('''
    # Group Information & Feedback Section

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

st.sidebar.subheader("Nevigation Bar for Multiple Search")

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

#@st.cache
### First of all, define a load_data function to read the csv file we want to use
def load_data():
    map_df = pd.read_csv("Up_20210120_with_keywords.csv", encoding='latin1')
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
data['Subject'] = data['Major Subject']+', '+data['Other Subjects'].fillna('')

###############
# Functions #
###############

### Create a function to return the state name from the address column
### It uses the the third last element from each collections' address
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

general_format_list = get_unique_value(data['General Format'])
sub_list = get_unique_value(data['Subject'])

general_format_final = get_unique_numbers(general_format_list)
major_subject_final = get_unique_numbers(sub_list)

general_format_final.sort()

###############
# Sidebar Selections #
###############

session_state = SessionState.get(general_format_SELECTED=[], button_confirm=False)

session_state.general_format_SELECTED = st.sidebar.multiselect('Enter General Format Fields', general_format_final)
button_confirm = st.sidebar.button("Confirm to 2nd Level Search")

if button_confirm:
    session_state.button_confirm = True

if session_state.button_confirm:

    progress_bar = st.progress(0)

    lir_gen_for = []
    for sub in session_state.general_format_SELECTED:
        lir_gen_for.append(sub)

    def prepross_gen_for (text):
        # initialize an empty string
        str_gen_for = ""

        # traverse in the string
        for i in text:
            str_gen_for = i+'|'+str_gen_for

        str_gen_for_final = str_gen_for[:-1]

        # return string
        return data[data['General Format'].str.contains(str_gen_for_final, case=False, regex=True)]

    data_second_fi = prepross_gen_for(lir_gen_for)
    data_second = data_second_fi.reset_index()

    specific_format_list = get_unique_value(data_second['Specific Formats'])
    specific_format_final = get_unique_numbers(specific_format_list)
    specific_format_final.sort()

    session_state.specific_format_SELECTED = st.sidebar.multiselect('Enter Specific Format Fields', specific_format_final)

    if st.sidebar.button("Search on 2nd Level Filtering"):

        lir_spe_for = []
        for sub in session_state.specific_format_SELECTED:
            lir_spe_for.append(sub)

        def prepross_spe_for (text):
            # initialize an empty string
            str_spe_for = ""

            # traverse in the string
            for i in text:
                str_spe_for = i+'|'+str_spe_for

            str_spe_for_final = str_spe_for[:-1]

            # return string
            return data_second[data_second['Specific Formats'].str.contains(str_spe_for_final, case=False, regex=True)]

        data_third = prepross_spe_for(lir_spe_for)

        def make_clickable(link):
            return f'<a href="{link}">{link}</a>'

        data_third['Links'] = data_third['URL'].apply(lambda x: make_clickable(x))

        data_final = data_third[['Institution', 'Library', 'Type of Library', 'Lanuages', 'General Format', 'Specific Formats', 'Subject', 'Keywords', 'Start Year', 'End Year']]
        data_des = data_third[['Collection Title', 'General Format', 'Specific Formats', 'Description', 'Address']]

        st.write(f"Number of Collections: {len(data_third)}", data_final)

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

        data_ht = pd.DataFrame(data_third[['Collection Title', 'Links']])
        st.write(data_ht.to_html(escape=False, index=False), unsafe_allow_html=True)
        progress_bar.progress(0.75)

        st.markdown(f'''
    ---
        ''')

        st.markdown('''
            ### Below is the corresponding map\n
    ---
        ''')

        st.map(data_third)
        progress_bar.progress(1.0)

        st.balloons()

#subject_SELECTED = st.sidebar.multiselect('Enter Subject Fields', major_subject_final)
