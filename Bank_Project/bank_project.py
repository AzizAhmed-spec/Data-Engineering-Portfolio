import requests
import pandas as pd
from datetime import datetime
import numpy as np
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sqlite3

# Code for ETL operations on Country-GDP data
url = 'https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attribs = ['Rank', 'Bank Name', 'Market Cap']
csv_path = '/Users/abdelazizahmed/IBM ETL/Bank_Project/exchange_rate.csv'
out_put_path = '/Users/abdelazizahmed/IBM ETL/Bank_Project/outputpath.csv'
db_name = 'Banks.db'
table_name = 'Largest_banks'


# Importing the required libraries

def log_progress(message):
    ''' This function logs the mentioned message of a given stage of the
    code execution to a log file. Function returns nothing'''
    timeStampFormat = '%Y-%h-%d-%H:%M:%S'
    now = datetime.now()
    timeStamp = now.strftime(timeStampFormat)
    with open("./etl_project_log.txt", 'a') as f:
        f.write(timeStamp + ',' + message +'\n')

def extract(url, table_attribs):
    ''' This function aims to extract the required
    information from the website and save it to a data frame. The
    function returns the data frame for further processing. '''
    html_page = requests.get(url).text
    data = BeautifulSoup(html_page, 'html.parser')
    table = data.find_all('tbody')
    rows = table[0].find_all('tr')
    df = pd.DataFrame(columns = table_attribs)

    for row in rows:
        col = row.find_all('td')
        if len(col) != 0:
            if col[1].find('a') is not None:
                data_dict = {'Rank': col[0].get_text(strip=True),
                            'Bank Name': col[1].get_text(strip=True),
                            'Market Cap': col[2].get_text(strip=True)}
                df1 = pd.DataFrame(data_dict, index=[0])
                df = pd.concat([df,df1], ignore_index=True)
    return df

def transform(df, csv_path):
    ''' This function accesses the CSV file for exchange rate
    information, and adds three columns to the data frame, each
    containing the transformed version of Market Cap column to
    respective currencies'''
    exchange_rate = pd.read_csv(csv_path)
    cap = df['Market Cap'].to_list()
    cap = [float("".join(x.split(','))) for x in cap]
    rates = exchange_rate.set_index('Currency')['Rate'].to_dict()
    df['MC_GBP_Billion'] = [np.round(x*rates['GBP'],2) for x in cap]
    df['MC_EUR_Billion'] = [np.round(x*rates['EUR'],2) for x in cap]
    df['MC_INR_Billion'] = [np.round(x*rates['INR'],2) for x in cap]

    print(df)

    return df

def load_to_csv(df, output_path):
    ''' This function saves the final data frame as a CSV file in
    the provided path. Function returns nothing.'''
    df.to_csv(output_path)

def load_to_db(df, sql_connection, table_name):
    ''' This function saves the final data frame to a database
    table with the provided name. Function returns nothing.'''
    df.to_sql(table_name, sql_connection, if_exists = 'replace', index = False)

def run_query(query_statement, sql_connection):
    ''' This function runs the query on the database table and
    prints the output on the terminal. Function returns nothing. '''
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)

''' Here, you define the required entities and call the relevant
functions in the correct order to complete the project. Note that this
portion is not inside any function.'''


log_progress("ETL has started")
log_progress("extracting has started")
extracted_data = extract(url,table_attribs)

log_progress("extracting has finished")
log_progress("Transforming the data has started")
transformed_data = transform(extracted_data, csv_path)
log_progress("transforming has finished")

log_progress("Loading the data to csv has started")
load_to_csv(transformed_data, out_put_path)
log_progress("Loading the data to csv has finished")

log_progress("SQL Connection initiated.")
sql_connection = sqlite3.connect(db_name)
load_to_db(transformed_data, sql_connection,table_name)
log_progress("Data loaded to Database as table. Running the query.")

query_statement1 =  f"SELECT * FROM {table_name}"
run_query(query_statement1, sql_connection)
query_statement2 =  f"SELECT AVG(MC_GBP_Billion) FROM {table_name}"
run_query(query_statement2, sql_connection)
query_statement3 =  f"SELECT 'Bank Name' from {table_name} LIMIT 5"
run_query(query_statement3, sql_connection)
log_progress("Process Complete.")

sql_connection.close()