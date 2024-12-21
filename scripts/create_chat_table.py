from app import app, db, User, ChatMessage
from sqlalchemy import inspect

def create_chat_table():
    with app.app_context():
        inspector = inspect(db.engine)
        if 'chat_messages' not in inspector.get_table_names():
            ChatMessage.__table__.create(db.engine)
            print("Chat messages table created successfully!")
        else:
            print("Chat messages table already exists!")

if __name__ == "__main__":
    create_chat_table()
