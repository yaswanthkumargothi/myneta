import ast
import re
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
import openai
import numpy as np
import logging
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
import pgvector  # Ensure pgvector is imported

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Register numpy array adapter for PostgreSQL
def addapt_numpy_array(numpy_array):
    return AsIs(tuple(numpy_array))

register_adapter(np.ndarray, addapt_numpy_array)

# Database configuration
DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = 'mysecretpassword'
DB_PORT = '5432'

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    port=DB_PORT
)
cur = conn.cursor()

# Create PGVector extension if it doesn't exist
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
conn.commit()

# Function to run a query and return results as a list
def query_as_list(db, query):
    db.execute(query)
    res = db.fetchall()
    res = [el for sub in res for el in sub if el]
    res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
    return list(set(res))

# Fetch candidates and constituencies
candidates = query_as_list(cur, "SELECT name FROM personaldetails")
constituency = query_as_list(cur, "SELECT constituency FROM personaldetails")

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Create PGVector instance with a specified collection name
connection_string = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
collection_name = "politician_data"  # Specify your collection name here
vector_db = PGVector.from_texts(
    candidates + constituency,
    embeddings,
    connection_string=connection_string,
    collection_name=collection_name
)

# Close the connection
cur.close()
conn.close()
