import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends
from sqlmodel import Session, select
from app.core.security import require_auth, sign_result
from app.core.helpers import (
    ok, err,
    VALID_INVOICE_TYPES, VALID_TP_TYPES, VALID_PAYMENT_TYPES,
    VALID_BOOL_FLAGS, VALID_CURRENCIES, INVOICE_REQUIRED,
    check_required, is_numeric,
)
from app.models.db import Invoice, get_session

router = APIRouter()

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _validate_invoice(data: dict, session: Session):
    missing = check_required(data, INVOICE_REQUIRED)
    if missing:
        return err(400, f"Veuillez fournir tous les champs obligatoires. Champ(s) manquant(s): {', '.join(missing)}")

    if len(data.get("invoice_number", "")) > 30:
        return err(400, "La taille du numéro de la facture excède celle du système (max 30 caractères)")

    try:
        inv_date = datetime.strptime(data["invoice_date"], DATE_FORMAT)
        if inv_date > datetime.now():
            return err(400, "La date de facturation fournie est supérieur à la date actuelle.")
    except ValueError:
        return err(400, "Le format de la date de facturation est incorrecte.")

    if data.get("invoice_type") not in VALID_INVOICE_TYPES:
        return err(400, "La valeur du champ type de facture doit être comprise entre : « FN » , « RC » ou « RHF ».")

    if data.get("tp_type") not in VALID_TP_TYPES:
        return err(400, "La valeur du champ type contribuable (tp_type) est incorrecte. La valeur doit être comprise entre '1' ou '2'.")

    if len(data.get("tp_name", "")) > 100:
        return err(400, "La taille du champ nom du contribuable excède celle du système (max 100 caractères)")

    if len(data.get("tp_TIN", "")) > 15:
        return err(400, "La taille du champ NIF du contribuable excède celle du système (max 15 caractères)")

    if data.get("vat_taxpayer") not in VALID_BOOL_FLAGS:
        return err(400, "La valeur du champ assujetti à la TVA est incorrecte. La valeur doit être comprise entre '0' ou '1'.")

    if data.get("ct_taxpayer") not in VALID_BOOL_FLAGS:
        return err(400, "La valeur du champ assujetti à la taxe de consommation est incorrecte. La valeur doit être comprise entre '0' ou '1'.")

    if data.get("tl_taxpayer") not in VALID_BOOL_FLAGS:
        return err(400, "La valeur du champ assujetti à la prélèvement forfaitaire libératoire est incorrecte. La valeur doit être comprise entre '0' ou '1'.")

    if data.get("payment_type") not in VALID_PAYMENT_TYPES:
        return err(400, "Le format ou la valeur du champ type de payement (payment_type) est incorrecte. La valeur doit être comprise entre '1','2',3 ou '4'.")

    if data.get("invoice_currency") and data["invoice_currency"] not in VALID_CURRENCIES:
        return err(400, "La valeur du champ devise est incorrecte.")

    if data.get("customer_TIN") and len(data["customer_TIN"]) > 50:
        return err(400, "La taille du champ NIF client excède celle du système.")

    # Vérif invoice_identifier format: NIF/system_id/datetime/invoice_number
    # Le numéro de facture peut lui-même contenir "/" → on split avec maxsplit=3
    identifier = data.get("invoice_identifier", "")
    parts = identifier.split("/", 3)
    if len(parts) < 4:
        return err(400, "Le format de l'identifiant de la facture incorrecte. Il manque certains éléments")
    nif_part, sys_part, date_part, _ = parts
    if not nif_part.isdigit():
        return err(400, "Le format de l'identifiant de la facture incorrecte. Le NIF fourni est incorrecte")
    if not sys_part.startswith("ws"):
        return err(400, "Le format de l'identifiant de la facture incorrecte. Identifiant système ou numéro de serie incorrecte")
    if len(date_part) != 14 or not date_part.isdigit():
        return err(400, "Le format de l'identifiant de la facture incorrecte. Date fournie incorrecte")

    # Vérif doublons
    existing = session.exec(select(Invoice).where(Invoice.invoice_number == data["invoice_number"])).first()
    if existing:
        return err(400, "Une facture avec le même numéro de facture existe déjà.")

    existing_id = session.exec(select(Invoice).where(Invoice.invoice_identifier == identifier)).first()
    if existing_id:
        return err(400, "Une facture avec le même identifiant existe déjà.")

    # Validation items
    items = data.get("invoice_items", [])
    if not isinstance(items, list) or len(items) == 0:
        return err(400, "Veuillez fournir tous les champs obligatoires. Champ(s) manquant(s): invoice_items")

    for i, item in enumerate(items, 1):
        if len(item.get("item_designation", "")) > 500:
            return err(400, f"La taille du champ Désignation de l'article excède celle du système (max 500 caractère). Pour la ligne numéro: {i}")
        if not is_numeric(item.get("item_quantity")):
            return err(400, f"La valeur du champ Quantité de l'article ne correspond pas à un nombre. Pour la ligne numéro: {i}")
        if not is_numeric(item.get("item_price")):
            return err(400, f"La valeur du champ prix de l'article ne correspond pas à un nombre. Pour la ligne numéro: {i}")
        if not is_numeric(item.get("item_price_nvat")):
            return err(400, f"La valeur du champ prix ex usine ne correspond pas à un nombre. Pour la ligne numéro: {i}")
        if not is_numeric(item.get("item_ct", "0")):
            return err(400, f"La valeur du champ Taxe de consommation ne correspond pas à un nombre. Pour la ligne numéro: {i}")

    return None


@router.post("/addInvoice_confirm/")
async def add_invoice(request: Request, session: Session = Depends(get_session), _=Depends(require_auth)):
    try:
        data = await request.json()
    except Exception:
        return err(400, "Le format de la chaine de caractère JSON est invalide.")

    validation_error = _validate_invoice(data, session)
    if validation_error:
        return validation_error

    registered_number = str(uuid.uuid4().int)[:7]
    registered_date = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    result = {
        "invoice_number": data["invoice_number"],
        "invoice_registered_number": registered_number,
        "invoice_registered_date": registered_date,
    }

    signature = sign_result(result)

    invoice = Invoice(
        invoice_number=data["invoice_number"],
        invoice_identifier=data["invoice_identifier"],
        invoice_date=data["invoice_date"],
        invoice_type=data["invoice_type"],
        invoice_registered_number=registered_number,
        invoice_registered_date=registered_date,
        electronic_signature=signature,
        raw_json=json.dumps(data),
    )
    session.add(invoice)
    session.commit()

    return ok(
        "La facture a été ajoutée avec succès!",
        result=result,
        electronique_signature=signature,
    )
