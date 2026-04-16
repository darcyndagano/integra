import jwt
import json
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from fastapi import HTTPException, Header
from app.core.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_SECONDS

import os

# Gestion de la persistance des clés RSA
KEY_FILE = "rsa_private.pem"

if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
        _private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )
else:
    _private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = _private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(KEY_FILE, "wb") as f:
        f.write(pem)

_public_key = _private_key.public_key()


def create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=JWT_EXPIRE_SECONDS)
    return jwt.encode({"username": username, "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide.")


def require_auth(authorization: str = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=403, detail="La clé API est manquante.")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=403, detail="La clé API est manquante.")
    return decode_token(parts[1])


def sign_result(result: dict) -> str:
    result_json = json.dumps(result, separators=(",", ":"))
    signature = _private_key.sign(
        result_json.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


def get_public_key_pem() -> str:
    return _public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
