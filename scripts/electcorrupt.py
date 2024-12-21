import csv
import requests
from bs4 import BeautifulSoup

# Define the URL
url = 'https://myneta.info/maharashtra2019/index.php?action=show_winners&sort=default'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all tables on the page
    all_tables = soup.find_all('table')
    
    # Iterate over each table
    for index, table in enumerate(all_tables):
        # Initialize a list to store the scraped data
        table_data = []
        
        # Extract the headers
        headers = [header.text.strip() for header in table.find_all('th')]
        
        # Iterate over each row in the table, except for the header row
        for row in table.find_all('tr')[1:]:
            # Extract the text from each cell in the row
            columns = row.find_all('td')
            data = [col.text.strip() for col in columns]
            table_data.append(data)
        
        # Write the data to a CSV file
        csv_filename = f'table_{index}_data.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Write the headers first
            writer.writerows(table_data)  # Then write the data rows
        
        print(f'Data from table {index} saved to {csv_filename}')
else:
    print('Failed to retrieve the webpage')
