from typing import List, Optional

from sqlmodel import Session, select

from app.models.aprendiz import Aprendiz
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.schemas.aprendiz import AprendizCreate, AprendizUpdate
from app.repositories.aprendiz_repository import AprendizRepository
from app.services.login_service import LoginService


class AprendizService:

    @staticmethod
    def crear(session: Session, aprendiz: AprendizCreate) -> Aprendiz:
        # 1. Verificar si ya existe un aprendiz con ese correo
        existente = AprendizRepository.buscar_por_correo(
            session, aprendiz.correo
        )
        if existente:
            raise ValueError("Ya existe un aprendiz con ese correo.")

        # 2. Verificar que no exista un usuario con ese correo
        usuario_existente = session.exec(
            select(Usuario).where(Usuario.correo == aprendiz.correo)
        ).first()
        if usuario_existente:
            raise ValueError("Ya existe un usuario con ese correo.")

        # 3. Obtener el rol "Aprendiz"
        rol_aprendiz = session.exec(
            select(Rol).where(Rol.nombre == "Aprendiz")
        ).first()
        if not rol_aprendiz:
            raise ValueError("El rol 'Aprendiz' no existe. Ejecuta seed_roles.py primero.")

        # 4. Hashear la contraseña
        contrasena_hash = LoginService.hash_password(aprendiz.contrasena)

        # 5. Crear el Usuario primero
        usuario = Usuario(
            nombre=aprendiz.nombre,
            apellido=aprendiz.apellido,
            correo=aprendiz.correo,
            contrasena=contrasena_hash,
            id_rol=rol_aprendiz.id_rol,
            activo=True
        )
        session.add(usuario)
        session.flush()  # Obtener id_usuario sin hacer commit aún

        # 6. Crear el Aprendiz vinculado al Usuario
        db_aprendiz = Aprendiz(
            nombre=aprendiz.nombre,
            apellido=aprendiz.apellido,
            correo=aprendiz.correo,
            contrasena=contrasena_hash,
            id_ficha=aprendiz.id_ficha,
            id_usuario=usuario.id_usuario
        )
        session.add(db_aprendiz)
        session.commit()
        session.refresh(db_aprendiz)

        return db_aprendiz

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
    def actualizar(
        session: Session,
        aprendiz_id: int,
        aprendiz_update: AprendizUpdate
    ) -> Optional[Aprendiz]:

        aprendiz = AprendizRepository.buscar(session, aprendiz_id)
        if not aprendiz:
            return None

        # Si cambia el correo, verificar que no exista otro aprendiz con ese correo
        if aprendiz_update.correo:
            existente = AprendizRepository.buscar_por_correo(
                session, aprendiz_update.correo
            )
            if existente and existente.id_aprendiz != aprendiz_id:
                raise ValueError("Ya existe otro aprendiz con ese correo.")

        # Si cambia la contraseña, hashearla
        if aprendiz_update.contrasena:
            aprendiz_update.contrasena = LoginService.hash_password(
                aprendiz_update.contrasena
            )

        # Actualizar también el usuario vinculado si cambian datos compartidos
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

        # Eliminar también el usuario vinculado
        if aprendiz.id_usuario:
            usuario = session.get(Usuario, aprendiz.id_usuario)
            if usuario:
                session.delete(usuario)

        return AprendizRepository.eliminar(session, aprendiz_id)
