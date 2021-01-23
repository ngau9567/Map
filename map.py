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

st.title("🌍 Collection Exploration")
st.sidebar.markdown('''
    # Mapping Digital Collections on Chinese Studies in North America

    ---
''')

@st.cache
def load_data():
    map_df = pd.read_csv("Final_Metadata_Two.csv", encoding='latin1')
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
st.write(f"Filtering Start Year between {min_selection} & {max_selection}")
data = data[
    (data["Start Year"] >= min_selection) & (data["Start Year"] <= max_selection)
]

st.write(f"Filtering End Year between {min_selection_end} & {max_selection_end}")
data = data[
    (data["End Year"] >= min_selection_end) & (data["End Year"] <= max_selection_end)
]

st.write(f"Collection Selected by Year: {len(data)}")

# Plot the GPS coordinates on the map
st.map(data)

st.markdown("""
---
""")

#st.markdown(data.columns.tolist())

#st.markdown(data.Subject.unique)

uni_list = []
for i in range(len(data['Subject'])):
    list_1 = data['Subject'][i].split (",")
    uni_list += list_1

uni_list_final = [x.strip(' ') for x in uni_list]

st.sidebar.subheader("Filter Year")

def get_unique_numbers(numbers):
    list_of_unique_numbers = []
    unique_numbers = set(numbers)
    for number in unique_numbers:
        list_of_unique_numbers.append(number)

    return list_of_unique_numbers

final = get_unique_numbers(uni_list_final)

final.sort()

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

st.markdown('''
    Put one or more desire subject fields in the box below, click the "Search" button, and
    we'll get to work! A sample input should look something like the following:
    ```
    history
    art
    culture
    ...
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

                def preprocess_text (text):
                    final_list = data[data['Subject'].str.contains(text)]
                    return final_list

                process_text = preprocess_text(subject)
                progress_bar.progress(0.125)

                st.markdown(f'''
                    Here's what your Collection List looks like after being Search:\n
                    **Collection List**\n
                    {process_text}
                    ---
                ''')

            # Setting this flag to true so it prints output
            is_valid = True
            st.balloons()


    except Exception as e:
        st.markdown(f'''
            There was an unexpected error running the model. Please raise an
            issue [here](https://github.com/msalceda/emse-6574-final-project/issues)
            and provide the following details:
            1. What inputs you put in.
            2. The error message below.
            ERROR MESSAGE: {e}
        ''')
