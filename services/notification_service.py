from sqlalchemy.orm import Session
from database.models import NotificationLog, NotificationPreference, NotificationChannel, CustomerProfile
from adapters.smtp_adapter import send_email, build_order_confirmation_email
from adapters.telegram_adapter import send_telegram_message
from schemas.notification import NotificationInput
from typing import Optional
from datetime import datetime


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def send(self, data: NotificationInput) -> bool:
        customer = self.db.query(CustomerProfile).filter_by(id=data.customer_id).first()
        pref = (
            self.db.query(NotificationPreference)
            .filter_by(customer_id=data.customer_id, channel=data.channel, is_enabled=True)
            .first()
        )
        was_sent = False
        error_msg = None
        if data.channel == NotificationChannel.email:
            email = (
                (pref.channel_address if pref and pref.channel_address else None)
                or (customer.user.email if customer and customer.user else None)
            )
            if email:
                ok, err = send_email(to=email, subject=data.subject or "Alma de Cacau", html_body=data.body)
                was_sent, error_msg = ok, err
        elif data.channel == NotificationChannel.telegram:
            chat_id = pref.channel_address if pref and pref.channel_address else None
            if chat_id:
                ok, err = send_telegram_message(chat_id=chat_id, text=data.body)
                was_sent, error_msg = ok, err
        self.db.add(NotificationLog(
            customer_id=data.customer_id,
            order_id=data.order_id,
            channel=data.channel,
            subject=data.subject,
            body_preview=data.body[:500],
            was_sent=was_sent,
            error_message=error_msg,
            sent_at=datetime.utcnow() if was_sent else None,
        ))
        return was_sent

    def notify_order_confirmation(self, order_number: str, customer_name: str,
                                  total: str, customer_id: int) -> None:
        html = build_order_confirmation_email(order_number, customer_name, total)
        self.send(NotificationInput(
            customer_id=customer_id,
            channel=NotificationChannel.email,
            subject=f"Pedido {order_number} recebido - Alma de Cacau",
            body=html,
        ))
