from typing import List, Optional
from sqlmodel import Session, select

from app.models.instructor import Instructor
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.instructor_competencia import InstructorCompetencia
from app.models.ficha_instructor import FichaInstructor
from app.models.respuesta import Respuesta
from app.models.evaluacion import Evaluacion
from app.models.horario import Horario
from app.schemas.instructor import InstructorCreate, InstructorUpdate
from app.services.login_service import LoginService


class InstructorService:
    @staticmethod
    def crear(session: Session, instructor: InstructorCreate) -> Instructor:
        correo = instructor.correo.strip().lower()

        if not correo.endswith("@sena.edu.co"):
            raise ValueError(
                "El correo del instructor debe ser institucional (@sena.edu.co)."
            )

        if session.exec(select(Instructor).where(Instructor.correo == correo)).first():
            raise ValueError("Ya existe un instructor con ese correo.")
        if session.exec(select(Usuario).where(Usuario.correo == correo)).first():
            raise ValueError("Ya existe un usuario con ese correo.")

        rol = session.exec(select(Rol).where(Rol.nombre == "Instructor")).first()
        if not rol:
            raise ValueError(
                "El rol 'Instructor' no existe. Ejecuta seed_roles.py primero."
            )

        pwd = LoginService.hash_password(LoginService.PASSWORD_PENDIENTE_MARKER)

        usuario = Usuario(
            nombre=instructor.nombre.strip(),
            apellido=instructor.apellido.strip(),
            correo=correo,
            contrasena=pwd,
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
            id_usuario=usuario.id_usuario,
        )
        session.add(db)
        session.flush()

        if instructor.competencias:
            for id_comp in instructor.competencias:
                session.add(
                    InstructorCompetencia(
                        id_instructor=db.id_instructor,
                        id_competencia=id_comp,
                    )
                )

        session.commit()
        session.refresh(db)
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
        from app.models.competencia import Competencia

        comps = []
        for rel in session.exec(
            select(InstructorCompetencia).where(
                InstructorCompetencia.id_instructor == instructor.id_instructor
            )
        ).all():
            c = session.get(Competencia, rel.id_competencia)
            if c:
                comps.append(
                    {
                        "id_competencia": c.id_competencia,
                        "nombre": c.nombre,
                        "descripcion": getattr(c, "descripcion", None),
                        "estado": getattr(c, "estado", True),
                    }
                )
        return {
            "id_instructor": instructor.id_instructor,
            "nombre": instructor.nombre,
            "apellido": instructor.apellido,
            "correo": instructor.correo,
            "telefono": instructor.telefono,
            "foto": instructor.foto,
            "competencias": comps,
            "activo": InstructorService.es_activo(session, instructor),
        }

    @staticmethod
    def actualizar(
        session: Session, instructor_id: int, instructor_update: InstructorUpdate
    ) -> Optional[Instructor]:
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return None

        if instructor_update.nombre is not None:
            instructor.nombre = instructor_update.nombre.strip()
        if instructor_update.apellido is not None:
            instructor.apellido = instructor_update.apellido.strip()
        if instructor_update.correo is not None:
            correo = instructor_update.correo.strip().lower()
            if not correo.endswith("@sena.edu.co"):
                raise ValueError(
                    "El correo del instructor debe ser institucional (@sena.edu.co)."
                )
            otro = session.exec(
                select(Instructor).where(
                    Instructor.correo == correo,
                    Instructor.id_instructor != instructor_id,
                )
            ).first()
            if otro:
                raise ValueError("Ya existe otro instructor con ese correo.")
            instructor.correo = correo
        if instructor_update.telefono is not None:
            instructor.telefono = instructor_update.telefono.strip()
        if instructor_update.foto is not None:
            instructor.foto = instructor_update.foto

        if instructor.id_usuario:
            usuario = session.get(Usuario, instructor.id_usuario)
            if usuario:
                if instructor_update.nombre is not None:
                    usuario.nombre = instructor.nombre
                if instructor_update.apellido is not None:
                    usuario.apellido = instructor.apellido
                if instructor_update.correo is not None:
                    usuario.correo = instructor.correo
                session.add(usuario)

        if instructor_update.competencias is not None:
            existentes = session.exec(
                select(InstructorCompetencia).where(
                    InstructorCompetencia.id_instructor == instructor_id
                )
            ).all()
            for e in existentes:
                session.delete(e)
            session.flush()

            ids_unicos = []
            vistos = set()
            for id_comp in instructor_update.competencias:
                try:
                    cid = int(id_comp)
                except (TypeError, ValueError):
                    continue
                if cid not in vistos:
                    vistos.add(cid)
                    ids_unicos.append(cid)

            for id_comp in ids_unicos:
                session.add(
                    InstructorCompetencia(
                        id_instructor=instructor_id,
                        id_competencia=id_comp,
                    )
                )

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