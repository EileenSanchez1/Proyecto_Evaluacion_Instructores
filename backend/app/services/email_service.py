"""
Envío de correos por SMTP (Gmail u otro proveedor).

Variables en backend/.env:
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=...
  SMTP_PASSWORD=...   # contraseña de aplicación
  SMTP_FROM=...
  SMTP_FROM_NAME=SENA Evaluación Instructores
"""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env desde la carpeta backend (no depende del cwd)
_BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(_BACKEND_DIR / ".env")
load_dotenv()  # por si también está en el cwd


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


def enviar_correo(
    destinatario: str,
    asunto: str,
    cuerpo_texto: str,
    cuerpo_html: str | None = None,
) -> bool:
    host, port, user, password, from_addr, from_name = _smtp_config()
    destinatario = (destinatario or "").strip().lower()

    if not user or not password:
        print(
            "\n[EMAIL] SMTP no configurado. Define SMTP_USER y SMTP_PASSWORD en backend/.env\n"
            f"        No se envió correo a {destinatario}.\n"
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
        print(f"[EMAIL] ✓ Enviado a {destinatario} | {asunto}")
        return True
    except Exception as e:
        print(f"[EMAIL] ✗ Error enviando a {destinatario}: {type(e).__name__}: {e}")
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


def enviar_credenciales_aprendiz(
    destinatario: str,
    nombre: str,
    usuario: str,
    contrasena: str,
    numero_ficha: str | None = None,
    programa: str | None = None,
) -> bool:
    """
    Envía usuario y contraseña al aprendiz (estilo SGVA / cartero).
    El aprendiz ya queda asignado a su ficha y solo debe iniciar sesión.
    """
    ficha_txt = f"\nFicha: {numero_ficha}" if numero_ficha else ""
    prog_txt = f"\nPrograma: {programa}" if programa else ""
    asunto = "Credenciales de acceso — Evaluación de Instructores SENA"
    texto = (
        f"Hola {nombre},\n\n"
        f"Has sido registrado en el Sistema de Evaluación de Instructores SENA."
        f"{ficha_txt}{prog_txt}\n\n"
        f"Tus datos de acceso son:\n"
        f"  Usuario (correo): {usuario}\n"
        f"  Contraseña temporal: {contrasena}\n\n"
        f"Te recomendamos cambiar la contraseña después del primer ingreso.\n\n"
        f"— SENA · Evaluación de Instructores\n"
    )
    html = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
      <h2 style="color:#39a900;margin:0 0 12px;">Bienvenido/a al sistema</h2>
      <p>Hola <strong>{nombre}</strong>,</p>
      <p>Has sido registrado en el
      <strong>Sistema de Evaluación de Instructores SENA</strong>
      y ya estás asignado a tu ficha.</p>
      {"<p><strong>Ficha:</strong> " + numero_ficha + "</p>" if numero_ficha else ""}
      {"<p><strong>Programa:</strong> " + programa + "</p>" if programa else ""}
      <p style="font-size:15px;margin-top:16px;">Tus datos de acceso:</p>
      <div style="background:#f3f4f6;padding:14px 20px;border-radius:10px;">
        <p style="margin:6px 0;"><strong>Usuario:</strong> {usuario}</p>
        <p style="margin:6px 0;"><strong>Contraseña temporal:</strong>
          <span style="font-family:monospace;letter-spacing:1px;">{contrasena}</span>
        </p>
      </div>
      <p style="color:#6b7280;font-size:13px;margin-top:14px;">
        Te recomendamos cambiar la contraseña después del primer ingreso.
      </p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;"/>
      <p style="color:#9ca3af;font-size:12px;">SENA · Evaluación de Instructores</p>
    </div>
    """
    return enviar_correo(destinatario, asunto, texto, html)


def enviar_codigo_instructor(destinatario: str, codigo: str) -> bool:
    """Mismo mecanismo que recuperación: código al correo del instructor."""
    asunto = "Código de verificación de instructor — SENA"
    texto = (
        f"Hola,\n\n"
        f"Para completar tu primer acceso como instructor en el Sistema de "
        f"Evaluación de Instructores SENA, usa este código:\n\n"
        f"{codigo}\n\n"
        f"Válido por 15 minutos.\n\n"
        f"Si no solicitaste este acceso, ignora este mensaje.\n\n"
        f"— SENA · Evaluación de Instructores\n"
    )
    html = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
      <h2 style="color:#39a900;margin:0 0 12px;">Primer acceso — Instructor</h2>
      <p>Para completar tu acceso como <strong>instructor</strong> y crear tu contraseña, usa este código:</p>
      <p style="font-size:28px;font-weight:700;letter-spacing:6px;color:#1f2937;
         background:#f3f4f6;padding:14px 20px;border-radius:10px;text-align:center;">
        {codigo}
      </p>
      <p style="color:#6b7280;font-size:13px;">Válido por 15 minutos. Revisa también la bandeja de spam.</p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;"/>
      <p style="color:#9ca3af;font-size:12px;">SENA · Evaluación de Instructores</p>
    </div>
    """
    return enviar_correo(destinatario, asunto, texto, html)


def enviar_novedad_resuelta(
    destinatario: str,
    nombre: str,
    mensaje_original: str | None = None,
) -> bool:
    """Avisa al aprendiz que su novedad/mensaje ya fue atendida."""
    asunto = "Tu novedad fue atendida — SENA Evaluación de Instructores"
    preview = (mensaje_original or "").strip()
    if len(preview) > 180:
        preview = preview[:180] + "…"
    texto = (
        f"Hola {nombre},\n\n"
        f"Te informamos que la novedad o mensaje que enviaste al administrador "
        f"ya fue revisada y marcada como solucionada.\n\n"
    )
    if preview:
        texto += f"Resumen de tu mensaje:\n{preview}\n\n"
    texto += (
        "Si aún necesitas ayuda, puedes enviar una nueva novedad desde Contacto "
        "en la plataforma.\n\n"
        "— SENA · Evaluación de Instructores\n"
    )
    html = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
      <h2 style="color:#39a900;margin:0 0 12px;">Novedad atendida</h2>
      <p>Hola <strong>{nombre}</strong>,</p>
      <p>Tu novedad o mensaje enviado al administrador
      <strong>ya fue revisada y marcada como solucionada</strong>.</p>
      {"<p style='background:#f3f4f6;padding:12px;border-radius:8px;font-size:13px;color:#374151;'><strong>Tu mensaje:</strong><br/>" + preview.replace(chr(10), '<br/>') + "</p>" if preview else ""}
      <p style="color:#6b7280;font-size:13px;">Si aún necesitas ayuda, envía una nueva novedad desde <strong>Contacto</strong> en la plataforma.</p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;"/>
      <p style="color:#9ca3af;font-size:12px;">SENA · Evaluación de Instructores</p>
    </div>
    """
    return enviar_correo(destinatario, asunto, texto, html)


def enviar_invitacion_instructor(
    destinatario: str,
    nombre: str,
    plazo_horas: int = 48,
) -> bool:
    """Avisa al instructor que ya fue registrado y debe completar primer acceso + foto."""
    asunto = "Bienvenido — Completa tu acceso como instructor SENA"
    texto = (
        f"Hola {nombre},\n\n"
        f"Has sido registrado como instructor en el Sistema de Evaluación de Instructores del SENA.\n\n"
        f"Tu correo de acceso es: {destinatario}\n\n"
        f"Para ingresar por primera vez:\n"
        f"1. Ve a la opción «Soy instructor» en la plataforma.\n"
        f"2. Solicita el código de verificación que llegará a este correo.\n"
        f"3. Crea tu contraseña segura.\n"
        f"4. Actualiza tu foto de perfil.\n\n"
        f"Tienes un plazo de {plazo_horas} horas para completar el acceso y subir tu foto. "
        f"Si no lo haces, se podrá generar un plan de mejora o llamado de atención con el coordinador.\n\n"
        f"— SENA · Evaluación de Instructores\n"
    )
    html = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
      <h2 style="color:#39a900;margin:0 0 12px;">Bienvenido al sistema</h2>
      <p>Hola <strong>{nombre}</strong>,</p>
      <p>Has sido registrado como <strong>instructor</strong> en el Sistema de Evaluación de Instructores del SENA.</p>
      <p><strong>Correo de acceso:</strong> {destinatario}</p>
      <p>Para ingresar por primera vez:</p>
      <ol>
        <li>Ve a la opción <strong>«Soy instructor»</strong> en la plataforma.</li>
        <li>Solicita el código de verificación que llegará a este correo.</li>
        <li>Crea tu contraseña segura.</li>
        <li>Actualiza tu foto de perfil.</li>
      </ol>
      <p style="background:#fef3c7;padding:12px;border-radius:8px;color:#92400e;">
        <strong>Plazo:</strong> tienes <strong>{plazo_horas} horas</strong> para completar el acceso y subir tu foto.
        Si no lo haces, se podrá generar un plan de mejora o llamado de atención con el coordinador.
      </p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;"/>
      <p style="color:#9ca3af;font-size:12px;">SENA · Evaluación de Instructores</p>
    </div>
    """
    return enviar_correo(destinatario, asunto, texto, html)


def enviar_nuevo_periodo_aprendiz(
    destinatario: str,
    nombre: str,
    nombre_periodo: str,
) -> bool:
    """Avisa al aprendiz que ya puede evaluar instructores del nuevo trimestre."""
    asunto = f"Nuevo periodo de evaluación habilitado — {nombre_periodo}"
    texto = (
        f"Hola {nombre},\n\n"
        f"Se ha habilitado el periodo de evaluación: {nombre_periodo}.\n\n"
        f"Ya puedes ingresar al Sistema de Evaluación de Instructores del SENA "
        f"para evaluar a tus instructores de este trimestre.\n\n"
        f"Ingresa con el mismo correo con el que te registraste y la contraseña "
        f"que actualizaste en tu primer acceso.\n\n"
        f"— SENA · Evaluación de Instructores\n"
    )
    html = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
      <h2 style="color:#39a900;margin:0 0 12px;">Nuevo periodo de evaluación</h2>
      <p>Hola <strong>{nombre}</strong>,</p>
      <p>Se ha habilitado el periodo: <strong>{nombre_periodo}</strong>.</p>
      <p>Ya puedes ingresar al sistema para evaluar a tus instructores de este trimestre.</p>
      <p style="background:#ecfdf5;padding:12px;border-radius:8px;color:#065f46;">
        Usa el <strong>mismo correo</strong> con el que te registraste y la
        <strong>contraseña que actualizaste</strong> en tu primer acceso.
      </p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;"/>
      <p style="color:#9ca3af;font-size:12px;">SENA · Evaluación de Instructores</p>
    </div>
    """
    return enviar_correo(destinatario, asunto, texto, html)
