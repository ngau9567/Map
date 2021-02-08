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

st.markdown('''
    #### This website offers Multiple Filtering functions for our database of Chinese Digital Collections. The dashboard link is: https://arcg.is/14qPaG\n
    #### Choose the desired fields for each categories on the left sidebar, click the "Search" button, and we'll get to work! (You can also conduct a singular search by entering fewer inputs.)\n

''')

st.markdown("""
---
""")

st.sidebar.subheader("Multiple Filtering")

@st.cache
def load_data():
    map_df = pd.read_csv("Final_Metadata_Final.csv", encoding='latin1')
    return map_df

data = load_data()

def get_unique_value(df):

    uni_list = []
    for i in range(len(df)):
        list_1 = df[i].split (",")
        uni_list += list_1
    uni_list_final = [x.strip(' ') for x in uni_list]

    return uni_list_final

def get_unique_numbers(numbers):

    list_of_unique_numbers = []
    unique_numbers = set(numbers)
    for number in unique_numbers:
        list_of_unique_numbers.append(number)

    return list_of_unique_numbers

sub_list = get_unique_value(data['Subject'])
format_list = get_unique_value(data['Format'])

final = get_unique_numbers(sub_list)
format_final = get_unique_numbers(format_list)

final.sort()
format_final.sort()

school_final = data['Institution'].unique()

school_SELECTED = st.sidebar.multiselect('Please Enter the School Name', school_final)
subject_SELECTED = st.sidebar.multiselect('Please Enter the Subject Field', final)
format_SELECTED = st.sidebar.multiselect('Please Enter the Format Field', format_final)
number = st.sidebar.number_input('Enter a Start Year')


if st.sidebar.button("Search"):

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
        return data[data['Institution'].str.contains(str_school_final, case=False, regex=True)]

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

    processing_sub = prepross_format(lir_format)

    if number == 0:
        data_input = processing_sub.sort_values(by=['Start Year'])
    else:
        data_input = processing_sub[
            (processing_sub["Start Year"] <= number) & (data["End Year"] >= number)
        ].sort_values(by=['Start Year'])

    data_input['Links'] = data_input['URL'].apply(lambda x: make_clickable(x))

    data_final = data_input[['Collection Title', 'Institution', 'Library', 'Format', 'Subject', 'Start Year', 'End Year']]
    data_des = data_input[['Collection Title', 'Description', 'Address']]

    st.write(f"Number of Collections: {len(data_final)}", data_final)

    st.markdown("""
    ---
    """)

    st.table(data_des)

    st.markdown('''
        ### Here is the URL, please Right-Click to open links\n
---
    ''')

    data_ht = pd.DataFrame(data_input[['Collection Title', 'Links']])
    st.write(data_ht.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.markdown(f'''
---
    ''')

    st.markdown('''
        ### Below is the corresponding map\n
---
    ''')

    st.map(data_input)

    st.balloons()

st.sidebar.markdown('''
---
''')

st.sidebar.markdown('''
    ### Contact Information

For CONTENT comments or questions please Email:

    hey@gwu.edu

For TECHNICAL issues or questions please Email:

    kngau@gwu.edu

---
''')
