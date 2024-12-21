from app import app, db, ChatMessage
from sqlalchemy import inspect

def setup_chat():
    with app.app_context():
        inspector = inspect(db.engine)
        if 'chat_messages' not in inspector.get_table_names():
            print("Creating chat_messages table...")
            ChatMessage.__table__.create(db.engine)
            print("Chat messages table created successfully!")
        else:
            print("Chat messages table already exists!")

if __name__ == "__main__":
    setup_chat()
