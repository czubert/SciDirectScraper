import pandas as pd

import src.utils as utils


def data_processing(df: pd.DataFrame):
    """
    Getting rid of repetitions and group by email
    :param df: pd.DataFrame
    :return: pd.DataFrame
    """
    df.drop_duplicates(inplace=True)

    # Groups authors by eamil
    df = utils.group_by_email(df)

    # Returns num of a list in each row
    df['num_of_publications'] = [len(x) for x in df['publ_title']]

    # Getting only the first publication from all (and their details: year and affiliation)
    df = df.applymap(utils.return_first_el)

    # Removing records of the same author with different email
    df = df.drop_duplicates(['name', 'surname'], keep='first')

    return df
