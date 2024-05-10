import textrazor
import json
import os
from itertools import combinations
from math import comb
from collections import Counter
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import fnmatch
import itertools
import time


textrazor.api_key = "YOUR_TEXTRAZOR_API_HERE"
spreadsheet_id = "YOUR_GOOGLE_SHEET_ID"
client = textrazor.TextRazor(extractors=["entities"])

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'

creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)



def excel_column_name(n):
    name = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        name = chr(65 + remainder) + name
    return name

def clear_sheet_range(spreadsheet_id, range_to_clear):
    service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_to_clear).execute()

range_to_clear = 'Sheet1'  # Clears all data in Sheet1
clear_sheet_range(spreadsheet_id, range_to_clear)

def update_sheet(competitor_num, entities, intersection_data=None, intersections_header=None, exclusive_data=None):
    if competitor_num is not None:
        header_range = 'Sheet1!A1:B1'
        headers = ["Competitors", "Entities"]
        header_body = {'values': [headers]}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=header_range,
            valueInputOption="RAW", body=header_body).execute()

        range_name = f"Sheet1!A{competitor_num+1}:B{competitor_num+1}"
        entity_counts = Counter(entities)
        formatted_entities = [f"{entity} - {count}" for entity, count in entity_counts.items()]
        values = [[f"Competitor {competitor_num}", ', '.join(formatted_entities)]]
        body = {'values': values}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption="RAW", body=body).execute()

    # Calculate starting index for exclusive and intersection data
    start_column_index = 3  # Exclusive data starts from column C

    if exclusive_data:
        end_exclusive_index = start_column_index + len(exclusive_data) - 1
        start_exclusive_column = excel_column_name(start_column_index)
        end_exclusive_column = excel_column_name(end_exclusive_index)
        exclusive_range = f"Sheet1!{start_exclusive_column}2:{end_exclusive_column}2"
        exclusive_headers = [f"C{i+1} Only" for i in range(len(exclusive_data))]
        exclusive_body = {'values': [[', '.join(data) for data in exclusive_data]]}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=exclusive_range,
            valueInputOption="RAW", body=exclusive_body).execute()
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=f"Sheet1!{start_exclusive_column}1:{end_exclusive_column}1",
            valueInputOption="RAW", body={'values': [exclusive_headers]}).execute()
        start_column_index = end_exclusive_index + 2  

    if intersection_data:
        end_intersection_index = start_column_index + len(intersection_data) - 1
        start_intersection_column = excel_column_name(start_column_index)
        end_intersection_column = excel_column_name(end_intersection_index)
        intersection_range = f"Sheet1!{start_intersection_column}2:{end_intersection_column}2"
        intersection_body = {'values': [intersection_data]}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=intersection_range,
            valueInputOption="RAW", body=intersection_body).execute()
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=f"Sheet1!{start_intersection_column}1:{end_intersection_column}1",
            valueInputOption="RAW", body={'values': [intersections_header]}).execute()

            
def generate_intersections(competitor_entities):
    total_competitors = len(competitor_entities)
    intersection_results = []
    headers = []

    for k in range(total_competitors, 1, -1):  
        for combo in itertools.combinations(range(total_competitors), k):
            intersection = set.intersection(*(competitor_entities[i] for i in combo))
            if intersection:  
                intersection_results.append(', '.join(intersection))
                headers.append(f"C {'∩ C '.join(str(x+1) for x in combo)}")
    
    return intersection_results, headers

def calculate_exclusive_entities(competitor_entities):
    total_competitors = len(competitor_entities)
    exclusive_results = []
    all_entities = set.union(*competitor_entities)
    
    for i in range(total_competitors):
        others = all_entities - competitor_entities[i]
        exclusive_entities = competitor_entities[i] - others
        exclusive_results.append(list(exclusive_entities))

    return exclusive_results


def get_files(directory, pattern="comp*.txt"):
    """Retrieve file paths matching the pattern within the directory."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if fnmatch.fnmatch(f, pattern)]

directory_path = "./files"
files = get_files(directory_path)
print(files)
competitor_entities = []

def analyze_text_with_retry(file_path, max_retries=3, retry_delay=5):
    attempts = 0
    while attempts < max_retries:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            response = client.analyze(text)
            if response.ok:  
                return response  

        except Exception as e:
            print(f"Attempt {attempts + 1} failed with error: {e}")
            time.sleep(retry_delay)  # Wait before retrying
            attempts += 1

    print(f"All {max_retries} attempts failed for file: {file_path}")
    return None  

for i, file_path in enumerate(files):
    response = analyze_text_with_retry(file_path)
    if response is not None:
        entities = [entity['entityId'] for entity in response.json['response']['entities']]
        competitor_entities.append(set(entities))
        update_sheet(i + 1, entities)
    else:
        print(f"Analysis for {file_path} completely failed after retries.")

total_competitors = len(files)
intersection_results = []
headers = []

for k in range(2, total_competitors + 1):
    for combo in combinations(range(total_competitors), k):
        intersection = set.intersection(*(competitor_entities[i] for i in combo))
        intersection_results.append(', '.join(intersection))
        print(intersection_results)
        headers.append(f"C {'∩ C '.join(map(str, [x+1 for x in combo]))}")
        print(headers)

intersection_results, headers = generate_intersections(competitor_entities)
exclusive_data = calculate_exclusive_entities(competitor_entities)
update_sheet(None, None, intersection_results, headers, exclusive_data)
