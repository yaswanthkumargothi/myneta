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

# Create a cursor object
cur = conn.cursor()

# Create a new database
#try:
#    cur.execute('CREATE DATABASE {};'.format(dbname))
#    print("Database created successfully")
#except Exception as e:
#    print("An error occurred: ", e)

# Close the connection to the default database
#cur.close()
#conn.close()

# Connect to the new database
#conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password)
#cur = conn.cursor()
table_names=["PersonalDetails","MovableAssets","ImmovableAssets","Liabilities","PersonalHistoricalDetails"]

# Function to remove tables if they exist
def remove_tables_if_exist(table_names):
    for table_name in table_names:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        except psycopg2.ProgrammingError as e:
            if e.pgcode != '42P07':  # Table does not exist
                raise e

remove_tables_if_exist(table_names)

# SQL statements to create tables
create_tables_sql = """
-- Table for storing personal details
CREATE TABLE PersonalDetails (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(255),
    Constituency VARCHAR(255),
    PartyCode VARCHAR(50),
    NumberOfCases INT,
    Education VARCHAR(255),
    TotalAssets DECIMAL(18, 2),
    TotalLiabilities DECIMAL(18, 2)
);

-- Table for storing movable assets
CREATE TABLE MovableAssets (
    AssetID SERIAL PRIMARY KEY,
    SrNo VARCHAR(255),
    Description VARCHAR(255),
    Self VARCHAR(4000),
    Spouse VARCHAR(2000),
    HUF VARCHAR(1000),
    Dependent1 VARCHAR(1000),
    Dependent2 VARCHAR(255),
    Dependent3 VARCHAR(255),
    TotalPrice DECIMAL(18, 2),
    PersonalDetailsID INT,
    FOREIGN KEY (PersonalDetailsID) REFERENCES PersonalDetails(ID) DEFERRABLE INITIALLY DEFERRED
);

-- Table for storing immovable assets
CREATE TABLE ImmovableAssets (
    AssetID SERIAL PRIMARY KEY,
    SrNo VARCHAR(255),
    Description VARCHAR(255),
    Self VARCHAR(3000),
    Spouse VARCHAR(2000),
    HUF VARCHAR(255),
    Dependent1 VARCHAR(1000),
    Dependent2 VARCHAR(255),
    Dependent3 VARCHAR(255),
    TotalPrice DECIMAL(18, 2),
    PersonalDetailsID INT,
    FOREIGN KEY (PersonalDetailsID) REFERENCES PersonalDetails(ID) DEFERRABLE INITIALLY DEFERRED
);

-- Table for storing liabilities
CREATE TABLE Liabilities (
    LiabilityID SERIAL PRIMARY KEY,
    SrNo VARCHAR(255),
    Description VARCHAR(255),
    Self VARCHAR(3000),
    Spouse VARCHAR(1000),
    HUF VARCHAR(255),
    Dependent1 VARCHAR(1000),
    Dependent2 VARCHAR(255),
    Dependent3 VARCHAR(255),
    TotalPrice DECIMAL(18, 2),
    PersonalDetailsID INT,
    FOREIGN KEY (PersonalDetailsID) REFERENCES PersonalDetails(ID) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE PersonalHistoricalDetails (
    HistID SERIAL PRIMARY KEY,
    Name VARCHAR(255),
    Constituency VARCHAR(255),
    Age INT,
    PartyCode VARCHAR(50),
    CriminalCases VARCHAR(50),
    NumberOfCases INT,
    EducationLevel VARCHAR(255),
    TotalAssets DECIMAL(18, 2),
    TotalLiabilities DECIMAL(18, 2),
    PANGiven CHAR(1),
    PersonalDetailsID INT,
    FOREIGN KEY (PersonalDetailsID) REFERENCES PersonalDetails(ID) DEFERRABLE INITIALLY DEFERRED
);
"""

# Execute the SQL statements to create tables
try:
    cur.execute(create_tables_sql)
    print("Tables created successfully")
except Exception as e:
    print("An error occurred while creating tables: ", e)

# Commit changes and close the connection
conn.commit()
cur.close()
conn.close()
