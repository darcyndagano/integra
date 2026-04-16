from fastapi import FastAPI
from app.models.db import create_db
from app.routers import login, invoice, misc, stock, dashboard
from app.core.security import get_public_key_pem

app = FastAPI(title="EBMS OBR Mock Server", version="0.5")


@app.on_event("startup")
def on_startup():
    create_db()


@app.get("/ebms_api/public_key/")
def public_key():
    return {"public_key": get_public_key_pem()}


app.include_router(login.router, prefix="/ebms_api")
app.include_router(invoice.router, prefix="/ebms_api")
app.include_router(misc.router, prefix="/ebms_api")
app.include_router(stock.router, prefix="/ebms_api")
app.include_router(dashboard.router)
