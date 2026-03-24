import sys
import os
import uuid
from pydantic import ValidationError

# Add backend/src to path
sys.path.append(os.path.abspath('c:/Users/HP/Desktop/react/agriflow-hackathon/backend'))

try:
    from src.auth.schemas import UserCreateResponse, AuthUserOut
    from src.auth.models import Role, User, FarmerTier
    from src.auth.schemas import AuthUserOut

    print("Imported successful. Testing model validation...")

    user_dummy = {
        "uid": uuid.uuid4(),
        "first_name": "Adebayo",
        "last_name": "Olusola",
        "email": "adebayo@gmail.com",
        "role": Role.FARMER,
        "business_name": "Olusola Farms",
        "bvn_verified": False,
        "bank_verified": False,
        "is_active": True,
        # included computed fields if present:
        "full_name": "Adebayo Olusola",
        "trust_tier": "unrated"
    }

    response_dict = {
        "success": True,
        "message": "Registration successful",
        "data": {
            **user_dummy,
            "access_token": "token...",
            "refresh_token": "token..."
        }
    }

    # Validate output
    UserCreateResponse(**response_dict)
    print("Dummy test passed with dict directly")

except ValidationError as e:
    print("\n--- VALIDATION ERROR ---")
    print(e)
except Exception as e:
    print(f"\nUnexpected error: {e}")
