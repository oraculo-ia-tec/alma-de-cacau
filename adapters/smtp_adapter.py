import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


SMTP_HOST     = os.getenv("SMTP_HOST") or os.getenv("EMAIL_HOST", "smtp.hostinger.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT") or os.getenv("EMAIL_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER") or os.getenv("EMAIL_USERNAME", "contato@almadecacau.com.br")
SMTP_PASS     = os.getenv("SMTP_PASS") or os.getenv("EMAIL_PASSWORD", "")
SMTP_USE_TLS  = (os.getenv("EMAIL_USE_TLS", "true").lower() == "true")
SMTP_FROM_NAME = "Alma de Cacau"


def send_email(to: str, subject: str, html_body: str) -> tuple[bool, Optional[str]]:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        if SMTP_USE_TLS:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)

        with server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to, msg.as_string())
        return True, None
    except Exception as e:
        return False, str(e)


def build_order_confirmation_email(order_number: str, customer_name: str, total: str) -> str:
    return f"""
    <html><body style="font-family: Georgia, serif; color: #3b1f0c; background: #fdf6ee; padding: 32px;">
      <h2 style="color: #7b3f00;">🍫 Alma de Cacau</h2>
      <p>Olá, <strong>{customer_name}</strong>!</p>
      <p>Seu pedido <strong>#{order_number}</strong> foi recebido com muito carinho. 💛</p>
      <p>Total: <strong>R$ {total}</strong></p>
      <p>Em breve nossa equipe entrará em contato para confirmar os próximos passos.</p>
      <hr style="border-color: #d4a96a;">
      <p style="font-style: italic; color: #7b3f00;">
        Alma de Cacau — Transformando chocolate em lembrança.<br>
        Feito à mão, com carinho. 🤍
      </p>
    </body></html>
    """
