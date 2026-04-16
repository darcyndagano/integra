from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.models.db import Invoice, StockMovement, get_session
import os

router = APIRouter()

# On définit le chemin des templates
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def dashboard(request: Request, session: Session = Depends(get_session)):
    # Récupération des données
    invoices = session.exec(select(Invoice).order_by(Invoice.id.desc()).limit(50)).all()
    movements = session.exec(select(StockMovement).order_by(StockMovement.id.desc()).limit(50)).all()
    
    cancelled_count = session.exec(select(Invoice).where(Invoice.cancelled == True)).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "invoices": invoices,
        "movements": movements,
        "cancelled_count": len(cancelled_count)
    })
