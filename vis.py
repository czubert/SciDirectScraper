import time
import streamlit as st

import vis_helper
from main import ScienceDirectParser

st.set_page_config(layout="wide",
                   page_title='ScienceDirectScrapper',
                   initial_sidebar_state='expanded'
                   )
# Changing the width of the sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{
        width: 330px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child{
        width: 330px;
        margin-left: -330px;
    }

    """,
    unsafe_allow_html=True,
)
st.sidebar.title("Log:")

# STYLE
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
st.subheader('SciDirectScraper')
setup = st.expander("Setup")

with setup:
    window = st.radio('Windows opening properties', ['Standard', 'Maximized', 'Hidden'])

st.warning('The only requirement to run this app is to have installed Google Chrome on your computer')
col1, col2, col3 = st.columns(3)
with col1:
    key_word = st.text_input(label='Search for:', placeholder='type your keyword here', value='sers',
                             help='Type a keyword you are looking for.')

# # # PAGES # # #
with col2:
    num_of_articles = int(st.number_input('Number of articles to scrap (set "0" for all available):',
                                          min_value=0, value=1, step=1,
                                          help='If you set more articles than "max articles per page", '
                                               'then program will go through pages to achieve '
                                               'requested number of articles, '
                                               'choose how many of them would you like to scrap'))
with col3:
    # # # ARTICLES PER PAGE # # #
    pubs = {1: 25, 2: 50, 3: 75, 4: 100}
    pubs_per_page = st.radio('How many articles per page would you like to parse:', [1, 2, 3, 4], index=3,
                             format_func=lambda x: pubs.get(x),
                             help='This parameter choose how many publications per one page should be visible,'
                                  'the more the faster it will go, as each page must be opened before parsing')

st.markdown("""<hr style="height:1px;border:none;background-color:#ddd; margin:1px" /> """,
            unsafe_allow_html=True)

# # # YEARS # # #
col_year1, col_year2, col_year3 = st.columns(3)
with col_year1:
    year = st.radio('Select a single year or a range of years', ['Single', 'Range'])
if year == 'Single':
    with col_year2:
        year_single = int(st.number_input('Provide a year', min_value=1900, max_value=2024, value=2022, step=1))
        selected_year = [year_single]
else:
    with col_year2:
        year_from = int(
            st.number_input('Provide a year "from":', min_value=1900, max_value=2024, value=2022, step=1, key='from'))
    with col_year3:
        year_to = int(
            st.number_input('Provide a year "to":', min_value=1900, max_value=2024, value=2022, step=1, key='to'))
        selected_year = [x for x in range(year_from, year_to)]

# # # PARSER + BUTTON # # #
st.markdown("""<hr style="height:1px;border:none;background-color:#ddd; margin:1px" /> """,
            unsafe_allow_html=True)

_, _, _, btn_col2, _, _, _ = st.columns(7)
with btn_col2:
    btn = st.button(label='Run parsing')

parser = ScienceDirectParser(keyword=key_word,
                             pub_per_page_multi25=pubs_per_page,
                             requested_num_of_publ=num_of_articles,
                             years=selected_year,
                             window=window)

if btn:
    start_time = time.time()
    try:
        with st.spinner('Wait while program is extracting publications urls...'):
            parser.main()
            duration = vis_helper.print_duration(start_time)
            st.sidebar.success(f'Summary:'
                               f'\n* {len(parser.articles_urls)} urls extracted!'
                               f'\n* Authors collected: {parser.authors_collection.shape[0]}'
                               f'\n* Duration: {duration}')

    except Exception as e:
        st.error(f'Something went wrong. Exception:{e}')

    exp = st.expander('Show data')
    with exp:
        st.write(parser.authors_collection)  # Show results as DataFrame

    st.balloons()
