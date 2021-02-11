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

st.title("🌍 Collection Exploration on Time Series")
st.sidebar.markdown('''
    # Mapping Digital Collections on Chinese Studies in North America

    ---
''')

@st.cache
def load_data():
    map_df = pd.read_csv("Final_Metadata_Final.csv", encoding='latin1')
    return map_df

data = load_data()

# Calculate the timerange for Start Year
min_st = min(data["Start Year"])
max_st = max(data["Start Year"])

# Calculate the timerange for End Year
min_ed = min(data["End Year"])
max_ed = max(data["End Year"])

st.sidebar.subheader("Time Inputs")
min_selection, max_selection = st.sidebar.slider(
    "Timeline: Start Year", min_value=min_st, max_value=max_st, value=[min_st, max_st]
)

min_selection_end, max_selection_end = st.sidebar.slider(
    "Timeline: End Year", min_value=min_ed, max_value=max_ed, value=[min_ed, max_ed]
)

# Filter Data based on selection
st.write(f"Filtering Start Year between: {min_selection} & {max_selection}")
data = data[
    (data["Start Year"] >= min_selection) & (data["Start Year"] <= max_selection)
]

st.write(f"Filtering End Year between: {min_selection_end} & {max_selection_end}")
data = data[
    (data["End Year"] >= min_selection_end) & (data["End Year"] <= max_selection_end)
]

st.write(f"Collection Selected by Year: {len(data)}")

# Plot the GPS coordinates on the map
st.map(data)

st.markdown("""
---
""")

st.title("🌍 Collection Exploration on Inputing Year")

@st.cache
def load_data():
    map_df = pd.read_csv("Final_Metadata_Final.csv", encoding='latin1')
    return map_df

data = load_data()

number = st.number_input('Enter a Year')

if st.button("Find Collections on Year"):

    data_input = data[
        (data["Start Year"] <= number) & (data["End Year"] >= number)
    ].sort_values(by=['Start Year'])

    st.write(f"Collection Selected by Year: {len(data_input)}")

    st.write('The Collections are: ', data_input)

    st.map(data_input)

#st.markdown(data.columns.tolist())

#st.markdown(data.Subject.unique)

@st.cache
def load_data():
    map_df = pd.read_csv("Final_Metadata_Final.csv", encoding='latin1')
    return map_df

data = load_data()

uni_list = []
for i in range(len(data['Subject'])):
    list_1 = data['Subject'][i].split (",")
    uni_list += list_1

uni_list_final = [x.strip(' ') for x in uni_list]

st.sidebar.subheader("Subject - Single Filtering")

def get_unique_numbers(numbers):
    list_of_unique_numbers = []
    unique_numbers = set(numbers)
    for number in unique_numbers:
        list_of_unique_numbers.append(number)

    return list_of_unique_numbers

final = get_unique_numbers(uni_list_final)

final.sort()

st.title("🌍 Collection Exploration on Single Filtering (Subject)")

#Checkbox for Hospitals
col_list = st.sidebar.selectbox("Select Subject", final)

# Filter Data based on selection
st.write(f"Filtering Subject on {col_list}")
data_su = data[
    (data["Subject"].str.contains(col_list))
]

st.write(f"Collection Selected by Subject: {len(data_su)}")

# Plot the GPS coordinates on the map
st.map(data_su)

#Chech box for Documents
#for_unique = st.sidebar.selectbox("Select Format", format_unique)

#st.subheader('Collection Count')

st.markdown("""
---

""")
st.title("🌍 Collection Exploration on Multiple Filtering (Subject)")
st.markdown("""
Selected Subjects:

""")

st.sidebar.subheader("Subject - Multiple Filtering")

check_boxes = [st.sidebar.checkbox(sub, key=sub) for sub in final]

st.write([sub for sub, checked in zip(final, check_boxes) if checked])

checked_boxes = [sub for sub, checked in zip(final, check_boxes) if checked]

if st.button("Find Collections on Multiple Subjects"):

    lir_1 = []
    for sub in checked_boxes:
        lir_1.append(sub)

    def prepross(text):
        # initialize an empty string
        str1 = ""
        #x = text.split(' ')

        # traverse in the string
        for i in text:
            str1 = i+'|'+str1

        str2 = str1[:-1]

        # return string
        return data[data['Subject'].str.contains(str2, case=False, regex=True)]

    #data[data['Subject'].str.contains(str2, case=False, regex=True)]

    processing_text = prepross(lir_1)

    st.write(f"Filtering Subject on {lir_1}")

    st.write(f"Collection Selected by Subject: {len(processing_text)}")

    st.write('Below is a List of Collections:', processing_text)

    st.map(processing_text)


st.markdown("""
---
""")


st.title("🌍 Collection Exploration on Inputs (Subject)")

st.markdown('''
    Put one or more desire subject fields in the box below, click the "Search" button, and
    we'll get to work! A sample input should look something like the following:
    ```
    history|art|culture|...
    ```
''')
subject = st.text_area('Subject')
is_valid = False

if st.button('Search'):
    try:
        if subject == '':
            st.markdown('''
                Subject list is empty! Please put something in and try again.
            ''')
        else:
            with st.spinner('Getting predictions...'):
                progress_bar = st.progress(0)

                def listToString(text):
                    # initialize an empty string
                    #str1 = ""
                    #x = text.split(' ')

                    # traverse in the string
                    #for i in x:
                        #str1 = i+'|'+str1

                    #str2 = str1[:-1]

                    # return string
                    return data[data['Subject'].str.contains(text, case=False, regex=True)]

                #data[data['Subject'].str.contains(str2, case=False, regex=True)]

                process_text = listToString(subject)
                progress_bar.progress(1.0)

                st.write('Below is a List of Collections:', process_text)

                st.write(f"Filtering Subject on {subject}")

                st.write(f"Collection Selected by Subject: {len(process_text)}")

                st.markdown(f'''
                    Here's what your Collection List looks like after being Search:\n
                    **URL List**\n
                    {process_text[['Collection Title', 'URL']]}
                    ---
                ''')

                st.map(process_text)

            # Setting this flag to true so it prints output
            is_valid = True
            st.balloons()


    except Exception as e:
        st.markdown(f'''
            There was an unexpected error running the model. Please raise an
            issue [here]('')
            and provide the following details:
            1. What inputs you put in.
            2. The error message below.
            ERROR MESSAGE: {e}
        ''')
