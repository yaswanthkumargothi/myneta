from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException 
from selenium.webdriver.common.by import By
import time
import pandas as pd
import os


options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Set up the Selenium WebDriver
driver = webdriver.Chrome(options=options)

# Define the URL
url = 'https://myneta.info/maharashtra2019/index.php?action=show_winners&sort=default'

# Open the URL in the browser
driver.get(url)

# Wait for the page to load
time.sleep(8)

#table_xpath = '/html/body/div[2]/div[8]/table'  # Replace with the actual XPath
#table = driver.find_element(By.XPATH, table_xpath)

candidates=pd.read_csv("links_and_names.csv", header='infer')

# Find all rows with anchor tags within the table
#rows_with_links = table.find_elements(By.XPATH, ".//tr/td/a[text()!='']")

#print("candidate links 0: ",rows_with_links[0])
#print(len(rows_with_links))
# Initialize a list to store the candidates' links
#candidates_links = []
#candidate_names=[]

# Iterate over each row and extract the href attribute
#for row in rows_with_links:
#    link = row.get_attribute('href')
#    text = row.text
#    candidates_links.append(link)
#    candidate_names.append(text)
folders = ['income_tax','movable_assets', 'immovable_assets', 'liabilities','details']
    
for folder in folders:
        # Create the folder if it doesn't exist
    table_id_folder = os.path.join("data", folder)
    os.makedirs(table_id_folder, exist_ok=True)

# Now, iterate over each link and click on it
for index,candidate in candidates.iterrows():
    # Open the link in a new tab
    link = candidate["links"]
    driver.execute_script(f"window.open('{link}');")
    
    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[1])
    
    # Wait for the page to load
    time.sleep(3)

    # Define the IDs of the tables you want to download
    table_ids = ['#income_tax','#movable_assets', '#immovable_assets', '#liabilities']

    

    # Iterate over each table ID
    for table_id in table_ids:

        folder = table_id.replace('#', '')

        # Find the table by ID
        table_element = driver.find_element(By.CSS_SELECTOR, table_id)
        
        # Extract the headers
        headers = [header.text.strip() for header in table_element.find_elements(By.TAG_NAME, 'th')]
        
        # Initialize a list to store the table data
        table_data = []
        
        # Iterate over each row in the table
        for row in table_element.find_elements(By.TAG_NAME, 'tr')[1:]:
            # Extract the text from each cell in the row
            columns = row.find_elements(By.TAG_NAME, 'td')
            data = [col.text.strip() for col in columns]
            table_data.append(data)
        
        candidate_name = candidate["names"]

        table_id_folder = os.path.join("data", folder)
        # Write the data to a CSV file within the folder
        csv_filename = os.path.join(table_id_folder, f"{candidate_name}.csv")
        df = pd.DataFrame(table_data)
        df.to_csv(csv_filename, index=False)
        
        print(f'Data from {folder} saved to {csv_filename}')
    
    # Click on the "Click here for more details" link
    try:
        link_xpath = "/html/body/div[2]/div[4]/div[2]/div/div/table/tbody/tr[6]/th/a"
        details_link = driver.find_element(By.XPATH, link_xpath)
        driver.execute_script("arguments[0].click();", details_link)
        
        # Wait for the details page to load
        time.sleep(4)
        
        # Download all tables on the details page
        all_tables = driver.find_elements(By.TAG_NAME, 'table')

        table_element = all_tables[2]

        
        # Extract the headers
        headers = [header.text.strip() for header in table_element.find_elements(By.TAG_NAME, 'th')]
            
        # Initialize a list to store the table data
        table_data = []

        # Create the folder if it doesn't exist
        table_id_folder = os.path.join("data", "details")
     
     # Iterate over each row in the table
        for row in table_element.find_elements(By.TAG_NAME, 'tr')[1:]:
            # Extract the text from each cell in the row
            columns = row.find_elements(By.TAG_NAME, 'td')
            data = [col.text.strip() for col in columns]
            table_data.append(data)
            
            # Write the data to a CSV file
         # Write the data to a CSV file within the folder
        csv_filename = os.path.join(table_id_folder, f"{candidate_name}.csv")
        df = pd.DataFrame(table_data,columns=headers)
        df.to_csv(csv_filename, index=False)
        
        print(f'Data from details saved to {csv_filename}')
    except NoSuchElementException:
        print('Element not found, continuing to next step.')
            
    # Close the current tab
    driver.close()
    
    # Switch back to the main window
    driver.switch_to.window(driver.window_handles[0])

# Close the current tab
driver.close()
    
# Switch back to the main window
driver.switch_to.window(driver.window_handles[0])

# Close the browser
driver.quit()

print('Processed all candidate links and downloaded the specified tables.')
