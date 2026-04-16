from fastapi.responses import JSONResponse


def ok(msg: str, result=None, **extra) -> JSONResponse:
    body = {"success": True, "msg": msg}
    if result is not None:
        body["result"] = result
    body.update(extra)
    return JSONResponse(status_code=200, content=body)


def err(status: int, msg: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"success": False, "msg": msg})


VALID_INVOICE_TYPES = {"FN", "FA", "RC", "RHF"}
VALID_TP_TYPES = {"1", "2"}
VALID_PAYMENT_TYPES = {"1", "2", "3", "4"}
VALID_FISCAL_CENTERS = {"DGC", "DMC", "DPMC"}
VALID_BOOL_FLAGS = {"0", "1"}
VALID_CURRENCIES = {"BIF", "USD", "EUR"}
VALID_MOVEMENT_TYPES = {"EN", "ER", "EI", "EAJ", "ET", "EAU", "SN", "SP", "SV", "SD", "SC", "SAJ", "ST", "SAU"}

INVOICE_REQUIRED = [
    "invoice_number", "invoice_date", "invoice_type", "tp_type", "tp_name",
    "tp_TIN", "tp_trade_number", "tp_phone_number", "tp_address_commune",
    "tp_address_quartier", "vat_taxpayer", "ct_taxpayer", "tl_taxpayer",
    "tp_fiscal_center", "tp_activity_sector", "tp_legal_form", "payment_type",
    "customer_name", "invoice_identifier", "invoice_items",
]

STOCK_REQUIRED = [
    "system_or_device_id", "item_code", "item_designation", "item_quantity",
    "item_measurement_unit", "item_purchase_or_sale_price",
    "item_purchase_or_sale_currency", "item_movement_type", "item_movement_date",
]


def check_required(data: dict, fields: list) -> list:
    return [f for f in fields if f not in data or (data[f] == "" and f not in ("item_movement_invoice_ref", "item_movement_description"))]


def is_numeric(value) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False
