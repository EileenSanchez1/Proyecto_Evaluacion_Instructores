from typing import Optional

from sqlmodel import SQLModel


class CompetenciaBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    estado: bool = True


class CompetenciaCreate(CompetenciaBase):
    pass


class CompetenciaRead(CompetenciaBase):
    id_competencia: int


class CompetenciaUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[bool] = None
