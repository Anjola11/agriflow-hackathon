import asyncio
import sys
from pathlib import Path
from sqlmodel import select
from sqlalchemy.exc import DatabaseError


if __package__ is None or __package__ == "":
    backend_root = Path(__file__).resolve().parents[2]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

from src.auth.models import User, Role
from src.bank.models import Bank
from src.bank.seedbank import banks as bank_seed_data
from src.db.main import async_session_maker
from src.utils.auth import generate_password_hash


FARMER_EMAIL_PASSWORDS = {
    "farmer01@agriflow.com": "Farmer01!Pass",
    "farmer02@agriflow.com": "Farmer02!Pass",
    "farmer03@agriflow.com": "Farmer03!Pass",
    "farmer04@agriflow.com": "Farmer04!Pass",
    "farmer05@agriflow.com": "Farmer05!Pass",
    "farmer06@agriflow.com": "Farmer06!Pass",
    "farmer07@agriflow.com": "Farmer07!Pass",
    "farmer08@agriflow.com": "Farmer08!Pass",
    "farmer09@agriflow.com": "Farmer09!Pass",
    "farmer10@agriflow.com": "Farmer10!Pass",
    "farmer11@agriflow.com": "Farmer11!Pass",
    "farmer12@agriflow.com": "Farmer12!Pass",
    "farmer13@agriflow.com": "Farmer13!Pass",
    "farmer14@agriflow.com": "Farmer14!Pass",
    "farmer15@agriflow.com": "Farmer15!Pass",
    "farmer16@agriflow.com": "Farmer16!Pass",
    "farmer17@agriflow.com": "Farmer17!Pass",
    "farmer18@agriflow.com": "Farmer18!Pass",
    "farmer19@agriflow.com": "Farmer19!Pass",
    "farmer20@agriflow.com": "Farmer20!Pass",
}


FIRST_NAMES = [
    "Amina", "Chinedu", "Ngozi", "Yusuf", "Bola",
    "Emeka", "Kehinde", "Fatima", "Tosin", "Ifeanyi",
    "Hadiza", "Seun", "Uche", "Mariam", "Tunde",
    "Blessing", "Kabiru", "Adaeze", "Sodiq", "Joy",
]

LAST_NAMES = [
    "Okafor", "Adeyemi", "Ibrahim", "Nwosu", "Balogun",
    "Eze", "Olawale", "Yahaya", "Afolabi", "Onyeka",
    "Bello", "Akinola", "Umeh", "Suleiman", "Adetola",
    "Okoro", "Garba", "Nnamdi", "Ojo", "Obi",
]

BUSINESS_NAMES = [
    "GreenSprout Farms", "SunYield Agro", "Riverbend Harvests", "PrimeCrop Fields", "GoldenRoot Agro",
    "FreshBarn Cooperative", "Savannah Produce", "EarthRise Farm Hub", "HarvestLink Farms", "BlueSoil Growers",
    "AgroPeak Ventures", "TerraNova Farms", "FieldNest Agro", "RainRich Farms", "CrownLeaf Agro",
    "HarvestWave Foods", "RuralEdge Farms", "PureCrop Collective", "FarmTrust Produce", "AgriVista Growers",
]

# Mixes trust tiers: <50 (Unrated), 50-74 (Emerging), >=75 (Verified).
TRUST_SCORES = [32, 38, 41, 45, 49, 52, 56, 60, 64, 69, 72, 74, 75, 78, 82, 86, 90, 94, 97, 100]


async def get_active_bank_codes() -> list[str]:
    async with async_session_maker() as session:
        statement = select(Bank).where(Bank.active == True)
        result = await session.exec(statement)
        active_banks = result.all()

    if active_banks:
        return [bank.code for bank in active_banks]

    # Fallback to seed data in case bank table is empty.
    return [bank.get("code") for bank in bank_seed_data if bank.get("active")]


async def seed_farmers() -> None:
    bank_codes = await get_active_bank_codes()
    if not bank_codes:
        print("No bank codes found. Seed banks first.")
        return

    new_farmers: list[User] = []

    async with async_session_maker() as session:
        for idx, (email, plain_password) in enumerate(FARMER_EMAIL_PASSWORDS.items(), start=1):
            existing_statement = select(User).where(User.email == email)
            existing_result = await session.exec(existing_statement)
            existing_user = existing_result.first()

            if existing_user:
                continue

            first_name = FIRST_NAMES[idx - 1]
            last_name = LAST_NAMES[idx - 1]
            business_name = BUSINESS_NAMES[idx - 1]
            bank_code = bank_codes[(idx - 1) % len(bank_codes)]

            # Generate deterministic fake account/BVN values for repeatable local tests.
            account_number = f"{3000000000 + idx:010d}"
            bvn_number = f"{22000000000 + idx:011d}"

            farmer = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                business_name=business_name,
                password_hash=generate_password_hash(plain_password),
                role=Role.FARMER,
                bvn=bvn_number,
                bvn_verified=True,
                bvn_name=f"{first_name} {last_name}",
                trust_score=TRUST_SCORES[idx - 1],
                account_number=account_number,
                bank_code=bank_code,
                account_name=business_name,
                bank_verified=True,
                is_active=True,
            )

            new_farmers.append(farmer)

        if not new_farmers:
            print("No new farmers added. Seed emails already exist.")
            return

        try:
            session.add_all(new_farmers)
            await session.commit()
            print(f"Successfully seeded {len(new_farmers)} farmers.")
            print("Use FARMER_EMAIL_PASSWORDS in this file for login testing.")
        except DatabaseError as exc:
            await session.rollback()
            print(f"Failed to seed farmers: {exc}")


if __name__ == "__main__":
    asyncio.run(seed_farmers())
