from typing import List, Optional

from sqlmodel import Session

from app.models.aprendiz import Aprendiz
from app.schemas.aprendiz import AprendizCreate, AprendizUpdate
from app.repositories.aprendiz_repository import AprendizRepository
from app.services.login_service import LoginService


class AprendizService:

    @staticmethod
    def crear(
        session: Session,
        aprendiz: AprendizCreate
    ) -> Aprendiz:

        # Verificar si ya existe un aprendiz con ese correo
        existente = AprendizRepository.buscar_por_correo(
            session,
            aprendiz.correo
        )

        if existente:
            raise ValueError(
                "Ya existe un aprendiz con ese correo."
            )

        # Convertir los datos recibidos a un diccionario
        datos = aprendiz.model_dump()

        # Hashear la contraseña antes de guardarla
        datos["contrasena"] = LoginService.hash_password(
            aprendiz.contrasena
        )

        # Crear un nuevo objeto AprendizCreate
        aprendiz_con_hash = AprendizCreate(
            **datos
        )

        return AprendizRepository.crear(
            session,
            aprendiz_con_hash
        )

    @staticmethod
    def buscar(
        session: Session,
        aprendiz_id: int
    ) -> Optional[Aprendiz]:

        return AprendizRepository.buscar(
            session,
            aprendiz_id
        )

    @staticmethod
    def buscar_por_correo(
        session: Session,
        correo: str
    ) -> Optional[Aprendiz]:

        return AprendizRepository.buscar_por_correo(
            session,
            correo
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Aprendiz]:

        return AprendizRepository.listar(
            session,
            offset,
            limit
        )

    @staticmethod
    def listar_por_ficha(
        session: Session,
        id_ficha: int
    ) -> List[Aprendiz]:

        return AprendizRepository.listar_por_ficha(
            session,
            id_ficha
        )

    @staticmethod
    def actualizar(
        session: Session,
        aprendiz_id: int,
        aprendiz_update: AprendizUpdate
    ) -> Optional[Aprendiz]:

        aprendiz = AprendizRepository.buscar(
            session,
            aprendiz_id
        )

        if not aprendiz:
            return None

        if aprendiz_update.correo:

            existente = AprendizRepository.buscar_por_correo(
                session,
                aprendiz_update.correo
            )

            if (
                existente
                and existente.id_aprendiz != aprendiz_id
            ):
                raise ValueError(
                    "Ya existe otro aprendiz con ese correo."
                )

        if aprendiz_update.contrasena:
            aprendiz_update.contrasena = LoginService.hash_password(
                aprendiz_update.contrasena
            )

        return AprendizRepository.actualizar(
            session,
            aprendiz_id,
            aprendiz_update
        )

    @staticmethod
    def eliminar(
        session: Session,
        aprendiz_id: int
    ) -> bool:

        return AprendizRepository.eliminar(
            session,
            aprendiz_id
        )