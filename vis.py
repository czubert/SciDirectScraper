import pandas as pd
import streamlit as st

import utils
from main import ScienceDirectParser

# STYLE
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
st.subheader('SciDirectScraper')
st.warning('The only requirement to run this app is to have installed Google Chrome on your computer')

key_word = st.text_input(label='Search for:', placeholder='type your keyword here', value='sers',
                         help='Type a keyword you are looking for.')

# # # PAGES # # #
st.markdown("""<hr style="height:1px;border:none;background-color:#ddd; margin:1px" /> """,
            unsafe_allow_html=True)
pages = int(st.number_input('How many pages with articles you would like to scrap ("0" to iterate over all pages):',
                            min_value=0, value=1, step=1,
                            help='If there are more articles then max articles per page,'
                                 'then there will be more pages with the rest of articles, '
                                 'choose how many of them would you like to scrap'))

# # # ARTICLES PER PAGE # # #
st.markdown("""<hr style="height:1px;border:none;background-color:#ddd; margin:1px" /> """,
            unsafe_allow_html=True)
pubs = {1: 25, 2: 50, 3: 75, 4: 100}
pubs_per_page = st.radio('How many articles per page would you like to parse:', [1, 2, 3, 4], index=3,
                         format_func=lambda x: pubs.get(x),
                         help='This parameter choose how many publications per one page should be visible,'
                              'the more the faster it will go, as each page must be opened before parsing')

# # # YEARS # # #
st.markdown("""<hr style="height:1px;border:none;background-color:#ddd; margin:1px" /> """,
            unsafe_allow_html=True)
year = st.radio('Select a single year or a range of years', ['Single', 'Range'])
if year == 'Single':
    year_single = int(st.number_input('Provide a year', min_value=1900, max_value=2023, value=2022, step=1))
    selected_year = [year_single]
else:
    st.write('Provide years "from" and "to"')
    year_from = int(st.number_input('Provide a year', min_value=1900, max_value=2023, value=2022, step=1, key='from'))
    year_to = int(st.number_input('Provide a year', min_value=1900, max_value=2023, value=2022, step=1, key='to'))
    selected_year = [year_from, year_to]

# st.progress
# # # PARSER + BUTTON # # #
st.markdown("""<hr style="height:1px;border:none;background-color:#ddd; margin:1px" /> """,
            unsafe_allow_html=True)
parser = ScienceDirectParser(keyword=key_word,
                             pub_per_page_multi25=pubs_per_page,
                             n_pages=pages,
                             years=selected_year)

if st.button(label='Run parsing'):
    parser.scrap()
    st.success('Articles parsed successfully!, to download - click the button below')

    try:
        st.download_button(
            label="Download data as CSV",
            data=parser.csv_file,
            file_name=parser.file_name + '.csv',
            mime='text/csv',
        )
    except TypeError:
        pass

    try:
        st.download_button(
            label="Download Excel worksheets",
            data=parser.collection_xlsx_buffer,
            file_name="pandas_multiple.xlsx",
            mime="application/vnd.ms-excel"
        )
    except TypeError:
        pass
