from mcp.server.fastmcp import FastMCP
from database.engine import get_db
from services.payment_service import PaymentService
from schemas.payment import CreatePaymentInput
from database.models import PaymentMethod
from typing import Optional


def register(mcp: FastMCP):

    @mcp.tool(
        name="create_payment",
        description="Cria cobranca via Asaas (PIX, BOLETO ou UNDEFINED). Nunca recebe dados de cartao.",
    )
    def create_payment(
        order_id: int,
        method: str,
        asaas_customer_id: Optional[str] = None,
    ) -> dict:
        try:
            payment_method = PaymentMethod(method)
        except ValueError:
            return {"error": f"Metodo invalido: {method}. Use: asaas, pix, boleto, cash_on_pickup, card_on_pickup"}
        data = CreatePaymentInput(order_id=order_id, method=payment_method,
                                  asaas_customer_id=asaas_customer_id)
        with get_db() as db:
            svc = PaymentService(db)
            payment, err = svc.create_payment(data)
            if err:
                return {"error": err}
            return {
                "success": True,
                "payment_id": payment.id,
                "status": payment.status.value,
                "amount": float(payment.amount),
                "provider_reference": payment.provider_reference,
            }

    @mcp.tool(name="get_pix_qr_code", description="Retorna QR Code Pix de um pagamento.")
    def get_pix_qr_code(payment_id: int) -> dict:
        with get_db() as db:
            svc = PaymentService(db)
            qr, err = svc.get_pix_qr_code(payment_id)
            if err:
                return {"error": err}
            return {
                "success": True,
                "encoded_image": qr.get("encodedImage"),
                "payload": qr.get("payload"),
                "expiration": qr.get("expirationDate"),
            }

    @mcp.tool(name="refund_payment", description="Estorna um pagamento aprovado.")
    def refund_payment(payment_id: int) -> dict:
        with get_db() as db:
            svc = PaymentService(db)
            ok, err = svc.refund(payment_id)
            if err:
                return {"error": err}
            return {"success": True, "message": "Estorno solicitado com sucesso."}

    @mcp.tool(name="process_payment_webhook",
              description="Processa webhook do Asaas para atualizar status de pagamento.")
    def process_payment_webhook(asaas_payment_id: str, asaas_status: str) -> dict:
        with get_db() as db:
            svc = PaymentService(db)
            ok, err = svc.confirm_payment(asaas_payment_id, asaas_status)
            if err:
                return {"error": err}
            return {"success": True, "message": f"Status atualizado para {asaas_status}."}
