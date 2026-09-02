from typing import List, Optional
from sqlmodel import Session, select
from app.models.aprendiz import Aprendiz
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.schemas.aprendiz import AprendizCreate, AprendizUpdate
from app.repositories.aprendiz_repository import AprendizRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.services.login_service import LoginService

class AprendizService:
    @staticmethod
    def crear(session: Session, aprendiz: AprendizCreate) -> Aprendiz:
        if AprendizRepository.buscar_por_correo(session, aprendiz.correo):
            raise ValueError("Ya existe un aprendiz con ese correo.")
        if session.exec(select(Usuario).where(Usuario.correo == aprendiz.correo)).first():
            raise ValueError("Ya existe un usuario con ese correo.")

        rol = session.exec(select(Rol).where(Rol.nombre == "Aprendiz")).first()
        if not rol:
            raise ValueError("El rol 'Aprendiz' no existe. Ejecuta seed_roles.py primero.")

        id_periodo = aprendiz.id_periodo
        if id_periodo is None:
            activos = PeriodoRepository.listar_activos(session)
            if activos:
                id_periodo = activos[0].id_periodo
            else:
                raise ValueError("No hay un periodo activo. Crea un periodo primero.")

        if not PeriodoRepository.buscar(session, id_periodo):
            raise ValueError("El periodo seleccionado no existe.")

        pwd = LoginService.hash_password(aprendiz.contrasena)
        usuario = Usuario(nombre=aprendiz.nombre, apellido=aprendiz.apellido, correo=aprendiz.correo,
                          contrasena=pwd, id_rol=rol.id_rol, activo=True)
        session.add(usuario)
        session.flush()

        db = Aprendiz(nombre=aprendiz.nombre, apellido=aprendiz.apellido, correo=aprendiz.correo,
                      contrasena=pwd, id_ficha=aprendiz.id_ficha, id_periodo=id_periodo, id_usuario=usuario.id_usuario)
        session.add(db)
        session.commit()
        session.refresh(db)
        return db

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
    def listar_por_ficha_y_periodo(session: Session, id_ficha: int, id_periodo: int) -> List[Aprendiz]:
        return AprendizRepository.listar_por_ficha_y_periodo(session, id_ficha, id_periodo)

    @staticmethod
    def actualizar(session: Session, aprendiz_id: int, aprendiz_update: AprendizUpdate) -> Optional[Aprendiz]:
        aprendiz = AprendizRepository.buscar(session, aprendiz_id)
        if not aprendiz: return None
        if aprendiz_update.correo:
            ex = AprendizRepository.buscar_por_correo(session, aprendiz_update.correo)
            if ex and ex.id_aprendiz != aprendiz_id:
                raise ValueError("Ya existe otro aprendiz con ese correo.")
        if aprendiz_update.contrasena:
            aprendiz_update.contrasena = LoginService.hash_password(aprendiz_update.contrasena)
        if aprendiz.id_usuario:
            usuario = session.get(Usuario, aprendiz.id_usuario)
            if usuario:
                if aprendiz_update.nombre: usuario.nombre = aprendiz_update.nombre
                if aprendiz_update.apellido: usuario.apellido = aprendiz_update.apellido
                if aprendiz_update.correo: usuario.correo = aprendiz_update.correo
                if aprendiz_update.contrasena: usuario.contrasena = aprendiz_update.contrasena
                session.add(usuario)
        return AprendizRepository.actualizar(session, aprendiz_id, aprendiz_update)

    @staticmethod
    def eliminar(session: Session, aprendiz_id: int) -> bool:
        aprendiz = AprendizRepository.buscar(session, aprendiz_id)
        if not aprendiz: return False
        if aprendiz.id_usuario:
            usuario = session.get(Usuario, aprendiz.id_usuario)
            if usuario: session.delete(usuario)
        return AprendizRepository.eliminar(session, aprendiz_id)
