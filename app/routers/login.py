from fastapi import APIRouter, Request
from app.core.config import TEST_CREDENTIALS
from app.core.security import create_token
from app.core.helpers import ok, err

router = APIRouter()


@router.post("/login/")
async def login(request: Request):
    try:
        data = await request.json()
    except Exception:
        return err(400, "Le format de la chaine de caractère JSON est invalide.")

    if "username" not in data:
        return err(400, "Veuillez fournir un nom d'utilisateur.")
    if "password" not in data:
        return err(400, "Veuillez fournir un mot de passe.")

    username = data["username"]
    password = data["password"]

    if TEST_CREDENTIALS.get(username) != password:
        return err(401, "Nom d'utilisateur ou mot de passe incorrect.")

    token = create_token(username)
    return ok("Opération réussie", result={"token": token})
