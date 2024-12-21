from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
import time
import pandas as pd


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

# Initialize a list to store the candidates' links

all_links_and_names=[]

def get_all_links():
    try:
        table_xpath = '/html/body/div[2]/div[8]/table'  # Replace with the actual XPath
        table = driver.find_element(By.XPATH, table_xpath)
        rows_with_links = table.find_elements(By.XPATH, ".//tr/td/a")
        candidates_links = []
        candidates_names=[]
        # Iterate over each row and extract the href attribute
        for i, rowlink in enumerate(rows_with_links):

            link = rowlink.get_attribute('href')
            text = rowlink.text
            if i%2!=0:
                print(link, text)
                candidates_links.append(link)
                candidates_names.append(text)

        return candidates_links,candidates_names
    except (NoSuchElementException, TimeoutException) as e:
        return None, None

def find_next_link(base_xpath, span_number):
    """
    Attempts to find the "Next" link using the provided base XPath and span number.
    Returns the element if found, None otherwise.
    """
    try:
        span_xpath = base_xpath + str(span_number) + "]"
        next_link = driver.find_element(By.XPATH, span_xpath)
        return next_link
    except (NoSuchElementException, TimeoutException):
        print(f"Next link with span number {span_number} not found.")
        return None

#span_number=0
#while True:
#    span_number += 1
#    print(span_number)

links,names = get_all_links()

print(len(links))
     

    # Convert links and names to a dictionary
links_and_names = dict(zip(links, names))    

# Create a pandas DataFrame
df = pd.DataFrame({"links": links, "names":names})

# Save the DataFrame as a CSV file
df.to_csv("links_and_names.csv", index=False)

#if links is None:
#    break  # Exit the loop if an exception occurred
    
    # Append the dictionary to a list
#all_links_and_names.append(links_and_names)

time.sleep(2)

    #base_xpath = "/html/body/div[2]/div[1]/div/span["

    #next_link = find_next_link(base_xpath, span_number)
    #if next_link is None:
    #    break

    #next_link.click()

    # Click on the "Next" link
    
    #time.sleep(8)

driver.quit()



