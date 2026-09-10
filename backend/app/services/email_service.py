"""
Envío de correos por SMTP (Gmail u otro proveedor).

Variables de entorno (.env en la carpeta backend):
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=tu_correo_cartero@gmail.com
  SMTP_PASSWORD=xxxx xxxx xxxx xxxx   # contraseña de aplicación (16 caracteres)
  SMTP_FROM=tu_correo_cartero@gmail.com
  SMTP_FROM_NAME=SENA Evaluación Instructores
"""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


def _smtp_config():
    host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    user = (os.getenv("SMTP_USER") or "").strip()
    password = (os.getenv("SMTP_PASSWORD") or "").strip().replace(" ", "")
    from_addr = (os.getenv("SMTP_FROM") or user).strip()
    from_name = (os.getenv("SMTP_FROM_NAME") or "SENA Evaluación Instructores").strip()
    return host, port, user, password, from_addr, from_name


def smtp_configurado() -> bool:
    _, _, user, password, _, _ = _smtp_config()
    return bool(user and password)


def enviar_correo(destinatario: str, asunto: str, cuerpo_texto: str, cuerpo_html: str | None = None) -> bool:
    """
    Envía un correo. Devuelve True si salió bien.
    Si SMTP no está configurado, no falla el flujo: solo imprime aviso.
    """
    host, port, user, password, from_addr, from_name = _smtp_config()
    destinatario = (destinatario or "").strip().lower()

    if not user or not password:
        print(
            "\n[EMAIL] SMTP no configurado. Define SMTP_USER y SMTP_PASSWORD en backend/.env\n"
            f"        Código/mensaje para {destinatario} NO se envió por correo.\n"
        )
        return False

    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = f"{from_name} <{from_addr}>"
    msg["To"] = destinatario
    msg.set_content(cuerpo_texto)
    if cuerpo_html:
        msg.add_alternative(cuerpo_html, subtype="html")

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, password)
            server.send_message(msg)
        print(f"[EMAIL] Enviado correctamente a {destinatario} | Asunto: {asunto}")
        return True
    except Exception as e:
        print(f"[EMAIL] ERROR al enviar a {destinatario}: {e}")
        return False


def enviar_codigo_recuperacion(destinatario: str, codigo: str) -> bool:
    asunto = "Código de recuperación de contraseña — SENA"
    texto = (
        f"Hola,\n\n"
        f"Recibimos una solicitud para restablecer tu contraseña en el "
        f"Sistema de Evaluación de Instructores SENA.\n\n"
        f"Tu código de verificación es: {codigo}\n\n"
        f"Válido por 15 minutos. Si no solicitaste este cambio, ignora este mensaje.\n\n"
        f"— SENA · Evaluación de Instructores\n"
    )
    html = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
      <h2 style="color:#39a900;margin:0 0 12px;">Recuperar contraseña</h2>
      <p>Recibimos una solicitud para restablecer tu contraseña en el
      <strong>Sistema de Evaluación de Instructores SENA</strong>.</p>
      <p style="font-size:15px;">Tu código de verificación es:</p>
      <p style="font-size:28px;font-weight:700;letter-spacing:6px;color:#1f2937;
         background:#f3f4f6;padding:14px 20px;border-radius:10px;text-align:center;">
        {codigo}
      </p>
      <p style="color:#6b7280;font-size:13px;">Válido por 15 minutos. Si no solicitaste este cambio, ignora este mensaje.</p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;"/>
      <p style="color:#9ca3af;font-size:12px;">SENA · Evaluación de Instructores</p>
    </div>
    """
    return enviar_correo(destinatario, asunto, texto, html)


def enviar_codigo_instructor(destinatario: str, codigo: str) -> bool:
    asunto = "Código de verificación de instructor — SENA"
    texto = (
        f"Hola,\n\n"
        f"Para completar tu acceso como instructor en el Sistema de Evaluación "
        f"de Instructores SENA, usa este código:\n\n"
        f"{codigo}\n\n"
        f"Válido por 15 minutos.\n\n"
        f"— SENA · Evaluación de Instructores\n"
    )
    html = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
      <h2 style="color:#39a900;margin:0 0 12px;">Verificación de instructor</h2>
      <p>Para completar tu acceso como <strong>instructor</strong>, usa este código:</p>
      <p style="font-size:28px;font-weight:700;letter-spacing:6px;color:#1f2937;
         background:#f3f4f6;padding:14px 20px;border-radius:10px;text-align:center;">
        {codigo}
      </p>
      <p style="color:#6b7280;font-size:13px;">Válido por 15 minutos.</p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;"/>
      <p style="color:#9ca3af;font-size:12px;">SENA · Evaluación de Instructores</p>
    </div>
    """
    return enviar_correo(destinatario, asunto, texto, html)
