from typing import List, Optional
import secrets
import string

from sqlmodel import Session, select

from app.models.aprendiz import Aprendiz
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.ficha import Ficha
from app.schemas.aprendiz import AprendizCreate, AprendizUpdate
from app.repositories.aprendiz_repository import AprendizRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.services.login_service import LoginService
from app.services.email_service import enviar_credenciales_aprendiz


def _generar_password_temporal(longitud: int = 10) -> str:
    """Contraseña temporal legible (letras + dígitos + un símbolo)."""
    simbolos = "!@#$%&*"
    alfabeto = string.ascii_letters + string.digits
    partes = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice(simbolos),
    ]
    partes += [secrets.choice(alfabeto) for _ in range(max(0, longitud - 4))]
    secrets.SystemRandom().shuffle(partes)
    return "".join(partes)


def _validar_correo_libre(session: Session, correo: str) -> None:
    if AprendizRepository.buscar_por_correo(session, correo):
        raise ValueError("Ya existe un aprendiz con ese correo.")
    if session.exec(select(Usuario).where(Usuario.correo == correo)).first():
        raise ValueError("Ya existe un usuario con ese correo.")


def _rol_aprendiz(session: Session) -> Rol:
    rol = session.exec(select(Rol).where(Rol.nombre == "Aprendiz")).first()
    if not rol:
        raise ValueError("El rol 'Aprendiz' no existe. Ejecuta seed_roles.py primero.")
    return rol


def _periodo_activo(session: Session, id_periodo: Optional[int]) -> int:
    """Periodo indicado (debe existir y estar activo) o el primer periodo activo."""
    if id_periodo is None:
        activos = PeriodoRepository.listar_activos(session)
        if not activos:
            raise ValueError("No hay un periodo activo. Crea un periodo primero.")
        id_periodo = activos[0].id_periodo
    periodo = PeriodoRepository.buscar(session, id_periodo)
    if not periodo:
        raise ValueError("El periodo seleccionado no existe.")
    if str(getattr(periodo, "estado", "")).lower() != "activo":
        raise ValueError("El periodo seleccionado no está activo. Elige el periodo vigente.")
    return id_periodo


def _enviar_credenciales(ap, ficha, password_plana: str) -> bool:
    return enviar_credenciales_aprendiz(
        destinatario=ap.correo,
        nombre=f"{ap.nombre} {ap.apellido}",
        usuario=ap.correo,
        contrasena=password_plana,
        numero_ficha=getattr(ficha, "numero_ficha", None),
        programa=getattr(ficha, "programa", None),
    )


def _marcar_credenciales_enviadas(session: Session, usuario) -> None:
    usuario.credenciales_enviadas = True
    session.add(usuario)
    session.commit()


def _sincronizar_usuario(session: Session, aprendiz, upd: AprendizUpdate) -> None:
    """Copia al usuario los campos que cambian (nombre, apellido, correo, contraseña)."""
    usuario = session.get(Usuario, aprendiz.id_usuario) if aprendiz.id_usuario else None
    if not usuario:
        return
    for campo in ("nombre", "apellido", "correo", "contrasena"):
        valor = getattr(upd, campo)
        if valor:
            setattr(usuario, campo, valor)
    session.add(usuario)


def _aprendices_a_notificar(session: Session, id_ficha: int, id_aprendiz) -> list:
    aprendices = AprendizRepository.listar_por_ficha(session, id_ficha)
    if id_aprendiz is None:
        return aprendices
    aprendices = [a for a in aprendices if a.id_aprendiz == int(id_aprendiz)]
    if not aprendices:
        raise ValueError("Aprendiz no encontrado en esta ficha.")
    return aprendices


def _usuario_y_estado(session: Session, ap) -> tuple:
    """(usuario, activo, ya_recibio_credenciales)"""
    usuario = session.get(Usuario, ap.id_usuario) if ap.id_usuario else None
    if usuario is None:
        return None, True, False
    return usuario, bool(usuario.activo), bool(getattr(usuario, "credenciales_enviadas", False))


def _motivo_omision(activo: bool, ya: bool, solo_activos: bool, solo_pendientes: bool) -> str:
    if solo_activos and not activo:
        return "Inactivo"
    if solo_pendientes and ya:
        return "Ya recibió credenciales"
    return ""


def _nueva_contrasena(session: Session, ap, usuario) -> str:
    """Genera y guarda una contraseña temporal. Devuelve la contraseña en texto plano."""
    password_plana = _generar_password_temporal()
    pwd = LoginService.hash_password(password_plana)
    ap.contrasena = pwd
    session.add(ap)
    if usuario:
        usuario.contrasena = pwd
        if ap.correo and usuario.correo != ap.correo:
            usuario.correo = ap.correo
        session.add(usuario)
    session.commit()
    return password_plana


class AprendizService:
    @staticmethod
    def crear(session: Session, aprendiz: AprendizCreate) -> Aprendiz:
        correo = aprendiz.correo.strip().lower()
        _validar_correo_libre(session, correo)
        rol = _rol_aprendiz(session)
        id_periodo = _periodo_activo(session, aprendiz.id_periodo)
        ficha = session.get(Ficha, aprendiz.id_ficha)
        if not ficha:
            raise ValueError("La ficha seleccionada no existe.")

        # Contraseña: la que envían o una temporal generada (estilo SGVA)
        password_plana = (aprendiz.contrasena or "").strip() or _generar_password_temporal()
        pwd = LoginService.hash_password(password_plana)

        usuario = Usuario(
            nombre=aprendiz.nombre.strip(),
            apellido=aprendiz.apellido.strip(),
            correo=correo,
            contrasena=pwd,
            id_rol=rol.id_rol,
            activo=True,
        )
        session.add(usuario)
        session.flush()

        db = Aprendiz(
            nombre=aprendiz.nombre.strip(),
            apellido=aprendiz.apellido.strip(),
            correo=correo,
            contrasena=pwd,
            id_ficha=aprendiz.id_ficha,
            id_periodo=id_periodo,
            id_usuario=usuario.id_usuario,
        )
        session.add(db)
        session.commit()
        session.refresh(db)

        # Envío de credenciales por correo (cartero / SGVA)
        if getattr(aprendiz, "enviar_correo", True) and _enviar_credenciales(
            db, ficha, password_plana
        ):
            _marcar_credenciales_enviadas(session, usuario)
        return db

    @staticmethod
    def buscar(session: Session, aprendiz_id: int) -> Optional[Aprendiz]:
        return AprendizRepository.buscar(session, aprendiz_id)

    @staticmethod
    def buscar_por_correo(session: Session, correo: str) -> Optional[Aprendiz]:
        return AprendizRepository.buscar_por_correo(session, correo)

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Aprendiz]:
        return AprendizRepository.listar(session, offset, limit)

    @staticmethod
    def listar_por_ficha(session: Session, id_ficha: int) -> List[Aprendiz]:
        return AprendizRepository.listar_por_ficha(session, id_ficha)

    @staticmethod
    def listar_por_ficha_y_periodo(
        session: Session, id_ficha: int, id_periodo: int
    ) -> List[Aprendiz]:
        return AprendizRepository.listar_por_ficha_y_periodo(
            session, id_ficha, id_periodo
        )

    @staticmethod
    def actualizar(
        session: Session, aprendiz_id: int, aprendiz_update: AprendizUpdate
    ) -> Optional[Aprendiz]:
        aprendiz = AprendizRepository.buscar(session, aprendiz_id)
        if not aprendiz:
            return None
        if aprendiz_update.correo:
            ex = AprendizRepository.buscar_por_correo(session, aprendiz_update.correo)
            if ex and ex.id_aprendiz != aprendiz_id:
                raise ValueError("Ya existe otro aprendiz con ese correo.")
        if aprendiz_update.contrasena:
            aprendiz_update.contrasena = LoginService.hash_password(aprendiz_update.contrasena)
        _sincronizar_usuario(session, aprendiz, aprendiz_update)
        return AprendizRepository.actualizar(session, aprendiz_id, aprendiz_update)

    @staticmethod
    def eliminar(session: Session, aprendiz_id: int) -> bool:
        aprendiz = AprendizRepository.buscar(session, aprendiz_id)
        if not aprendiz:
            return False
        if aprendiz.id_usuario:
            usuario = session.get(Usuario, aprendiz.id_usuario)
            if usuario:
                session.delete(usuario)
        return AprendizRepository.eliminar(session, aprendiz_id)

    @staticmethod
    def to_read(session: Session, aprendiz: Aprendiz) -> dict:
        activo = True
        credenciales_enviadas = False
        if aprendiz.id_usuario:
            usuario = session.get(Usuario, aprendiz.id_usuario)
            if usuario is not None:
                activo = bool(usuario.activo)
                credenciales_enviadas = bool(
                    getattr(usuario, "credenciales_enviadas", False)
                )
        return {
            "id_aprendiz": aprendiz.id_aprendiz,
            "nombre": aprendiz.nombre,
            "apellido": aprendiz.apellido,
            "correo": aprendiz.correo,
            "id_ficha": aprendiz.id_ficha,
            "id_periodo": aprendiz.id_periodo,
            "activo": activo,
            "credenciales_enviadas": credenciales_enviadas,
        }

    @staticmethod
    def desactivar(session: Session, aprendiz_id: int) -> bool:
        """Desactiva al aprendiz (desertor / baja). No borra historial."""
        aprendiz = AprendizRepository.buscar(session, aprendiz_id)
        if not aprendiz:
            return False
        if not aprendiz.id_usuario:
            raise ValueError("El aprendiz no tiene usuario vinculado.")
        usuario = session.get(Usuario, aprendiz.id_usuario)
        if not usuario:
            raise ValueError("Usuario del aprendiz no encontrado.")
        usuario.activo = False
        session.add(usuario)
        session.commit()
        return True

    @staticmethod
    def reactivar(session: Session, aprendiz_id: int) -> bool:
        aprendiz = AprendizRepository.buscar(session, aprendiz_id)
        if not aprendiz:
            return False
        if not aprendiz.id_usuario:
            raise ValueError("El aprendiz no tiene usuario vinculado.")
        usuario = session.get(Usuario, aprendiz.id_usuario)
        if not usuario:
            raise ValueError("Usuario del aprendiz no encontrado.")
        usuario.activo = True
        session.add(usuario)
        session.commit()
        return True

    @staticmethod
    def reenviar_credenciales_ficha(
        session: Session,
        id_ficha: int,
        solo_activos: bool = True,
        solo_pendientes: bool = True,
        id_aprendiz: int | None = None,
    ) -> dict:
        """
        Genera nueva contraseña temporal y envía correo.
        - solo_activos: no envía a inactivos
        - solo_pendientes: solo a quienes aún no tienen credenciales_enviadas
        - id_aprendiz: si se indica, solo ese aprendiz (ignora solo_pendientes)
        """
        ficha = session.get(Ficha, id_ficha)
        if not ficha:
            raise ValueError("La ficha no existe.")
        aprendices = _aprendices_a_notificar(session, id_ficha, id_aprendiz)
        # Envío individual siempre; en lote solo pendientes
        solo_pendientes = solo_pendientes and id_aprendiz is None

        enviados, omitidos, errores = [], [], []
        for ap in aprendices:
            usuario, activo, ya_enviado = _usuario_y_estado(session, ap)
            motivo = _motivo_omision(activo, ya_enviado, solo_activos, solo_pendientes)
            if motivo:
                omitidos.append({"correo": ap.correo, "motivo": motivo})
                continue
            password_plana = _nueva_contrasena(session, ap, usuario)
            if not _enviar_credenciales(ap, ficha, password_plana):
                errores.append({"correo": ap.correo, "error": "No se pudo enviar el correo (SMTP)"})
                continue
            enviados.append(ap.correo)
            if usuario:
                _marcar_credenciales_enviadas(session, usuario)

        return {
            "enviados": len(enviados),
            "omitidos": len(omitidos),
            "errores": len(errores),
            "detalle_enviados": enviados,
            "detalle_omitidos": omitidos,
            "detalle_errores": errores,
            "mensaje": (
                f"Correos enviados: {len(enviados)}. "
                f"Omitidos: {len(omitidos)}. "
                f"Fallidos: {len(errores)}."
            ),
        }
