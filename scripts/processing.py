import pandas as pd
import csv
import os

#headers
movable_asset_headers = ["SrNo","Description","Self","Spouse",	"HUF","Dependent1","Dependent2","Dependent3","TotalPrice"]
immovable_asset_headers = ["SrNo","Description","Self","Spouse",	"HUF","Dependent1","Dependent2","Dependent3","TotalPrice"]
liabilities_headers = ["SrNo","Description","Self","Spouse",   "HUF","Dependent1","Dependent2","Dependent3","TotalPrice"]
details_headers = ["Name","Constituency","Age","PartyCode","CriminalCases","NumberOfCases","EducationLevel","TotalAssets","TotalLiabilities","PANGiven"]


# Function to construct file path
def construct_file_path(folder_name, person_name):
    base_path = "data/"
    file_name = f"{folder_name}/{person_name}.csv"
    return base_path+file_name
 
def transform_value(x):
    if pd.isna(x) or x == 'Nil':
        return 0
    else:
        return x.split('\n')[0].replace('Rs', '').replace(',', '')
    
def add_roman_numerals(df):
    """Adds Roman numerals to the first column if missing and shifts the row to the right."""
    roman_numerals = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x','xi', 'xii','xiii']
    
    for index, row in df.iterrows():
        if row[0]in ["Total Current Market Value of (i) to (v) (as per Affidavit)","Totals Calculated","Gross Total Value (as per Affidavit)","Totals (Calculated as Sum of Values)", "Totals (Calculated as Sum of Values)"]:  # Check if first column value is not a number
            # Add Roman numeral based on index
            df.iloc[index, :] = df.iloc[index, :].shift(1, fill_value='')
            df.iloc[index, 0] = roman_numerals[index]
            
    return df

def add_roman_numerals_liablities(df):
    """Adds Roman numerals to the first column if missing and shifts the row to the right."""
    roman_numerals = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x','xi', 'xii','xiii','xiv','xv','xvi','xvii', 'xviii','xix','xx']
    
    for index, row in df.iterrows():
        if not row[0]in ['i', 'ii', 'iii', 'iv']:  # Check if first column value is not a number
            # Add Roman numeral based on index
            df.iloc[index, :] = df.iloc[index, :].shift(1, fill_value='')
            df.iloc[index, 0] = roman_numerals[index]
        else:  # Check if first column value is not a number
            # Add Roman numeral based on index
            df.iloc[index, 0] = roman_numerals[index]
            
    return df

def process_details(file, person_name):
    try:    
        data = pd.read_csv(file, header=1)
        

        # Apply the transformation to the last column
        data.iloc[:,7] = data.iloc[:,7].apply(transform_value)
        data.iloc[:,8] = data.iloc[:,8].apply(transform_value)
        file_name = f"{person_name}.csv"

        # Define the directory and file path
        directory = 'data/details_processed_new'
        file_path = os.path.join(directory, file_name)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        data.to_csv(file_path,header=details_headers,index=False)

    except:
        print("no details")

def process__assets(file, person_name,asset):
    try:  
        data = pd.read_csv(file, header='infer')
        df=add_roman_numerals(data)

        # Apply the transformation to the last column
        df.iloc[:,-1] = df.iloc[:,-1].apply(transform_value)

        file_name = f"{person_name}.csv"
        directory = "data/"+asset+"_processed_new/"
        file_path = os.path.join(directory, file_name)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        if asset =="movable_assets": 
            df.to_csv(file_path, header = movable_asset_headers,  index=False)
        elif asset == "immovable_assets":
            df.to_csv(file_path, header = immovable_asset_headers,  index=False)
        elif asset == "liabilities":
            df.to_csv(file_path, header = liabilities_headers,  index=False)
    except:
        print('no'+asset+person_name)

def process__liablities(file, person_name,asset):
    try:  
        data = pd.read_csv(file,header=1)
        df=add_roman_numerals_liablities(data)

        # Apply the transformation to the last column
        df.iloc[:,-1] = df.iloc[:,-1].apply(transform_value)

        file_name = f"{person_name}.csv"
        directory = "data/"+asset+"_processed_new/"
        file_path = os.path.join(directory, file_name)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

       
        df.to_csv(file_path, header = liabilities_headers,  index=False)
    except:
        print('no'+asset+person_name)            

with open('List_of_winners_maha_data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        person_name = row['Candidate']

        # Construct file paths for each CSV
        movable_assets_path = construct_file_path("movable_assets", person_name)
        immovable_assets_path = construct_file_path("immovable_assets", person_name)
        liabilities_path = construct_file_path("liabilities", person_name)
        personal_historical_details_path = construct_file_path("details", person_name)
        print(personal_historical_details_path)

        process__assets(movable_assets_path, person_name,"movable_assets")
        process__assets(immovable_assets_path, person_name,"immovable_assets")
        process__liablities(liabilities_path, person_name,"liabilities")
        process_details(personal_historical_details_path, person_name)

