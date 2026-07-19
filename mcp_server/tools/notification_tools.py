from mcp.server.fastmcp import FastMCP
from database.engine import get_db
from services.notification_service import NotificationService
from schemas.notification import NotificationInput
from database.models import NotificationChannel
from typing import Optional


def register(mcp: FastMCP):

    @mcp.tool(name="send_notification",
              description="Envia notificacao a um cliente via email ou telegram.")
    def send_notification(
        customer_id: int, channel: str, body: str,
        subject: Optional[str] = None, order_id: Optional[int] = None,
    ) -> dict:
        try:
            ch = NotificationChannel(channel)
        except ValueError:
            return {"error": f"Canal invalido: {channel}. Use: email, telegram"}
        data = NotificationInput(customer_id=customer_id, channel=ch,
                                 subject=subject, body=body, order_id=order_id)
        with get_db() as db:
            svc = NotificationService(db)
            ok = svc.send(data)
            return {"success": ok, "channel": channel, "customer_id": customer_id}

    @mcp.tool(name="notify_order_confirmation",
              description="Envia email de confirmacao de pedido ao cliente.")
    def notify_order_confirmation(
        order_number: str, customer_name: str, total: str, customer_id: int,
    ) -> dict:
        with get_db() as db:
            svc = NotificationService(db)
            svc.notify_order_confirmation(
                order_number=order_number, customer_name=customer_name,
                total=total, customer_id=customer_id,
            )
        return {"success": True, "order_number": order_number}
