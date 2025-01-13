import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape financial data
def get_financial_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch data. Status Code:", response.status_code)
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table')  # Extract all tables
    
    dataframes = []
    for table in tables:
        headers = []
        rows = []
        
        # Extract headers
        for header in table.find_all('th'):
            headers.append(header.text.strip())
        
        # Extract table rows
        for row in table.find_all('tr'):
            cells = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
            if cells:
                rows.append(cells)
        
        # Adjust headers if mismatched
        max_len = max(len(row) for row in rows)
        while len(headers) < max_len:
            headers.append(f"Column_{len(headers)+1}")
        
        # Convert to DataFrame
        if rows:
            df = pd.DataFrame(rows, columns=headers[:max_len])
            dataframes.append(df)
    
    return dataframes

# URL of the company page on Screener or similar website
url = 'https://www.screener.in/company/AERON/'  # Replace with the actual company URL

# Get all data tables
data_tables = get_financial_data(url)

# Display the tables
i = 1
if data_tables:
    for table in data_tables:
        print(f"\nTable {i}:")
        print(table)
        i += 1
else:
    print("No tables found or failed to fetch data.")
