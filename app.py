from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import inspect
from scripts.text_to_sql import natural_language_to_sql, correct_names, find_proper_nouns
# from scripts.qdrant_client import QdrantClient
# from scripts.qdrant_client.models import PointStruct
# from scripts.sentence_transformers import SentenceTransformer
import numpy as np

app = Flask("Myneta Chat")
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mysecretpassword@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def inspect_db():
    """Helper function to inspect database tables"""
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("Available tables:", tables)
        for table in tables:
            print(f"\nTable: {table}")
            print("Columns:")
            for column in inspector.get_columns(table):
                print(f"  {column['name']}: {column['type']}")
        return "\n".join([f"Table: {table}" for table in tables])  # Return as string
    except Exception as e:
        print(f"Error inspecting database: {str(e)}")
        return "No tables found"

# Initialize database inspector 
with app.app_context():
    available_tables = inspect_db()

# Initialize Qdrant client and sentence transformer
# qdrant = QdrantClient("localhost", port=6333)
# model = SentenceTransformer('all-MiniLM-L6-v2')
collection_name = "chat_messages"

# Create collection if it doesn't exist
def init_qdrant():
    try:
        # qdrant.create_collection(
        #     collection_name=collection_name,
        #     vectors_config={"size": 384, "distance": "Cosine"}
        # )
        pass
    except Exception as e:
        print(f"Collection might already exist: {e}")

def embed_text(text):
    # return model.encode(text).tolist()
    pass

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    chat_messages = db.relationship('ChatMessage', backref='author', lazy=True)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_query = db.Column(db.Boolean, default=False)
    query_result = db.Column(db.Text, nullable=True)
    #vector = db.Column(db.ARRAY(db.Float))  # Add vector column

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    messages = ChatMessage.query.order_by(ChatMessage.timestamp.desc()).limit(50).all()
    return render_template('index.html', messages=messages)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    content = request.form.get('content')
    if content:
        if content.lower().startswith('/query '):
            question = content[7:]
            proper_nouns = find_proper_nouns(question)
            corrected_question = question
            if proper_nouns:
                corrected_names = correct_names(question)
                if corrected_names and isinstance(corrected_names, str):
                    corrected_question = corrected_names
            
            try:
                result = natural_language_to_sql(corrected_question)
                query_result = result.get('result', 'No result available') if isinstance(result, dict) else str(result)
                
                message = ChatMessage(
                    content=f"Query: {corrected_question}",
                    user_id=current_user.id,
                    is_query=True,
                    query_result=f"Result: {query_result}"
                )
            except Exception as e:
                message = ChatMessage(
                    content=f"Query: {corrected_question}",
                    user_id=current_user.id,
                    is_query=True,
                    query_result=f"Error executing query: {str(e)}"
                )
        else:
            message = ChatMessage(
                content=content,
                user_id=current_user.id
            )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': {
                'content': message.content,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'username': current_user.username,
                'is_query': message.is_query,
                'query_result': message.query_result
            }
        })
    return jsonify({'status': 'error', 'message': 'Empty message'})

@app.route('/search_messages', methods=['POST'])
@login_required
def search_messages():
    query = request.form.get('query')
    if not query:
        return jsonify({'status': 'error', 'message': 'Empty query'})

    # Generate embedding for the search query
    # search_vector = embed_text(query)

    # Search in Qdrant
    # search_results = qdrant.search(
    #     collection_name=collection_name,
    #     query_vector=search_vector,
    #     limit=5
    # )

    # Get messages from database
    # message_ids = [hit.id for hit in search_results]
    # messages = ChatMessage.query.filter(ChatMessage.id.in_(message_ids)).all()
    
    # Format results
    results = []
    # for message in messages:
    #     results.append({
    #         'content': message.content,
    #         'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
    #         'username': message.author.username,
    #         'is_query': message.is_query,
    #         'query_result': message.query_result
    #     })

    return jsonify({'status': 'success', 'results': results})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt - Username: {username}")  # Debug log
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # In production, use proper password hashing
            login_user(user)
            print(f"Login successful for user: {username}")  # Debug log
            return redirect(url_for('index'))
        else:
            print(f"Login failed for user: {username}")  # Debug log
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/flowchart')
def flowchart():
    return send_file('scripts/flowchart.png', mimetype='image/png')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_qdrant()
    app.run(debug=True)