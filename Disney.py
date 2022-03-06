import json
import pandas as pd
import numpy as np
import requests as rq
def retrieve_data_without_authentication():
    """
    This function retrieve data on Disney character
    The Disney API is accessible without authentication
    :return: a csv file that contains data on Disney characters
    """
    base_url = 'https://api.disneyapi.dev/'
    endpoint = 'characters'

    def request_page(base_url, endpoint, page):
        response = rq.get(base_url + endpoint + '?page=%d' % page)
        return response.json()

    def process_data(page):
        """
        This function process each page data so that lists are converted to string
        :param page: the page number of the API (This is to include pagination)
        :return: the data of a specified Disney API page where data that are list are converted into string
        """
        data = request_page(base_url, endpoint, page)['data']

        for item in data:
            for key, info in item.items():
                if (isinstance(info, list)):
                    #add comma (,) to the item unless it is the last item of the list
                    item[key] = ''.join(val if info.index(val) == len(info) - 1 else (val + ',') for val in info)
                    #set the list to np.nan if the list is empty
                    if len(item[key]) == 0:
                        item[key] = np.nan
        return data

    #create the inital dataframe to store data later
    result_df = pd.DataFrame()

    # the total number of pages in Disney API
    page_num = request_page(base_url, endpoint, 1)['totalPages']

    #loop through all the pages
    for i in range(1, page_num + 1):
        data = process_data(i)
        #create an empty dict to store data
        char_dict = {}

        #loop through all the characters in each page
        for j in range((request_page(base_url, endpoint, i)['count'])):
            #assign the value of data[j] to the key j in char_dict
            char_dict[j] = data[j]

        #create a json file to store char_dict
        out_file = open("disney.json", "w")
        json.dump(char_dict, out_file)
        out_file.close()

        #create a dataframe from the json file
        df = pd.read_json('disney.json', orient='index')

        #append the new dataframe to the initial dataframe
        result_df = result_df.append(df)

    #reset index of the initial dataframe
    result_df.reset_index(inplace=True)

    # drop all the columns that only contains null values
    result_df.dropna(how='all', axis=1, inplace=True)

    # drop all the rows that only contains null values
    result_df.dropna(how='all', axis=0, inplace=True)

    # drop these columns because they are not necessary
    result_df.drop(columns=['index', '__v'], inplace=True)

    # drop the duplicate rows
    result_df = result_df.drop_duplicates()

    # drop the duplicate columns by using .drop_duplicates() functions and transposing twice
    result_df = result_df.T.drop_duplicates().T

    #Fill null values with N/A (Not applicable)
    result_df.fillna('N/A', inplace=True)

    #create the csv file
    csvData1 = result_df.to_csv('disney.csv', index=False)

if __name__ == '__main__':
    retrieve_data_without_authentication()