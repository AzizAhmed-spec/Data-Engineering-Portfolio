import glob
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

target_file = "transformed_data.csv"
log_process = "log_process.txt"

# Extract

def extracted_from_csv(file_to_process):
    dataframe = pd.read_csv(file_to_process)
    return dataframe

def extracted_from_json(file_to_process):
    dataframe = pd.read_json(file_to_process, lines=True)
    return dataframe

def extracted_from_xml(file_to_process):
    dataframe = pd.DataFrame(columns=['name', 'height', 'weight'])
    tree = ET.parse(file_to_process)
    root = tree.getroot()
    for person in root:
        name = person.find('name').text
        height = float(person.find('height').text)
        weight = float(person.find('weight').text)
        dataframe = pd.concat([dataframe, pd.DataFrame(columns=[{'name':name, 'height':height, 'weight':weight}])], ignore_index=True)
    return dataframe

def extract():
    extracted_data = pd.DataFrame(columns=['name','height','weight'])
    for csvfile in glob.glob('*.csv'):
        if csvfile != target_file:
            extracted_data = pd.concat([extracted_data,pd.DataFrame(extracted_from_csv(csvfile))], ignore_index=True)
    for jsonfile in glob.glob('*.json'):
        extracted_data = pd.concat([extracted_data, pd.DataFrame(extracted_from_json(jsonfile))], ignore_index=True)

    for xmlfile in glob.glob('*.xml'):
        extracted_data = pd.concat([extracted_data, pd.DataFrame(extracted_from_xml(xmlfile))], ignore_index=True)

    return extracted_data


def transform(data):
    data['height'] = round(data.height * 0.254,2)
    data['weight'] = round(data.weight*0.45359237,2)
    return data

def load_data(target_file, transformed_data):
    transformed_data.to_csv(target_file)

def log_progress(message):
    timeStampFormat = '%Y-%h-%d-%H:%M:%S'
    now = datetime.now()
    timeStamp = now.strftime(timeStampFormat)
    with open(log_process, 'a') as f:
        f.write(timeStamp + ' ' + message +'\n')
        
