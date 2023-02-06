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
