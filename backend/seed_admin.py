import asyncio
import uuid
import sys
import os

sys.path.append(os.path.abspath('c:/Users/HP/Desktop/react/agriflow-hackathon/backend'))

from src.db.main import async_session_maker, init_db
from src.auth.models import Admin
from src.utils.auth import generate_password_hash
from sqlmodel import select

async def seed_admin():
    print("Initializing Database...")
    await init_db()
    
    async with async_session_maker() as session:
        # Check if already exists
        statement = select(Admin).where(Admin.email == "admin@agriflow.ng")
        result = await session.exec(statement)
        existing_admin = result.first()

        if existing_admin:
            print("Admin already exists in database.")
            return

        print("Creating admin account 'admin@agriflow.ng' with pass 'Admin123!'...")
        hashed_password = generate_password_hash("Admin123!")
        
        new_admin = Admin(
            uid=uuid.uuid4(),
            first_name="App",
            last_name="Admin",
            email="admin@agriflow.ng",
            password_hash=hashed_password,
            is_active=True
        )

        try:
            session.add(new_admin)
            await session.commit()
            print("Successfully seeded Admin user!")
        except Exception as e:
            await session.rollback()
            print(f"Error seeding admin: {e}")

if __name__ == "__main__":
    asyncio.run(seed_admin())
