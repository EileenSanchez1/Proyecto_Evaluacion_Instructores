from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy import delete

from app.models.instructor import Instructor
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.ficha_instructor import FichaInstructor
from app.models.instructor_competencia import InstructorCompetencia
from app.models.horario import Horario
from app.models.respuesta import Respuesta
from app.schemas.instructor import InstructorCreate, InstructorUpdate
from app.repositories.instructor_repository import InstructorRepository
from app.repositories.competencia_repository import CompetenciaRepository
from app.repositories.instructor_competencia_repository import (
    InstructorCompetenciaRepository
)
from app.services.login_service import LoginService
import secrets


class InstructorService:

    @staticmethod
    def _construir_read(instructor: Instructor) -> dict:
        """
        Arma el diccionario que espera InstructorRead, incluyendo
        las competencias asignadas (relación m2m).
        """
        return {
            "id_instructor": instructor.id_instructor,
            "nombre": instructor.nombre,
            "apellido": instructor.apellido,
            "correo": instructor.correo,
            "telefono": instructor.telefono,
            "foto": instructor.foto,
            "competencias": [
                {
                    "id_competencia": ic.competencia.id_competencia,
                    "nombre": ic.competencia.nombre,
                    "descripcion": ic.competencia.descripcion,
                    "estado": ic.competencia.estado,
                }
                for ic in instructor.instructor_competencias
            ],
        }

    @staticmethod
    def _validar_competencias(
        session: Session,
        ids_competencia: List[int]
    ) -> None:
        for id_competencia in ids_competencia:
            if not CompetenciaRepository.buscar(session, id_competencia):
                raise ValueError(
                    f"La competencia con id {id_competencia} no existe."
                )

    @staticmethod
    def _asignar_competencias(
        session: Session,
        id_instructor: int,
        ids_competencia: List[int]
    ) -> None:
        # Reemplaza el conjunto completo de competencias del instructor.
        InstructorCompetenciaRepository.eliminar_por_instructor(
            session, id_instructor
        )
        for id_competencia in ids_competencia:
            InstructorCompetenciaRepository.crear(
                session, id_instructor, id_competencia
            )

    @staticmethod
    def crear(session: Session, instructor: InstructorCreate) -> dict:
        # Verificar que no exista un instructor con ese correo
        existente = InstructorRepository.buscar_por_correo(
            session, instructor.correo
        )
        if existente:
            raise ValueError("Ya existe un instructor con ese correo.")

        # Verificar que no exista un usuario con ese correo
        usuario_existente = session.exec(
            select(Usuario).where(Usuario.correo == instructor.correo)
        ).first()
        if usuario_existente:
            raise ValueError("Ya existe un usuario con ese correo.")

        # Obtener el rol "Instructor"
        rol_instructor = session.exec(
            select(Rol).where(Rol.nombre == "Instructor")
        ).first()
        if not rol_instructor:
            raise ValueError("El rol 'Instructor' no existe. Ejecuta seed_roles.py primero.")

        # Validar competencias
        InstructorService._validar_competencias(
            session, instructor.competencias
        )

        # Crear el Usuario primero (con contraseña temporal)
        clave_temporal = secrets.token_urlsafe(9)
        contrasena_hash = LoginService.hash_password(clave_temporal)

        usuario = Usuario(
            nombre=instructor.nombre,
            apellido=instructor.apellido,
            correo=instructor.correo,
            contrasena=contrasena_hash,
            id_rol=rol_instructor.id_rol,
            activo=True
        )
        session.add(usuario)
        session.flush()  # Obtener id_usuario

        # Crear el Instructor vinculado al Usuario
        db_instructor = InstructorRepository.crear(session, instructor)
        db_instructor.id_usuario = usuario.id_usuario
        session.add(db_instructor)
        session.flush()

        # Asignar competencias
        if instructor.competencias:
            InstructorService._asignar_competencias(
                session,
                db_instructor.id_instructor,
                instructor.competencias
            )
            session.refresh(db_instructor)

        session.commit()
        session.refresh(db_instructor)

        print(
            f"[DEV] Instructor creado: {instructor.correo} "
            f"-> clave temporal: {clave_temporal}"
        )

        return InstructorService._construir_read(db_instructor)

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[dict]:
        instructores = InstructorRepository.listar(session, offset, limit)
        return [
            InstructorService._construir_read(i) for i in instructores
        ]

    @staticmethod
    def buscar(session: Session, instructor_id: int) -> Optional[dict]:
        instructor = InstructorRepository.buscar(session, instructor_id)
        if not instructor:
            return None
        return InstructorService._construir_read(instructor)

    @staticmethod
    def actualizar(
        session: Session,
        instructor_id: int,
        instructor_update: InstructorUpdate
    ) -> Optional[dict]:

        instructor = InstructorRepository.buscar(session, instructor_id)
        if not instructor:
            return None

        if instructor_update.correo:
            existente = InstructorRepository.buscar_por_correo(
                session, instructor_update.correo
            )
            if existente and existente.id_instructor != instructor_id:
                raise ValueError(
                    "Ya existe otro instructor con ese correo."
                )

        if instructor_update.competencias is not None:
            InstructorService._validar_competencias(
                session, instructor_update.competencias
            )

        db_instructor = InstructorRepository.actualizar(
            session, instructor_id, instructor_update
        )

        # Actualizar también el usuario vinculado si cambian datos compartidos
        if instructor.id_usuario:
            usuario = session.get(Usuario, instructor.id_usuario)
            if usuario:
                if instructor_update.nombre:
                    usuario.nombre = instructor_update.nombre
                if instructor_update.apellido:
                    usuario.apellido = instructor_update.apellido
                if instructor_update.correo:
                    usuario.correo = instructor_update.correo
                if instructor_update.foto:
                    usuario.foto = instructor_update.foto
                session.add(usuario)

        if instructor_update.competencias is not None:
            InstructorService._asignar_competencias(
                session, instructor_id, instructor_update.competencias
            )
            session.refresh(db_instructor)

        session.commit()
        return InstructorService._construir_read(db_instructor)

    @staticmethod
    def eliminar(session: Session, instructor_id: int) -> bool:
        instructor = session.get(Instructor, instructor_id)
        if not instructor:
            return False

        # CORREGIDO: eliminar relaciones primero para evitar errores de FK
        session.exec(
            delete(FichaInstructor)
            .where(FichaInstructor.id_instructor == instructor_id)
        )
        session.exec(
            delete(InstructorCompetencia)
            .where(InstructorCompetencia.id_instructor == instructor_id)
        )
        session.exec(
            delete(Horario)
            .where(Horario.id_instructor == instructor_id)
        )
        session.exec(
            delete(Respuesta)
            .where(Respuesta.id_instructor == instructor_id)
        )

        # Eliminar usuario vinculado
        if instructor.id_usuario:
            usuario = session.get(Usuario, instructor.id_usuario)
            if usuario:
                session.delete(usuario)

        # Eliminar instructor
        session.delete(instructor)
        session.commit()

        return True
