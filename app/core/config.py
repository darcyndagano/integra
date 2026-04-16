import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ebms_mock.db")
JWT_SECRET = os.getenv("JWT_SECRET", "ebms_mock_secret_change_me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRE_SECONDS", "60"))

# Credentials de test (simule les comptes OBR)
TEST_CREDENTIALS = {
    os.getenv("EBMS_USERNAME", "test_user"): os.getenv("EBMS_PASSWORD", "test_pass"),
}
