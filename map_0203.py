import re
import string
import time

###############
# Third-Party #
###############

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

# set page layout
st.set_page_config(
    page_title="Collection Exploration",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🌍 Collection Exploration on the United States and Canada")
st.sidebar.markdown('''
    # Mapping Digital Collections on Chinese Studies in North America

    ---
''')
st.markdown('''
    This website offers Multiple Filtering functions for our database of Chinese Digital Collections.\n
    Choose the desired fields for each categories on the left sidebar, click the "Search" button, and
    we'll get to work!\n
    You can also conduct a singular search by entering fewer inputs.\n
    A sample input should look something like the following:\n
    
    ```
    Art culture
    Image Text
    1600
    ```
''')

@st.cache
def load_data():
    map_df = pd.read_csv("Final_Metadata_Two.csv", encoding='latin1')
    return map_df

data = load_data()

uni_list = []
for i in range(len(data['Subject'])):
    list_1 = data['Subject'][i].split (",")
    uni_list += list_1

uni_list_final = [x.strip(' ') for x in uni_list]

st.sidebar.subheader("Multiple Filtering")

def get_unique_numbers(numbers):
    list_of_unique_numbers = []
    unique_numbers = set(numbers)
    for number in unique_numbers:
        list_of_unique_numbers.append(number)

    return list_of_unique_numbers

final = get_unique_numbers(uni_list_final)

final.sort()

format_final = data['Format'].unique()

subject_SELECTED = st.sidebar.multiselect('Please Enter the Subject Field', final)
format_SELECTED = st.sidebar.multiselect('Please Enter the Format Field', format_final)
number = st.sidebar.number_input('Enter a Start Year')

# Mask to filter dataframe
#mask_countries = data['Subject'].isin(subject_SELECTED)

#data = data[mask_countries]

if st.sidebar.button("Search"):

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
        return data[data['Subject'].str.contains(str2, case=False, regex=True)]

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

    #data[data['Subject'].str.contains(str2, case=False, regex=True)]

    processing_sub = prepross_format(lir_format)

    if number == 0:
        data_input = processing_sub.sort_values(by=['Start Year'])
    else:
        data_input = processing_sub[
            (processing_sub["Start Year"] <= number) & (data["End Year"] >= number)
        ].sort_values(by=['Start Year'])

    data_final = data_input[['Collection Title', 'Institution', 'Library', 'Format', 'Subject', 'Start Year', 'End Year']]
    data_des = data_input[['Collection Title', 'Description', 'Address']]

    st.write(f"Filtering Subject by {lir_2} within Year of {int(number)}")

    st.write(f"Collection Selected by Subject: {len(data_final)}")

    st.write('Below is a List of Collections:', data_final)

    st.table(data_des)

    st.markdown(f'''
        Here is the List of Collections' URL:\n

        {data_input[['URL']]}

    ''')

    st.map(data_input)

    st.balloons()
