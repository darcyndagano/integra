from fastapi import APIRouter, Request, Depends
from sqlmodel import Session
from app.core.security import require_auth
from app.core.helpers import ok, err, VALID_MOVEMENT_TYPES, VALID_CURRENCIES, STOCK_REQUIRED, check_required
from app.models.db import StockMovement, get_session

router = APIRouter()

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


@router.post("/AddStockMovement/")
async def add_stock_movement(request: Request, session: Session = Depends(get_session), _=Depends(require_auth)):
    try:
        data = await request.json()
    except Exception:
        return err(400, "Le format de la chaine de caractère JSON est invalide.")

    missing = check_required(data, STOCK_REQUIRED)
    if missing:
        return err(400, f"Veuillez fournir tous les champs obligatoires. Champ(s) manquant(s): {', '.join(missing)}")

    if not data.get("system_or_device_id", "").startswith("ws"):
        return err(400, "Identifiant système incorrect.")

    if data.get("item_movement_type") not in VALID_MOVEMENT_TYPES:
        return err(400, (
            "Veuillez fournir un type de mouvement valide. Le type de mouvement de stock doit être "
            "inclu dans les types suivants : EN, ER, EI, EAJ, ET, EAU, SN, SP, SV, SD, SC, SAJ, ST, SAU."
        ))

    currency = data.get("item_purchase_or_sale_currency", "BIF")
    if currency not in VALID_CURRENCIES:
        return err(400, "La valeur du champ devise est incorrecte.")

    movement = StockMovement(
        system_or_device_id=data["system_or_device_id"],
        item_code=data["item_code"],
        item_designation=data["item_designation"],
        item_quantity=str(data["item_quantity"]),
        item_measurement_unit=data["item_measurement_unit"],
        item_purchase_or_sale_price=str(data["item_purchase_or_sale_price"]),
        item_purchase_or_sale_currency=currency,
        item_movement_type=data["item_movement_type"],
        item_movement_invoice_ref=data.get("item_movement_invoice_ref", ""),
        item_movement_description=data.get("item_movement_description", ""),
        item_movement_date=data["item_movement_date"],
    )
    session.add(movement)
    session.commit()

    return ok("La transaction a été ajoutée avec succès!")
