# System message for verification agent
VERIFY_PREFIX = """You are an agent designed to verify the results of SQL queries.
Given the results of a SQL query, you should check for correctness, consistency, and completeness.
You should also ensure that the results make logical sense and adhere to any specified constraints.
If any issues are found, provide a detailed explanation of the problem and suggest possible corrections."""

verify_system_message = SystemMessage(content=VERIFY_PREFIX)


# System message for response agent
RESPONSE_PREFIX = """You are an agent designed to respond to the results of SQL query verification.
Given the verification results, you should check for necessary data and provide a meaningful response to the user's query.
If any issues are found in the verification results, provide a detailed explanation and suggest possible corrections."""

response_system_message = SystemMessage(content=RESPONSE_PREFIX)

import os
from dotenv import load_dotenv
from langchain.agents import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import PGVector
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings


import logging
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = 'mysecretpassword'
DB_PORT = '5432'

# Create database connection string
db_url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize database for LangChain
langchain_db = SQLDatabase.from_uri(db_url)

# Initialize Ollama with Llama2
#llm = Ollama(model="llama3.2")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)



# Create retriever tool
if vector_db:
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    retriever_tool = create_retriever_tool(
        retriever,
        name="search_proper_nouns",
        description="Use to look up correct spellings of names. Input should be a dictionary with a 'query' field containing the name to search for.",
    )
else:
    retriever_tool = None

examples = [
    {"input": "List all artists.", "query": "SELECT * FROM Artist;"},
    {
        "input": "who is the richest candidate?",
        "query": "SELECT name, totalassets FROM personaldetails ORDER BY totalassets DESC LIMIT 1;",
    },
    {
        "input": "How many people are contesting from ANDHERI EAST?",
        "query": "SELECT COUNT(*) FROM personaldetails WHERE constituency = 'ANDHERI EAST';",
    },
    {
        "input": "Who has the highest number of cases registered on him?",
        "query": "SELECT name, numberofcases FROM personaldetails ORDER BY numberofcases DESC LIMIT 1;",
    },
    {
        "input": "How many assets are there in the spouse's name of Mahendra Hari Dalvi?",
        "query": """SELECT COUNT(*) 
                    FROM immovableassets ia
                    JOIN personaldetails pd ON ia.personaldetailsid = pd.id
                    WHERE pd.name = 'Mahendra Hari Dalvi' 
                    AND ia.spouse IS NOT NULL;""",
    },
    {
        "input": "In which companies did Mahendra Hari Dalvi invest in?",
        "query": """SELECT ia.self 
                    FROM movableassets ma
                    JOIN personaldetails pd ON ma.personaldetailsid = pd.id
                    WHERE pd.name = 'Mahendra Hari Dalvi' 
                    AND ma.description LIKE '%Shares in companies%';""",
    },
    {
        "input": "How much gold did Mahendra Hari Dalvi have?",
        "query": """SELECT ma.self 
                  FROM movableassets ma
                  JOIN personaldetails pd ON ma.personaldetailsid = pd.id
                  WHERE pd.name = 'Mahendra Hari Dalvi' 
                AND ma.description LIKE '%Jewellery%';""",
    },
]

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Use existing PGVector instance
vector_db = PGVector.from_existing_index(
    embedding=embeddings,
    collection_name="politician_data",  # Use the specified collection name
    connection_string=db_url  # Pass the connection string explicitly
)

# System message for SQL agent
SQL_PREFIX = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

To start you should ALWAYS look at the tables in the database to see what you can query.
Do NOT skip this step.

If the question does not seem related to the database, just return "I don't know" as the answer.

Here are some examples of user inputs and their corresponding SQL queries:

{examples}"""

system_message = SystemMessage(content=SQL_PREFIX)


# Create the prompt template correctly
prompt_template = PromptTemplate(template=SQL_PREFIX, input_variables=[])
system_message_prompt = SystemMessagePromptTemplate(prompt=prompt_template)


full_prompt = ChatPromptTemplate.from_messages(
    [
        system_message_prompt,
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)


# Create enhanced context for the personaldetails table
PERSONALDETAILS_CONTEXT = """
The 'personaldetails' table contains comprehensive information about politicians or public figures:
- 'name': Full name of the individual
- 'partycode': Political party the individual represents
- 'education': Educational background of the individual
- 'numberofcases': Number of civil criminal cases the individual is involved in
- 'totalassets': Total monetary assets of the individual
- 'totalliabilities': Total monetary liabilities of the individual
- 'constituency': The electoral constituency the individual represents

When querying this table, consider:
- Civil and criminal cases are numeric counts
- Assets and liabilities are monetary values
- Constituency represents the specific electoral region

Note: start with 'personaldetails' table to get an overview of the candidates personal information.
      name is a unique identifier for each candidate.
      A 'candidate' refers to an individual listed in this table, typically a political aspirant or elected representative.
      Do not query 'users', 'chat_messages', 'user' tables.
"""

# Create detailed context for asset and liability tables
ASSETS_LIABILITIES_CONTEXT = """
Additional Asset and Liability Tables provide detailed financial information:

1. 'immovableassets' Table:
   - Includes details of non-movable properties owned by the candidate
   - Covers assets for the candidate, spouse, and dependents
   - Typically includes land, buildings, real estate properties
   - Columns may include description, value, ownership details

2. 'movableassets' Table:
   - Contains information about movable assets owned by the candidate
   - Includes assets for the candidate, spouse, and dependents
   - May cover vehicles, investments, stocks, jewelry, and other mobile valuables
   - Columns likely include description, value, ownership details

3. 'liabilities' Table:
   - Detailed breakdown of financial liabilities
   - Covers liabilities for the candidate, spouse, and dependents
   - Includes various types of loans, mortgages, and financial obligations
   - Columns may include liability description, value, ownership details

Querying Tips:
- When investigating a candidate's financial details, cross-reference these tables
- Asset and liability values are detailed across these tables, complementing the summary in 'personaldetails'
- You can join these tables with 'personaldetails' using the candidate's name
- Values represent individual and family financial status

Example Use Cases:
- Detailed asset breakdown by type
- Comparison of declared vs. actual assets
- Identifying significant financial interests
- Analyzing financial transparency of candidates
"""

# Create SQLDatabaseToolkit with enhanced context
toolkit = SQLDatabaseToolkit(
    db=langchain_db, 
    llm=llm,
    custom_table_context={
        "personaldetails": PERSONALDETAILS_CONTEXT,
        "immovableassets": ASSETS_LIABILITIES_CONTEXT,
        "movableassets": ASSETS_LIABILITIES_CONTEXT,
        "liabilities": ASSETS_LIABILITIES_CONTEXT
    }
)

# Create the SQL agent
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    prompt=full_prompt,
    agent_type="openai-tools",
    verbose= True  # Add system message here
)

def get_table_info():
    """Get information about all tables in the database"""
    return langchain_db.get_table_info()

def natural_language_to_sql(question: str):
    """
    Convert natural language question to SQL and execute it
    
    Args:
        question (str): Natural language question about the database
    
    Returns:
        dict: Contains the query result
    """
    try:
        logging.debug(f"Input question: {question}")
        
        # Use invoke instead of run
        config = {"configurable": {"language": "en"}}
        response = agent.invoke({"input": question}, config)
        
        # Extract the output from the response
        result_output = response.get('output', 'No output found')
        
        logging.debug(f"Agent response: {result_output}")
        
        
        return {
            "query": "Generated by SQL Agent",
            "result": result_output,
            "success": True
        }
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return {
            "query": None,
            "result": f"Error: {str(e)}",
            "verification": None,
            "response": None,
            "success": False
        }

def format_result(result):
    """Format the query result for better readability"""
    if isinstance(result, list):
        return "\n".join([str(item) for item in result])
    return str(result)

# Function to find proper nouns in the query
def find_proper_nouns(query_text):
    # Use a simple regex to find capitalized words (proper nouns)
    proper_nouns = re.findall(r'\b[A-Z][a-z]*\b', query_text)
    return proper_nouns

# Function to get proper nouns from PGVector using retriever tool of langchain
def correct_names(query_text):
    """
    Correct proper nouns using the retriever tool.
    
    Args:
        query_text: Text containing names to be corrected
        
    Returns:
        str: Corrected text or original text if correction fails
    """
    try:
        if not retriever_tool:
            logging.warning("Retriever tool not available")
            return query_text
            
        # Prepare input in the correct format
        tool_input = {"query": query_text}
        
        # Use the retriever tool
        results = retriever_tool.invoke(tool_input)
        return results
    except Exception as e:
        logging.error(f"Error in correct_names: {e}")
        return query_text

def main():
    # Print available tables and their schema
    print("\n=== Database Schema ===")
    print(get_table_info())
    print("\n=== Example Questions ===")
    print("1. Show all users")
    print("2. Count total messages")
    print("3. Find latest messages")
    print("\nType 'quit' to exit\n")
    
    while True:
        # Get user input
        question = input("\nEnter your question: ")
        
        if question.lower() == 'quit':
            break
        
        # Process the question
        result = natural_language_to_sql(question)
        
        # Print results
        print("\n=== Query Result ===")
        print(format_result(result["result"]))
        print("\n" + "="*50)

if __name__ == "__main__":
    main()