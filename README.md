# Myneta Chat

## Overview

Myneta Chat is a chat-based application designed to provide users with easy access to detailed information about Indian politicians. Leveraging data from [Myneta.info](https://myneta.info), the platform simplifies the process of understanding election affidavits by eliminating complex jargon and excessive data, ensuring that users can effortlessly stay informed about politicians' assets, liabilities, and other relevant details.

## Features

- **Interactive Chat Interface:** Engage with a user-friendly chat system that answers queries about politicians without the need to navigate through multiple web pages.
- **Comprehensive Data Integration:** Access information on immovable and movable assets, liabilities, legal cases, constituency details, age, political party affiliations, and more.
- **Advanced Search Capabilities:** Utilize vector search powered by Pgvector and OpenAI embeddings to find information based on names and constituencies, even with variations and inconsistencies.
- **Database Management:** Robust database design to handle extensive data with numerous text-based columns, ensuring efficient data retrieval and management.
- **Future Enhancements:** Plans to incorporate automated web scraping, external news-based searches, and investigative agents to uncover deeper insights into political corruption.

## Technology Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL with Pgvector extension
- **AI & Machine Learning:** OpenAI embeddings, Langchain framework
- **Web Scraping:** Firecrawl framework
- **Frontend:** HTML, CSS, JavaScript
- **Other Tools:** Langchain, PGVector for vector storage

## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/myneta.git
    cd myneta
    ```

2. **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up the Database:**
    - Ensure PostgreSQL is installed and running.
    - Create a new database:
        ```sql
        CREATE DATABASE myneta_chat;
        ```

5. **Run Database Schema Setup:**
    ```bash
    python schema_run.py
    ```

6. **Run Embeddings Creation:**
    ```bash
    python create_embeddings.py
    ```

7. **Configure Environment Variables:**
    - Create a [.env](http://_vscodecontentref_/0) file and add necessary configurations:
        ```
        FLASK_APP=app.py
        FLASK_ENV=development
        DATABASE_URL=postgresql://postgres:mysecretpassword@localhost/myneta_chat
        OPENAI_API_KEY=your_openai_api_key
        ADMIN_USERNAME=admin
        ADMIN_PASSWORD=adminpassword
        ```

8. **Run the Application:**
    ```bash
    flask run
    ```

## Usage

- Navigate to `http://localhost:5000` in your web browser.
- **Admin Login:**
    - **Username:** admin
    - **Password:** adminpassword
- Register or log in to access the chat interface.
- Use the chat to inquire about various politicians' assets, liabilities, and other relevant information.
- The system leverages advanced search and AI capabilities to provide accurate and relevant responses.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- [Myneta.info](https://myneta.info) for providing comprehensive data on Indian politicians.
- OpenAI for their powerful language models.
- The contributors of the various frameworks and libraries used in this project.
