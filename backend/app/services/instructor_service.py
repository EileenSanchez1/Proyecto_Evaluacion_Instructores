from typing import List, Optional
from sqlmodel import Session, select

from app.models.instructor import Instructor
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.instructor_resultado_aprendizaje import InstructorResultadoAprendizaje
from app.schemas.instructor import InstructorCreate, InstructorUpdate
from app.services.login_service import LoginService
from app.services.instructor_credenciales_service import (
    enviar_credenciales_nuevo,
    generar_password_temporal,
    reenviar_credenciales_instructores,
)


MSG_CORREO_INSTITUCIONAL = "El correo del instructor debe ser institucional (@sena.edu.co)."


def _normalizar_planta(valor: Optional[str]) -> Optional[str]:
    """Normaliza valores comunes del Excel: PLANTA, CONTRATO o el texto (máx. 20)."""
    planta = (valor or "").strip().upper()
    if not planta:
        return None
    if "PLANTA" in planta:
        return "PLANTA"
    if "CONTRAT" in planta:
        return "CONTRATO"
    return planta[:20]


def _planta_actualizada(valor: str) -> Optional[str]:
    pc = valor.strip().upper()
    if "PLANTA" in pc:
        return "PLANTA"
    if "CONTRAT" in pc:
        return "CONTRATO"
    return pc or None


def _validar_correo_nuevo(session: Session, correo: str) -> None:
    if not correo.endswith("@sena.edu.co"):
        raise ValueError(MSG_CORREO_INSTITUCIONAL)
    if session.exec(select(Instructor).where(Instructor.correo == correo)).first():
        raise ValueError("Ya existe un instructor con ese correo.")
    if session.exec(select(Usuario).where(Usuario.correo == correo)).first():
        raise ValueError("Ya existe un usuario con ese correo.")


def _rol_instructor(session: Session) -> Rol:
    rol = session.exec(select(Rol).where(Rol.nombre == "Instructor")).first()
    if not rol:
        raise ValueError("El rol 'Instructor' no existe. Ejecuta seed_roles.py primero.")
    return rol


def _agregar_resultados(session: Session, id_instructor: int, ids_ra) -> None:
    for id_ra in ids_ra:
        session.add(
            InstructorResultadoAprendizaje(id_instructor=id_instructor, id_resultado=id_ra)
        )


def _validar_correo_actualizado(session: Session, correo: str, instructor_id: int) -> str:
    correo = correo.strip().lower()
    if not correo.endswith("@sena.edu.co"):
        raise ValueError(MSG_CORREO_INSTITUCIONAL)
    otro = session.exec(
        select(Instructor).where(
            Instructor.correo == correo,
            Instructor.id_instructor != instructor_id,
        )
    ).first()
    if otro:
        raise ValueError("Ya existe otro instructor con ese correo.")
    return correo


def _aplicar_cambios(session: Session, instructor, upd: InstructorUpdate) -> None:
    """Copia al instructor los campos que vienen en la actualización."""
    for campo in ("nombre", "apellido"):
        valor = getattr(upd, campo)
        if valor is not None:
            setattr(instructor, campo, valor.strip())
    if upd.correo is not None:
        instructor.correo = _validar_correo_actualizado(
            session, upd.correo, instructor.id_instructor
        )
    if upd.telefono is not None:
        instructor.telefono = upd.telefono.strip()
    if upd.foto is not None:
        instructor.foto = upd.foto
    if upd.planta_contrato is not None:
        instructor.planta_contrato = _planta_actualizada(upd.planta_contrato)


def _sincronizar_usuario(session: Session, instructor, upd: InstructorUpdate) -> None:
    """Mantiene nombre, apellido y correo del usuario igual al del instructor."""
    usuario = session.get(Usuario, instructor.id_usuario) if instructor.id_usuario else None
    if not usuario:
        return
    for campo in ("nombre", "apellido", "correo"):
        if getattr(upd, campo) is not None:
            setattr(usuario, campo, getattr(instructor, campo))
    session.add(usuario)


def _ids_resultados(upd: InstructorUpdate):
    """Lista de resultados de aprendizaje a asignar (None = no cambiar)."""
    if upd.resultados_aprendizaje is None and upd.competencias is not None:
        return upd.competencias
    return upd.resultados_aprendizaje


def _ids_unicos(ids) -> list[int]:
    """Enteros válidos sin repetir, en el mismo orden."""
    unicos: list[int] = []
    for id_ra in ids:
        try:
            rid = int(id_ra)
        except (TypeError, ValueError):
            continue
        if rid not in unicos:
            unicos.append(rid)
    return unicos


def _reemplazar_resultados(session: Session, instructor_id: int, ids) -> None:
    existentes = session.exec(
        select(InstructorResultadoAprendizaje).where(
            InstructorResultadoAprendizaje.id_instructor == instructor_id
        )
    ).all()
    for e in existentes:
        session.delete(e)
    session.flush()
    _agregar_resultados(session, instructor_id, _ids_unicos(ids))


class InstructorService:
    @staticmethod
    def crear(
        session: Session, instructor: InstructorCreate, enviar_correo: bool = True
    ) -> Instructor:
        correo = instructor.correo.strip().lower()
        _validar_correo_nuevo(session, correo)
        rol = _rol_instructor(session)

        # Contraseña temporal (igual que aprendices) — se envía por correo
        password_plana = generar_password_temporal()
        usuario = Usuario(
            nombre=instructor.nombre.strip(),
            apellido=instructor.apellido.strip(),
            correo=correo,
            contrasena=LoginService.hash_password(password_plana),
            id_rol=rol.id_rol,
            activo=True,
        )
        session.add(usuario)
        session.flush()

        db = Instructor(
            nombre=instructor.nombre.strip(),
            apellido=instructor.apellido.strip(),
            correo=correo,
            telefono=instructor.telefono.strip(),
            foto=instructor.foto,
            planta_contrato=_normalizar_planta(instructor.planta_contrato),
            id_usuario=usuario.id_usuario,
        )
        session.add(db)
        session.flush()

        ids_ra = instructor.resultados_aprendizaje or instructor.competencias or []
        _agregar_resultados(session, db.id_instructor, ids_ra)
        session.commit()
        session.refresh(db)

        # Enviar credenciales por correo (opcional; en carga masiva va en False)
        if enviar_correo:
            enviar_credenciales_nuevo(session, usuario, db, password_plana)
        return db

    @staticmethod
    def buscar(session: Session, instructor_id: int) -> Optional[Instructor]:
        return session.get(Instructor, instructor_id)

    @staticmethod
    def es_activo(session: Session, instructor: Instructor) -> bool:
        if not instructor.id_usuario:
            return True
        usuario = session.get(Usuario, instructor.id_usuario)
        return bool(usuario and usuario.activo)

    @staticmethod
    def listar(session: Session, incluir_inactivos: bool = False) -> List[Instructor]:
        todos = session.exec(select(Instructor)).all()
        if incluir_inactivos:
            return list(todos)
        return [i for i in todos if InstructorService.es_activo(session, i)]

    @staticmethod
    def to_read(session: Session, instructor: Instructor) -> dict:
        from app.models.resultado_aprendizaje import ResultadoAprendizaje

        ras = []
        for rel in session.exec(
            select(InstructorResultadoAprendizaje).where(
                InstructorResultadoAprendizaje.id_instructor == instructor.id_instructor
            )
        ).all():
            ra = session.get(ResultadoAprendizaje, rel.id_resultado)
            if ra:
                ras.append(
                    {
                        "id_resultado": ra.id_resultado,
                        "codigo": getattr(ra, "codigo", None),
                        "nombre": ra.nombre,
                        "descripcion": getattr(ra, "descripcion", None),
                        "estado": getattr(ra, "estado", True),
                    }
                )
        credenciales_enviadas = False
        if instructor.id_usuario:
            usuario = session.get(Usuario, instructor.id_usuario)
            if usuario is not None:
                credenciales_enviadas = bool(
                    getattr(usuario, "credenciales_enviadas", False)
                )
        return {
            "id_instructor": instructor.id_instructor,
            "nombre": instructor.nombre,
            "apellido": instructor.apellido,
            "correo": instructor.correo,
            "telefono": instructor.telefono,
            "foto": instructor.foto,
            "planta_contrato": getattr(instructor, "planta_contrato", None),
            "resultados_aprendizaje": ras,
            "activo": InstructorService.es_activo(session, instructor),
            "credenciales_enviadas": credenciales_enviadas,
        }

    @staticmethod
    def actualizar(
        session: Session, instructor_id: int, instructor_update: InstructorUpdate
    ) -> Optional[Instructor]:
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return None

        _aplicar_cambios(session, instructor, instructor_update)
        _sincronizar_usuario(session, instructor, instructor_update)
        ids_ra = _ids_resultados(instructor_update)
        if ids_ra is not None:
            _reemplazar_resultados(session, instructor_id, ids_ra)

        session.add(instructor)
        try:
            session.commit()
            session.refresh(instructor)
        except Exception as e:
            session.rollback()
            raise ValueError(f"No se pudo guardar el instructor: {e}") from e
        return instructor

    @staticmethod
    def eliminar(session: Session, instructor_id: int) -> bool:
        """Desactiva el instructor (soft delete). No borra historial ni datos."""
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return False
        if not instructor.id_usuario:
            raise ValueError(
                "El instructor no tiene usuario vinculado para desactivar."
            )
        usuario = session.get(Usuario, instructor.id_usuario)
        if not usuario:
            raise ValueError("Usuario del instructor no encontrado.")
        usuario.activo = False
        session.add(usuario)
        session.commit()
        return True

    @staticmethod
    def reactivar(session: Session, instructor_id: int) -> bool:
        """Reactiva un instructor previamente desactivado."""
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return False
        if not instructor.id_usuario:
            raise ValueError("El instructor no tiene usuario vinculado.")
        usuario = session.get(Usuario, instructor.id_usuario)
        if not usuario:
            raise ValueError("Usuario del instructor no encontrado.")
        usuario.activo = True
        session.add(usuario)
        session.commit()
        return True

    @staticmethod
    def resetear_primer_acceso(session: Session, instructor_id: int) -> bool:
        """Deja al instructor en modo primer acceso (código + crear contraseña)."""
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return False
        if not instructor.id_usuario:
            return False
        usuario = session.get(Usuario, instructor.id_usuario)
        if not usuario:
            return False
        usuario.contrasena = LoginService.hash_password(
            LoginService.PASSWORD_PENDIENTE_MARKER
        )
        session.add(usuario)
        session.commit()
        return True

    @staticmethod
    def actualizar_foto(
        session: Session, instructor_id: int, foto_url: str
    ) -> Optional[Instructor]:
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return None
        instructor.foto = foto_url
        session.add(instructor)
        if instructor.id_usuario:
            usuario = session.get(Usuario, instructor.id_usuario)
            if usuario:
                usuario.foto = foto_url
                session.add(usuario)
        session.commit()
        session.refresh(instructor)
        return instructor

    @staticmethod
    def reenviar_credenciales(
        session: Session,
        solo_activos: bool = True,
        solo_pendientes: bool = True,
        id_instructor: int | None = None,
    ) -> dict:
        """
        Envía (o reenvía) credenciales a instructores.
        - solo_activos: omite usuarios inactivos
        - solo_pendientes: solo quienes no tienen credenciales_enviadas
        - id_instructor: si se indica, solo ese (siempre envía, aunque ya tenga flag)
        """
        return reenviar_credenciales_instructores(
            session, solo_activos, solo_pendientes, id_instructor
        )
