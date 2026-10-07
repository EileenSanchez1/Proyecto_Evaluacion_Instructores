from typing import List, Optional
from sqlmodel import Session
from app.models.ficha_instructor import FichaInstructor
from app.schemas.ficha_instructor import FichaInstructorCreate, FichaInstructorUpdate
from app.repositories.ficha_instructor_repository import FichaInstructorRepository
from app.repositories.ficha_repository import FichaRepository
from app.repositories.instructor_repository import InstructorRepository
from app.repositories.periodo_repository import PeriodoRepository


class FichaInstructorService:
    @staticmethod
    def crear(session: Session, ficha_instructor: FichaInstructorCreate) -> FichaInstructor:
        if not FichaRepository.buscar(session, ficha_instructor.id_ficha):
            raise ValueError("La ficha no existe.")
        if not InstructorRepository.buscar(session, ficha_instructor.id_instructor):
            raise ValueError("El instructor no existe.")
        periodo = PeriodoRepository.buscar(session, ficha_instructor.id_periodo)
        if not periodo:
            raise ValueError("El periodo no existe.")
        if str(getattr(periodo, "estado", "")).lower() != "activo":
            raise ValueError(
                "No se puede asignar instructor a un periodo desactivado. "
                "Activa el periodo o elige uno activo."
            )

        # Si ya existe (aunque desactivada) → reactivar y actualizar RA
        existente = FichaInstructorRepository.buscar_asignacion_cualquier(
            session,
            ficha_instructor.id_ficha,
            ficha_instructor.id_instructor,
            ficha_instructor.id_periodo,
        )
        if existente:
            if getattr(existente, "activo", True):
                raise ValueError(
                    "El instructor ya está asignado a esta ficha en el periodo seleccionado."
                )
            # Reactivar y actualizar RA
            update = FichaInstructorUpdate(
                id_resultado=ficha_instructor.id_resultado,
                activo=True,
            )
            return FichaInstructorRepository.actualizar(session, existente.id, update)

        return FichaInstructorRepository.crear(session, ficha_instructor)

    @staticmethod
    def buscar(session: Session, relacion_id: int) -> Optional[FichaInstructor]:
        return FichaInstructorRepository.buscar(session, relacion_id)

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar(session, offset, limit)

    @staticmethod
    def listar_por_ficha(session: Session, id_ficha: int) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar_por_ficha(session, id_ficha)

    @staticmethod
    def listar_por_ficha_y_periodo(
        session: Session, id_ficha: int, id_periodo: int
    ) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar_por_ficha_y_periodo(
            session, id_ficha, id_periodo, solo_activos=True
        )

    @staticmethod
    def listar_por_instructor(session: Session, id_instructor: int) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar_por_instructor(session, id_instructor)

    @staticmethod
    def actualizar(
        session: Session, relacion_id: int, update: FichaInstructorUpdate
    ) -> Optional[FichaInstructor]:
        relacion = FichaInstructorRepository.buscar(session, int(relacion_id))
        if not relacion:
            return None

        id_ficha = update.id_ficha if update.id_ficha is not None else relacion.id_ficha
        id_instructor = (
            update.id_instructor
            if update.id_instructor is not None
            else relacion.id_instructor
        )
        id_periodo = (
            update.id_periodo if update.id_periodo is not None else relacion.id_periodo
        )

        if not FichaRepository.buscar(session, id_ficha):
            raise ValueError("La ficha no existe.")
        if not InstructorRepository.buscar(session, id_instructor):
            raise ValueError("El instructor no existe.")
        periodo = PeriodoRepository.buscar(session, id_periodo)
        if not periodo:
            raise ValueError("El periodo no existe.")

        # Conflicto solo con OTRA asignación ACTIVA del mismo triple
        ex = FichaInstructorRepository.buscar_asignacion(
            session, id_ficha, id_instructor, id_periodo, solo_activos=True
        )
        if ex is not None and int(ex.id) != int(relacion_id):
            raise ValueError(
                "El instructor ya está asignado a esta ficha en el periodo seleccionado."
            )

        # Si el periodo/RA cambian y hay una fila desactivada en el destino, no choca por unique
        # (unique incluye desactivadas). Si existe desactivada con el nuevo triple y no es esta, error de unique.
        otra_cualquiera = FichaInstructorRepository.buscar_asignacion_cualquier(
            session, id_ficha, id_instructor, id_periodo
        )
        if (
            otra_cualquiera is not None
            and int(otra_cualquiera.id) != int(relacion_id)
            and not getattr(otra_cualquiera, "activo", True)
        ):
            # Hay una desactivada en el periodo destino: reactivarla con el RA nuevo y desactivar la actual
            FichaInstructorRepository.actualizar(
                session,
                otra_cualquiera.id,
                FichaInstructorUpdate(
                    id_resultado=(
                        update.id_resultado
                        if update.id_resultado is not None
                        else relacion.id_resultado
                    ),
                    activo=True,
                ),
            )
            # Desactivar la fila original
            FichaInstructorRepository.desactivar(session, int(relacion_id))
            return FichaInstructorRepository.buscar(session, otra_cualquiera.id)

        return FichaInstructorRepository.actualizar(session, int(relacion_id), update)

    @staticmethod
    def desactivar(session: Session, relacion_id: int) -> bool:
        return FichaInstructorRepository.desactivar(session, int(relacion_id))

    @staticmethod
    def reactivar(session: Session, relacion_id: int) -> Optional[FichaInstructor]:
        return FichaInstructorRepository.reactivar(session, int(relacion_id))

    @staticmethod
    def eliminar(session: Session, relacion_id: int) -> bool:
        # Soft-delete por defecto
        return FichaInstructorRepository.desactivar(session, int(relacion_id))
