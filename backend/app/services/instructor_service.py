from typing import List, Optional
from sqlmodel import Session, select
from app.models.instructor import Instructor
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.schemas.instructor import InstructorCreate, InstructorUpdate
from app.services.login_service import LoginService

class InstructorService:
    @staticmethod
    def crear(session: Session, instructor: InstructorCreate) -> Instructor:
        if session.exec(select(Instructor).where(Instructor.correo == instructor.correo)).first():
            raise ValueError("Ya existe un instructor con ese correo.")
        if session.exec(select(Usuario).where(Usuario.correo == instructor.correo)).first():
            raise ValueError("Ya existe un usuario con ese correo.")

        rol = session.exec(select(Rol).where(Rol.nombre == "Instructor")).first()
        if not rol:
            raise ValueError("El rol 'Instructor' no existe. Ejecuta seed_roles.py primero.")

        pwd = LoginService.hash_password(instructor.contrasena)
        usuario = Usuario(
            nombre=instructor.nombre,
            apellido=instructor.apellido,
            correo=instructor.correo,
            contrasena=pwd,
            id_rol=rol.id_rol,
            activo=True
        )
        session.add(usuario)
        session.flush()

        db = Instructor(
            nombre=instructor.nombre,
            apellido=instructor.apellido,
            correo=instructor.correo,
            telefono=instructor.telefono,
            foto=instructor.foto,
            id_usuario=usuario.id_usuario
        )
        session.add(db)
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

        if instructor_update.nombre: instructor.nombre = instructor_update.nombre
        if instructor_update.apellido: instructor.apellido = instructor_update.apellido
        if instructor_update.correo: instructor.correo = instructor_update.correo
        if instructor_update.telefono: instructor.telefono = instructor_update.telefono
        if instructor_update.foto is not None: instructor.foto = instructor_update.foto

        # Actualizar usuario asociado
        if instructor.id_usuario:
            usuario = session.get(Usuario, instructor.id_usuario)
            if usuario:
                if instructor_update.nombre: usuario.nombre = instructor_update.nombre
                if instructor_update.apellido: usuario.apellido = instructor_update.apellido
                if instructor_update.correo: usuario.correo = instructor_update.correo
                session.add(usuario)

        session.add(instructor)
        session.commit()
        session.refresh(instructor)
        return instructor

    @staticmethod
    def eliminar(session: Session, instructor_id: int) -> bool:
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return False
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