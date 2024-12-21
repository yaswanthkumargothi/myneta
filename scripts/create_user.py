from app import app, db, User

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Create a test user
    test_user = User(username='admin', password='admin123')
    db.session.add(test_user)
    db.session.commit()
    print("Test user created successfully!")
