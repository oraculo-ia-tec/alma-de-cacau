"""
Adapter para integração com a API Asaas v3.
Documentação: https://docs.asaas.com/reference

Autenticação: header 'access_token' com a chave da conta.
Nunca armazenar dados de cartão — usar tokenização via Asaas Checkout.
"""
import os
import httpx
from typing import Optional
from datetime import date, timedelta


ASAAS_API_KEY = os.getenv("ASAAS_API_KEY", "")
ASAAS_ENV = os.getenv("ASAAS_ENV", "sandbox")  # "sandbox" ou "production"

_BASE_URLS = {
    "sandbox": "https://api-sandbox.asaas.com/v3",
    "production": "https://api.asaas.com/v3",
}


def _base_url() -> str:
    return _BASE_URLS.get(ASAAS_ENV, _BASE_URLS["sandbox"])


def _headers() -> dict:
    return {
        "access_token": ASAAS_API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "AlmaDeCacau/1.0.0",
    }


# ──────────────────────────────────────────────
# CLIENTES
# ──────────────────────────────────────────────

def create_customer(
    name: str,
    cpf_cnpj: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    external_reference: Optional[str] = None,
) -> tuple[Optional[dict], Optional[str]]:
    """
    Cria ou localiza um cliente no Asaas.
    Retorna (customer_data, error_message).
    CPF/CNPJ é usado para evitar duplicatas antes da criação.
    """
    # Verificar duplicidade por cpfCnpj antes de criar
    existing, err = find_customer_by_cpf_cnpj(cpf_cnpj)
    if err:
        return None, err
    if existing:
        return existing, None

    payload = {
        "name": name,
        "cpfCnpj": cpf_cnpj,
        "notificationDisabled": False,
    }
    if email:
        payload["email"] = email
    if phone:
        payload["mobilePhone"] = phone
    if external_reference:
        payload["externalReference"] = external_reference

    try:
        resp = httpx.post(
            f"{_base_url()}/customers",
            json=payload,
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Asaas HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def find_customer_by_cpf_cnpj(cpf_cnpj: str) -> tuple[Optional[dict], Optional[str]]:
    """Busca cliente existente por CPF/CNPJ. Retorna o primeiro resultado ou None."""
    try:
        resp = httpx.get(
            f"{_base_url()}/customers",
            params={"cpfCnpj": cpf_cnpj},
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("data", [])
        return (items[0] if items else None), None
    except httpx.HTTPStatusError as e:
        return None, f"Asaas HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


# ──────────────────────────────────────────────
# COBRANÇAS
# ──────────────────────────────────────────────

def create_payment(
    asaas_customer_id: str,
    amount: float,
    billing_type: str,
    description: str,
    external_reference: Optional[str] = None,
    due_date: Optional[str] = None,
) -> tuple[Optional[dict], Optional[str]]:
    """
    Cria uma cobrança no Asaas.

    billing_type: "PIX" | "BOLETO" | "CREDIT_CARD" | "UNDEFINED"
    due_date: ISO date string (YYYY-MM-DD). Padrão: hoje + 1 dia.
    Retorna (payment_data, error_message).
    """
    if not due_date:
        due_date = (date.today() + timedelta(days=1)).isoformat()

    payload = {
        "customer": asaas_customer_id,
        "billingType": billing_type.upper(),
        "value": round(float(amount), 2),
        "dueDate": due_date,
        "description": description,
    }
    if external_reference:
        payload["externalReference"] = external_reference

    try:
        resp = httpx.post(
            f"{_base_url()}/payments",
            json=payload,
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Asaas HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def get_payment(asaas_payment_id: str) -> tuple[Optional[dict], Optional[str]]:
    """Recupera dados de uma cobrança pelo ID Asaas."""
    try:
        resp = httpx.get(
            f"{_base_url()}/payments/{asaas_payment_id}",
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Asaas HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def get_pix_qr_code(asaas_payment_id: str) -> tuple[Optional[dict], Optional[str]]:
    """
    Retorna o QR Code Pix de uma cobrança.
    Retorna dict com 'encodedImage' (base64) e 'payload' (copia-e-cola).
    """
    try:
        resp = httpx.get(
            f"{_base_url()}/payments/{asaas_payment_id}/pixQrCode",
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Asaas HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def refund_payment(asaas_payment_id: str) -> tuple[Optional[dict], Optional[str]]:
    """Estorna/reembolsa uma cobrança pelo ID Asaas."""
    try:
        resp = httpx.post(
            f"{_base_url()}/payments/{asaas_payment_id}/refund",
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Asaas HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def get_payment_status(asaas_payment_id: str) -> tuple[Optional[str], Optional[str]]:
    """
    Retorna o status simplificado de uma cobrança.
    Status Asaas: PENDING, CONFIRMED, RECEIVED, OVERDUE, REFUNDED, REFUND_REQUESTED,
                  CHARGEBACK_REQUESTED, CHARGEBACK_DISPUTE, AWAITING_CHARGEBACK_REVERSAL,
                  DUNNING_REQUESTED, DUNNING_RECEIVED, AWAITING_RISK_ANALYSIS.
    """
    data, err = get_payment(asaas_payment_id)
    if err:
        return None, err
    return data.get("status"), None


# ──────────────────────────────────────────────
# MAPEAMENTO DE STATUS
# ──────────────────────────────────────────────

ASAAS_TO_INTERNAL_STATUS = {
    "PENDING": "pending",
    "CONFIRMED": "approved",
    "RECEIVED": "approved",
    "OVERDUE": "pending",
    "REFUNDED": "refunded",
    "REFUND_REQUESTED": "refunded",
    "CHARGEBACK_REQUESTED": "refused",
    "CHARGEBACK_DISPUTE": "refused",
}


def map_asaas_status(asaas_status: str) -> str:
    """Converte status do Asaas para o enum interno PaymentStatus."""
    return ASAAS_TO_INTERNAL_STATUS.get(asaas_status, "pending")
