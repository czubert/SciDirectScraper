import time
import streamlit as st


def get_duration(start_time):
    parsing_time = time.time() - start_time
    if parsing_time < 60:
        parsing_time = f'{round(parsing_time, 2)} s'
    elif parsing_time > 60:
        parsing_time = f'{int(parsing_time // 60)} m {4300 % 3600 % 60} s'
    elif parsing_time > 3600:
        parsing_time = f'{int(parsing_time // 3600)} h {int(4300 % 3600 // 60)} m {4300 % 3600 % 60} s'

    return parsing_time


def success_msg(parser, start_time):
    duration = get_duration(start_time)
    st.sidebar.success(f'Summary:'
                       f'\n* URLs extracted: {len(parser.articles_urls)} !'
                       f'\n* Authors collected: {parser.authors_collection.shape[0]}'
                       f'\n* Duration: {duration}')

    st.success('Articles parsed successfully! Saved in the "output" folder in app directory.'
               'Below find preview:')
