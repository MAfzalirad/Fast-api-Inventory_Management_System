import os
from dotenv import load_dotenv
from models import Users
from dependencies import bcrypt_context
from database import SessionLocal

load_dotenv()


def create_admin(db):
    user_model = db.query(Users).filter(Users.role == 'admin').first()
    if user_model is None:
        admin_user = Users(
            username=os.getenv('ADMIN_USERNAME'),
            email=os.getenv('ADMIN_EMAIL'),
            first_name='Admin',
            last_name='User',
            hash_password=bcrypt_context.hash(os.getenv('ADMIN_PASSWORD')),
            is_active=True,
            role='admin'
        )
        db.add(admin_user)
        db.commit()

if __name__ == '__main__':
    db = SessionLocal()
    try:
        create_admin(db)
    finally:
        db.close()