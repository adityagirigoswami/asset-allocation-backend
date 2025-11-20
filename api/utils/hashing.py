from passlib.context import CryptContext
import warnings

# Suppress bcrypt version warning (compatibility issue between passlib and newer bcrypt)
warnings.filterwarnings("ignore", category=UserWarning, module="passlib.handlers.bcrypt")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(hashed_password: str, plain_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)