"""

GENERAL UTILITY PROJECT FUNCTIONS
THAT DO NOT RELATE DIRECTLY TO NEITHER THE SPOTIFY WEB API
NOR THE YOUTUB DATA API

"""

import pandas as pd
import json
import sys
import os
import re


def read_jsonfile_as_dict(filename):

    """
    Reads a json file and returns a dictionary
    :param filename: string with path and filename i.e. "./folder/file.json"
    :return: a dictionary
    """
    try:
        with open(filename) as json_file:
            json_dict = json.load(json_file)
    except FileNotFoundError:
        print(f"\nJSON file '{filename}' could not be found!")
        sys.exit(1)

    return json_dict


def read_csv_file(csv_filename, folder):
    """
    Reads a csv file into a DataFrame
    :param csv_filename: str
    :return: DataFrame
    """

    try:
        playlist_df = pd.read_csv(f"{folder}/{csv_filename}")
        return playlist_df

    except FileNotFoundError:
        print(f"\nError - Could not find the file: {csv_filename} in the folder {folder}")


def file_exists(filename, folder):

    return os.path.isfile(f"{folder}/{filename}")


def unpack_list_series(series):
    """

    Takes a Pandas Series in which each row has a lists of values
    i.e. row 1 = ['a','b']      row 2 = ['b','b']

    and returns another Pandas Series
    in which each individual value takes a row, also repeated values

    i.e. row 1 = ['a']      row 2 = ['b']     row 3 = ['b']      row 4 = ['b']

    :param series:
    :return: series
    """
    return pd.Series(sum(list(series.values), []))


def only_alphanumeric(string):

    """
    Strips all non alphanumeric characters from a string

    :param string: str with or without non alphanumeric chars
    :return: str with only alphanumeric chars
    """

    return re.sub(re.compile('\W'), '', string)



