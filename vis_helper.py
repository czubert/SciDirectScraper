import time
import streamlit as st


def print_duration(start_time):
    parsing_time = time.time() - start_time
    if parsing_time < 60:
        parsing_time = f'{round(parsing_time, 2)} s'
    elif parsing_time > 60:
        parsing_time = f'{parsing_time // 60} m {4300 % 3600 % 60} s'
    elif parsing_time > 3600:
        parsing_time = f'{parsing_time // 3600} h {4300 % 3600 // 60} m {4300 % 3600 % 60} s'

    st.sidebar.write(f'Total time: {parsing_time}')
    st.success('Articles parsed successfully!, to download - click the button below')
