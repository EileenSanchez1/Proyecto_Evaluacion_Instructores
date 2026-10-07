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


class AprendizService:
    @staticmethod
    def crear(session: Session, aprendiz: AprendizCreate) -> Aprendiz:
        correo = aprendiz.correo.strip().lower()
        if AprendizRepository.buscar_por_correo(session, correo):
            raise ValueError("Ya existe un aprendiz con ese correo.")
        if session.exec(select(Usuario).where(Usuario.correo == correo)).first():
            raise ValueError("Ya existe un usuario con ese correo.")

        rol = session.exec(select(Rol).where(Rol.nombre == "Aprendiz")).first()
        if not rol:
            raise ValueError("El rol 'Aprendiz' no existe. Ejecuta seed_roles.py primero.")

        id_periodo = aprendiz.id_periodo
        if id_periodo is None:
            activos = PeriodoRepository.listar_activos(session)
            if activos:
                id_periodo = activos[0].id_periodo
            else:
                raise ValueError("No hay un periodo activo. Crea un periodo primero.")

        periodo = PeriodoRepository.buscar(session, id_periodo)
        if not periodo:
            raise ValueError("El periodo seleccionado no existe.")
        if str(getattr(periodo, "estado", "")).lower() != "activo":
            raise ValueError(
                "El periodo seleccionado no está activo. Elige el periodo vigente."
            )

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
        if getattr(aprendiz, "enviar_correo", True):
            enviar_credenciales_aprendiz(
                destinatario=correo,
                nombre=f"{db.nombre} {db.apellido}",
                usuario=correo,
                contrasena=password_plana,
                numero_ficha=getattr(ficha, "numero_ficha", None),
                programa=getattr(ficha, "programa", None),
            )

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
            aprendiz_update.contrasena = LoginService.hash_password(
                aprendiz_update.contrasena
            )
        if aprendiz.id_usuario:
            usuario = session.get(Usuario, aprendiz.id_usuario)
            if usuario:
                if aprendiz_update.nombre:
                    usuario.nombre = aprendiz_update.nombre
                if aprendiz_update.apellido:
                    usuario.apellido = aprendiz_update.apellido
                if aprendiz_update.correo:
                    usuario.correo = aprendiz_update.correo
                if aprendiz_update.contrasena:
                    usuario.contrasena = aprendiz_update.contrasena
                session.add(usuario)
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
        if aprendiz.id_usuario:
            usuario = session.get(Usuario, aprendiz.id_usuario)
            if usuario is not None:
                activo = bool(usuario.activo)
        return {
            "id_aprendiz": aprendiz.id_aprendiz,
            "nombre": aprendiz.nombre,
            "apellido": aprendiz.apellido,
            "correo": aprendiz.correo,
            "id_ficha": aprendiz.id_ficha,
            "id_periodo": aprendiz.id_periodo,
            "activo": activo,
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
    ) -> dict:
        """
        Genera nueva contraseña temporal y envía correo a cada aprendiz de la ficha.
        Útil tras editar correos o para recordatorio de acceso.
        """
        from app.models.ficha import Ficha

        ficha = session.get(Ficha, id_ficha)
        if not ficha:
            raise ValueError("La ficha no existe.")

        aprendices = AprendizRepository.listar_por_ficha(session, id_ficha)
        enviados = []
        omitidos = []
        errores = []

        for ap in aprendices:
            activo = True
            usuario = None
            if ap.id_usuario:
                usuario = session.get(Usuario, ap.id_usuario)
                if usuario is not None:
                    activo = bool(usuario.activo)
            if solo_activos and not activo:
                omitidos.append({"correo": ap.correo, "motivo": "Inactivo"})
                continue

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

            ok = enviar_credenciales_aprendiz(
                destinatario=ap.correo,
                nombre=f"{ap.nombre} {ap.apellido}",
                usuario=ap.correo,
                contrasena=password_plana,
                numero_ficha=getattr(ficha, "numero_ficha", None),
                programa=getattr(ficha, "programa", None),
            )
            if ok:
                enviados.append(ap.correo)
            else:
                errores.append({"correo": ap.correo, "error": "No se pudo enviar el correo (SMTP)"})

        return {
            "enviados": len(enviados),
            "omitidos": len(omitidos),
            "errores": len(errores),
            "detalle_enviados": enviados,
            "detalle_omitidos": omitidos,
            "detalle_errores": errores,
            "mensaje": (
                f"Correos enviados: {len(enviados)}. "
                f"Omitidos (inactivos): {len(omitidos)}. "
                f"Fallidos: {len(errores)}."
            ),
        }
