import pandas as pd
import os

#headers
winners_headers = ["Sno","Candidate","Constituency","Party","Criminal Case","Education","Total Assets","Liabilities"]

def transform_value(x):
    if pd.isna(x):
        return 0
    else:
        return x.split(' ')[0].replace('Rs','').replace(',', '').strip()

def process__winners(file):
    try:  
        data = pd.read_csv(file, header="infer")

        # Apply the transformation to the last column
        data.iloc[:,6] = data.iloc[:,6].apply(transform_value)
        data.iloc[:,7] = data.iloc[:,7].apply(transform_value)


        file_name = f"List_of_winners_maha_data.csv"
        directory = "data/"+"winners_processed/"
        file_path = os.path.join(directory, file_name)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
       
        data.to_csv(file_path,header=winners_headers,index=False)
    except:
        print('no'+file)

file_path = "List_of_winners_maha_data.csv"
process__winners(file_path)

