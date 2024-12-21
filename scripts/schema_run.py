import csv
import pandas as pd
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# Database connection parameters
host = 'localhost'
dbname = 'postgres'
user = 'postgres'
password = 'mysecretpassword'
port="5432"

# Connect to PostgreSQL server
conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cur = conn.cursor()

# Function to construct file path
def construct_file_path(folder_name, person_name):
    base_path = "data/"
    file_name = f"{folder_name}_processed_new/{person_name}.csv"
    return base_path + file_name


personal_details_path = "data/winners_processed/List_of_winners_maha_data.csv"

##
# Read the CSV files
with open(personal_details_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        person_name = row['Candidate']

        # Construct file paths for each CSV
        movable_assets_path = construct_file_path("movable_assets", person_name)
        immovable_assets_path = construct_file_path("immovable_assets", person_name)
        liabilities_path = construct_file_path("liabilities", person_name)
        personal_historical_details_path = construct_file_path("details", person_name)


        # Execute COPY commands for each table
        # Prepare the SQL statement with placeholders
        sql = """
            INSERT INTO PersonalDetails (Name, Constituency, PartyCode, NumberOfCases, Education, TotalAssets, TotalLiabilities)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING ID;
            """

        cur.execute(sql, (
        person_name,
        row['Constituency'],
        row['Party'],
        row['Criminal Case'],
        row['Education'],
        row['Total Assets'],
        row['Liabilities'],
        ))
        
        # Retrieve the last inserted PersonalDetails ID
        last_inserted_id = cur.fetchone()[0]
        print(last_inserted_id)

        try:
        # Example for MovableAssets
            print("copying movable assests from ", movable_assets_path)

            movable_assets_csv=pd.read_csv(movable_assets_path,header="infer")
            immovable_assets_csv=pd.read_csv(immovable_assets_path,header="infer")
            liabilities_csv=pd.read_csv(liabilities_path,header="infer")
            historical_details_csv=pd.read_csv(personal_historical_details_path,header="infer")

            

            sql = """
            INSERT INTO MovableAssets (SrNo, Description, Self, Spouse, HUF, Dependent1, Dependent2, Dependent3, TotalPrice, PersonalDetailsID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            for i,rows in movable_assets_csv.iterrows():
                cur.execute(sql, (
                rows['SrNo'],
                rows['Description'],
                rows['Self'],
                rows['Spouse'],
                rows['HUF'],
                rows['Dependent1'],
                rows['Dependent2'],
                rows['Dependent3'],
                rows['TotalPrice'],
                last_inserted_id
                ))
            
            
            print("copying immovable assests from ", immovable_assets_path)

            sql = """
            INSERT INTO ImmovableAssets (SrNo, Description, Self, Spouse, HUF, Dependent1, Dependent2, Dependent3, TotalPrice, PersonalDetailsID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            for i,rows in immovable_assets_csv.iterrows():
                cur.execute(sql, (
                rows['SrNo'],
                rows['Description'],
                rows['Self'],
                rows['Spouse'],
                rows['HUF'],
                rows['Dependent1'],
                rows['Dependent2'],
                rows['Dependent3'],
                rows['TotalPrice'],
                last_inserted_id
                ))

            
            print("copying liabilities from ", liabilities_path)

            
            sql = """
            INSERT INTO Liabilities (SrNo, Description, Self, Spouse, HUF, Dependent1, Dependent2, Dependent3, TotalPrice, PersonalDetailsID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            for i,rows in liabilities_csv.iterrows():
                cur.execute(sql, (
                rows['SrNo'],
                rows['Description'],
                rows['Self'],
                rows['Spouse'],
                rows['HUF'],
                rows['Dependent1'],
                rows['Dependent2'],
                rows['Dependent3'],
                rows['TotalPrice'],
                last_inserted_id
                ))

            #cur.execute("""
            #        COPY MovableAssets (SrNo, Description, Self, Spouse, HUF, Dependent1, Dependent2, Dependent3, TotalPrice, PersonalDetailsID) 
            #        FROM %s 
            #        WITH (FORMAT csv, HEADER, DELIMITER ',',ESCAPE '|');
            #""", (movable_assets_path, last_inserted_id))

            #cur.execute("""
            #            COPY MovableAssets (SrNo, Description, Self, Spouse, HUF, Dependent1, Dependent2, Dependent3, TotalPrice, PersonalDetailsID) 
            #            FROM %s 
            #            WITH (FORMAT csv, HEADER, DELIMITER ',',ESCAPE '|');""", (movable_assets_path,last_inserted_id))

        # Repeat for other tables...

            #cur.execute("""
            #            COPY ImmovableAssets (SrNo, Description, Self, Spouse, HUF, Dependent1, Dependent2, Dependent3, TotalPrice, PersonalDetailsID) 
            #            FROM %s 
            #            WITH (FORMAT csv, HEADER, DELIMITER ',',ESCAPE '|');""", (immovable_assets_path,last_inserted_id))

        
            #cur.execute("""
            #            COPY Liabilities (SrNo, Description, Self, Spouse, HUF, Dependent1, Dependent2, Dependent3, TotalPrice, PersonalDetailsID) 
            #            FROM %s 
            #            WITH (FORMAT csv, HEADER, DELIMITER ',',ESCAPE '|'); """, (liabilities_path,last_inserted_id))


            if os.path.exists(personal_historical_details_path):
                print("copying personal history", personal_historical_details_path)
                sql = """
                    INSERT INTO PersonalHistoricalDetails (Name, Constituency, Age, PartyCode, CriminalCases, NumberOfCases, EducationLevel, TotalAssets, TotalLiabilities, PANGiven, PersonalDetailsID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                for i,rows in historical_details_csv.iterrows():
                    cur.execute(sql, (
                    rows['Name'],
                    rows['Constituency'],
                    rows['Age'],
                    rows['PartyCode'],
                    rows['CriminalCases'],
                    rows['NumberOfCases'],
                    rows['EducationLevel'],
                    rows['TotalAssets'],
                    rows['TotalLiabilities'],
                    rows['PANGiven'],
                    last_inserted_id
                    ))

                #print("copying personal history")
                #cur.execute("""
                #            COPY PersonalHistoricalDetails (Name, Constituency, Age, PartyCode, CriminalCases, NumberOfCases, EducationLevel, TotalAssets, TotalLiabilities, PANGiven, PersonalDetailsID) 
                #            FROM %s 
                #            WITH (FORMAT csv, HEADER, DELIMITER ',',ESCAPE '|');""", (personal_historical_details_path,last_inserted_id))
            else:
                continue
        except Exception as e:
            print(e)


# Commit changes and close the connection
conn.commit()
cur.close()
conn.close()
