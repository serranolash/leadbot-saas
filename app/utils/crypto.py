import json
from cryptography.fernet import Fernet
from ..settings import settings

fernet = Fernet(settings.CRYPTO_FERNET_KEY.encode())

def encrypt_obj(obj: dict) -> str:
    return fernet.encrypt(json.dumps(obj).encode()).decode()

def decrypt_obj(token: str) -> dict:
    return json.loads(fernet.decrypt(token.encode()).decode())
