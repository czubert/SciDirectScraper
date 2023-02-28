import time
import streamlit as st
from streamlit.errors import StreamlitAPIException

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

# # # Select Browser # # #
browser = {1: 'Chrome', 2: 'EDGE', 3: 'Firefox'}
pubs_per_page = st.radio('Select browser for parsing:', [1, 2, 3], index=0,
                         format_func=lambda x: browser.get(x),
                         help='This browser must be installed on your PC')

st.markdown("""<hr style="height:1px;border:none;background-color:#ddd; margin:1px" /> """,
            unsafe_allow_html=True)

with st.expander("Setup popup window"):
    window = st.radio('Window opening properties', ['Standard', 'Maximized', 'Hidden'])

st.markdown("""<hr style="height:1px;border:none;background-color:#ddd; margin:1px" /> """,
            unsafe_allow_html=True)

col1, col2 = st.columns(2)
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
                             requested_num_of_publ=num_of_articles,
                             years=selected_year,
                             window=window)

if btn:
    start_time = time.time()

    with st.spinner('Wait while program is collecting authors...'):
        ###
        # ====> Parser Initialization <====
        ###

        # Creates named DataFrame for data storage, creates parser URL, initialize WebDriver
        st.sidebar.write('Parser initialization...')
        parser.parser_init()

        ###
        # ====> Getting articles URLs <====
        ###

        st.sidebar.write('Getting articles URLs...')
        # Opens search engine from initial URL. Parse all publications urls page by page
        parser.get_articles_urls(open_browser_sleep=1.5, pagination_sleep=1.0)

        ###
        # ====> Collecting authors data - parsing <====
        ###

        st.sidebar.write('Collecting  authors data...')
        # initializing progressbar for authors collection
        progress_bar = st.sidebar.progress(0)
        # Takes opened driver and opens each publication in a new tab
        parser.parse_articles(btn_click_sleep=0.25, pbar=progress_bar)
        # Showing progressbar
        try:
            st.sidebar.write(progress_bar)
        except StreamlitAPIException:
            pass

        ###
        # ====> Postprocessing data <====
        ###

        # Takes opened driver and opens each publication in a new tab
        st.sidebar.write('Postprocessing the data...')
        parser.data_postprocessing()

    vis_helper.success_msg(parser, start_time)

    with st.spinner('Program is preparing a DataFrame preview'):
        with st.expander('Show data'):
            st.write(parser.authors_collection)  # Show results as DataFrame

    balloons = False
    if not balloons:
        st.balloons()
        balloons = True
