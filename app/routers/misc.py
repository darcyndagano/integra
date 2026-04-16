import json
from fastapi import APIRouter, Request, Depends
from sqlmodel import Session, select
from app.core.security import require_auth
from app.core.helpers import ok, err
from app.models.db import Invoice, get_session

router = APIRouter()


@router.post("/getInvoice/")
async def get_invoice(request: Request, session: Session = Depends(get_session), _=Depends(require_auth)):
    try:
        data = await request.json()
    except Exception:
        return err(400, "Le format de la chaine de caractère JSON est invalide.")

    identifier = data.get("invoice_identifier")
    if not identifier:
        return err(400, "Veuillez fournir un identifiant de la facture.")

    invoice = session.exec(select(Invoice).where(Invoice.invoice_identifier == identifier)).first()
    if not invoice:
        return err(400, "Identifiant de la facture inconnu.")

    raw = json.loads(invoice.raw_json)
    raw["invoice_registered_number"] = invoice.invoice_registered_number
    raw["invoice_registered_date"] = invoice.invoice_registered_date
    raw["cancelled_invoice"] = "Y" if invoice.cancelled else "N"

    return ok("Opération réussie", result={"invoices": [raw]})


@router.post("/cancelInvoice/")
async def cancel_invoice(request: Request, session: Session = Depends(get_session), _=Depends(require_auth)):
    try:
        data = await request.json()
    except Exception:
        return err(400, "Le format de la chaine de caractère JSON est invalide.")

    identifier = data.get("invoice_identifier")
    motif = data.get("cn_motif")

    if not identifier:
        return err(400, "Veuillez fournir un identifiant de la facture.")
    if not motif:
        return err(400, "Veuillez fournir le motif d'annulation.")

    invoice = session.exec(select(Invoice).where(Invoice.invoice_identifier == identifier)).first()
    if not invoice:
        return err(400, "Identifiant de la facture inconnu.")
    if invoice.cancelled:
        return err(400, "La facture que vous voulez annuler a été déjà annulée…")

    invoice.cancelled = True
    session.add(invoice)
    session.commit()

    return ok(f"La facture avec de l'identifiant {identifier} a été annulée avec succès!")


@router.post("/checkTIN/")
async def check_tin(request: Request, _=Depends(require_auth)):
    try:
        data = await request.json()
    except Exception:
        return err(400, "Le format de la chaine de caractère JSON est invalide.")

    tin = data.get("tp_TIN")
    if not tin:
        return err(400, "Veuillez fournir le NIF du contribuable.")

    # NIF simulé : valide si 10 chiffres
    if not tin.isdigit() or len(tin) != 10:
        return err(400, "NIF du contribuable inconnu.")

    return ok("Opération réussie", result={"taxpayer": [{"tp_name": "CONTRIBUABLE TEST"}]})
