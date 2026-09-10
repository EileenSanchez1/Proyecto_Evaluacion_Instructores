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
            raise ValueError("El correo del instructor debe ser institucional (@sena.edu.co).")

        if session.exec(select(Instructor).where(Instructor.correo == correo)).first():
            raise ValueError("Ya existe un instructor con ese correo.")
        if session.exec(select(Usuario).where(Usuario.correo == correo)).first():
            raise ValueError("Ya existe un usuario con ese correo.")

        rol = session.exec(select(Rol).where(Rol.nombre == "Instructor")).first()
        if not rol:
            raise ValueError("El rol 'Instructor' no existe. Ejecuta seed_roles.py primero.")

        # Primer acceso: el instructor creará su contraseña con código
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
    def listar(session: Session) -> List[Instructor]:
        return session.exec(select(Instructor)).all()

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
            for id_comp in instructor_update.competencias:
                session.add(
                    InstructorCompetencia(
                        id_instructor=instructor_id,
                        id_competencia=id_comp,
                    )
                )

        session.add(instructor)
        session.commit()
        session.refresh(instructor)
        return instructor

    @staticmethod
    def eliminar(session: Session, instructor_id: int) -> bool:
        """
        Elimina instructor y todas sus dependencias
        (respuestas, evaluaciones, fichas, horarios, competencias, usuario).
        """
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return False

        try:
            # 1) Respuestas ligadas al instructor
            for r in session.exec(
                select(Respuesta).where(Respuesta.id_instructor == instructor_id)
            ).all():
                session.delete(r)

            # 2) Evaluaciones (y respuestas residuales por evaluación)
            evaluaciones = session.exec(
                select(Evaluacion).where(Evaluacion.id_instructor == instructor_id)
            ).all()
            for ev in evaluaciones:
                for r in session.exec(
                    select(Respuesta).where(Respuesta.id_evaluacion == ev.id_evaluacion)
                ).all():
                    session.delete(r)
                session.delete(ev)

            # 3) Asignaciones ficha–instructor
            for fi in session.exec(
                select(FichaInstructor).where(
                    FichaInstructor.id_instructor == instructor_id
                )
            ).all():
                session.delete(fi)

            # 4) Horarios
            for h in session.exec(
                select(Horario).where(Horario.id_instructor == instructor_id)
            ).all():
                session.delete(h)

            # 5) Competencias
            for rel in session.exec(
                select(InstructorCompetencia).where(
                    InstructorCompetencia.id_instructor == instructor_id
                )
            ).all():
                session.delete(rel)

            # 6) Usuario vinculado
            if instructor.id_usuario:
                usuario = session.get(Usuario, instructor.id_usuario)
                if usuario:
                    session.delete(usuario)

            # 7) Instructor
            session.delete(instructor)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise ValueError(f"No se pudo eliminar el instructor: {e}") from e

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
