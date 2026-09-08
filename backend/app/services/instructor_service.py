from typing import List, Optional
from sqlmodel import Session, select
from app.models.instructor import Instructor
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.instructor_competencia import InstructorCompetencia
from app.schemas.instructor import InstructorCreate, InstructorUpdate
from app.services.login_service import LoginService

# Marcador interno: el instructor aún no ha creado su contraseña
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

        # Contraseña temporal: el instructor la creará en su primer acceso
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

        # Asignar competencias si vienen
        if instructor.competencias:
            for id_comp in instructor.competencias:
                rel = InstructorCompetencia(
                    id_instructor=db.id_instructor,
                    id_competencia=id_comp,
                )
                session.add(rel)

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
    def actualizar(session: Session, instructor_id: int, instructor_update: InstructorUpdate) -> Optional[Instructor]:
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return None

        if instructor_update.nombre:
            instructor.nombre = instructor_update.nombre
        if instructor_update.apellido:
            instructor.apellido = instructor_update.apellido
        if instructor_update.correo:
            correo = instructor_update.correo.strip().lower()
            if not correo.endswith("@sena.edu.co"):
                raise ValueError("El correo del instructor debe ser institucional (@sena.edu.co).")
            instructor.correo = correo
        if instructor_update.telefono:
            instructor.telefono = instructor_update.telefono
        if instructor_update.foto is not None:
            instructor.foto = instructor_update.foto

        if instructor.id_usuario:
            usuario = session.get(Usuario, instructor.id_usuario)
            if usuario:
                if instructor_update.nombre:
                    usuario.nombre = instructor_update.nombre
                if instructor_update.apellido:
                    usuario.apellido = instructor_update.apellido
                if instructor_update.correo:
                    usuario.correo = instructor_update.correo.strip().lower()
                session.add(usuario)

        # Reemplazar competencias si se envían
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
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return False
        # Borrar relaciones de competencias
        for rel in session.exec(
            select(InstructorCompetencia).where(
                InstructorCompetencia.id_instructor == instructor_id
            )
        ).all():
            session.delete(rel)
        if instructor.id_usuario:
            usuario = session.get(Usuario, instructor.id_usuario)
            if usuario:
                session.delete(usuario)
        session.delete(instructor)
        session.commit()
        return True

    @staticmethod
    def actualizar_foto(session: Session, instructor_id: int, foto_url: str) -> Optional[Instructor]:
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return None
        instructor.foto = foto_url
        session.add(instructor)
        session.commit()
        session.refresh(instructor)
        return instructor
