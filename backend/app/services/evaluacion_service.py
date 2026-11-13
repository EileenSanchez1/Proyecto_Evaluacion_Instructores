from typing import List, Optional
from sqlmodel import Session
from app.models.evaluacion import Evaluacion
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionUpdate
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.aprendiz_repository import AprendizRepository
from app.repositories.instructor_repository import InstructorRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.repositories.ficha_instructor_repository import FichaInstructorRepository


class EvaluacionService:
    @staticmethod
    def _validar_pertenencia(
        session: Session,
        id_aprendiz: int,
        id_instructor: int,
        id_periodo: int,
    ) -> None:
        """
        Regla de negocio crítica:
        - El aprendiz solo puede evaluar instructores asignados (activos)
          a su misma ficha en el periodo de evaluación (periodo operativo activo).
        - El id_periodo del aprendiz es de registro y puede diferir del periodo
          activo; no se exige coincidencia exacta.
        - Evita evaluaciones fuera de contexto (otra ficha / periodo cerrado).
        """
        aprendiz = AprendizRepository.buscar(session, id_aprendiz)
        if not aprendiz:
            raise ValueError("El aprendiz no existe.")

        if not getattr(aprendiz, "id_ficha", None):
            raise ValueError(
                "El aprendiz no tiene ficha de formación asignada. Contacta al coordinador."
            )

        # El id_periodo del aprendiz es el de registro/matrícula y puede quedar
        # desfasado respecto al periodo operativo activo. La validación real es:
        # instructor activo en la misma ficha del aprendiz para el periodo de evaluación.
        asignacion = FichaInstructorRepository.buscar_asignacion(
            session,
            id_ficha=aprendiz.id_ficha,
            id_instructor=id_instructor,
            id_periodo=id_periodo,
            solo_activos=True,
        )
        if not asignacion:
            raise ValueError(
                "El instructor no está asignado (activo) a la ficha del aprendiz en este periodo. "
                "No se puede iniciar ni registrar esta evaluación."
            )

        periodo = PeriodoRepository.buscar(session, id_periodo)
        if not periodo:
            raise ValueError("El periodo no existe.")
        estado = str(getattr(periodo, "estado", "") or "").lower()
        if estado and estado not in ("activo", "abierto", "en curso"):
            # Permite si el periodo no tiene estado estricto; bloquea solo si está claramente cerrado
            if estado in ("cerrado", "inactivo", "finalizado", "cerrada"):
                raise ValueError(
                    "No se pueden crear evaluaciones en un periodo cerrado o inactivo."
                )

    @staticmethod
    def crear(session: Session, evaluacion: EvaluacionCreate) -> Evaluacion:
        if not AprendizRepository.buscar(session, evaluacion.id_aprendiz):
            raise ValueError("El aprendiz no existe.")
        if not InstructorRepository.buscar(session, evaluacion.id_instructor):
            raise ValueError("El instructor no existe.")
        periodo = PeriodoRepository.buscar(session, evaluacion.id_periodo)
        if not periodo:
            raise ValueError("El periodo no existe.")

        # Pertenencia ficha-instructor-periodo (regla de negocio)
        EvaluacionService._validar_pertenencia(
            session,
            evaluacion.id_aprendiz,
            evaluacion.id_instructor,
            evaluacion.id_periodo,
        )

        existente = EvaluacionRepository.buscar_por_aprendiz_instructor_periodo(
            session,
            evaluacion.id_aprendiz,
            evaluacion.id_instructor,
            evaluacion.id_periodo,
        )
        if existente:
            # Si ya está Completada, no se permite otra
            estado = (existente.estado or "").strip().lower()
            if estado in ("completada", "finalizada", "enviada", "respondida", "evaluado"):
                raise ValueError(
                    "El aprendiz ya completó la evaluación de este instructor en este periodo."
                )
            # Si está Pendiente, devolver la existente (idempotente)
            return existente

        return EvaluacionRepository.crear(session, evaluacion)

    @staticmethod
    def buscar(session: Session, evaluacion_id: int) -> Optional[Evaluacion]:
        return EvaluacionRepository.buscar(session, evaluacion_id)

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Evaluacion]:
        return EvaluacionRepository.listar(session, offset, limit)

    @staticmethod
    def listar_por_aprendiz(session: Session, id_aprendiz: int) -> List[Evaluacion]:
        return EvaluacionRepository.listar_por_aprendiz(session, id_aprendiz)

    @staticmethod
    def listar_por_instructor(session: Session, id_instructor: int) -> List[Evaluacion]:
        return EvaluacionRepository.listar_por_instructor(session, id_instructor)

    @staticmethod
    def buscar_por_aprendiz_instructor_periodo(
        session: Session, id_aprendiz: int, id_instructor: int, id_periodo: int
    ) -> Optional[Evaluacion]:
        return EvaluacionRepository.buscar_por_aprendiz_instructor_periodo(
            session, id_aprendiz, id_instructor, id_periodo
        )

    @staticmethod
    def actualizar(
        session: Session, evaluacion_id: int, evaluacion_update: EvaluacionUpdate
    ) -> Optional[Evaluacion]:
        db = EvaluacionRepository.buscar(session, evaluacion_id)
        if not db:
            return None
        estado_actual = (db.estado or "").strip().lower()
        cerrados = ("completada", "finalizada", "enviada", "respondida", "evaluado")
        if estado_actual in cerrados:
            # Evaluación ya cerrada: solo se permite actualizar la observación general
            # (el bulk de respuestas marca Evaluado antes de guardar la observación).
            data = evaluacion_update.model_dump(exclude_unset=True)
            claves = set(data.keys())
            if not claves.issubset({"observacion_general"}):
                raise ValueError(
                    "No se puede modificar una evaluación ya completada."
                )
            # No permitir reabrir ni cambiar estado desde este camino
            data.pop("estado", None)
            evaluacion_update = EvaluacionUpdate(**data)
        return EvaluacionRepository.actualizar(session, evaluacion_id, evaluacion_update)

    @staticmethod
    def actualizar_estado(
        session: Session, evaluacion_id: int, estado: str
    ) -> Optional[Evaluacion]:
        db = EvaluacionRepository.buscar(session, evaluacion_id)
        if not db:
            return None
        estado_actual = (db.estado or "").strip().lower()
        nuevo = (estado or "").strip()
        if estado_actual in ("completada", "finalizada", "enviada", "respondida", "evaluado") and nuevo.lower() not in (
            "completada",
            "finalizada",
            "enviada",
            "respondida",
            "evaluado",
        ):
            raise ValueError("No se puede reabrir una evaluación ya completada.")
        return EvaluacionRepository.actualizar_estado(session, evaluacion_id, nuevo)

    @staticmethod
    def eliminar(session: Session, evaluacion_id: int) -> bool:
        return EvaluacionRepository.eliminar(session, evaluacion_id)
