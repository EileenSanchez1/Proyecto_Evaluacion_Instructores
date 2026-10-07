from datetime import time
from typing import Optional

from pydantic import field_validator
from sqlmodel import SQLModel

from app.models.horario import DIAS_VALIDOS
from app.schemas.resultado_aprendizaje import ResultadoAprendizajeRead


class HorarioBase(SQLModel):
    id_instructor: int
    id_ficha: int
    dia: str
    hora_inicio: time
    hora_fin: time
    id_resultado: Optional[int] = None
    ambiente: Optional[str] = None

    @field_validator("dia")
    @classmethod
    def validar_dia(cls, valor: str) -> str:
        if valor not in DIAS_VALIDOS:
            raise ValueError(
                f"Día inválido. Debe ser uno de: {', '.join(DIAS_VALIDOS)}"
            )
        return valor


class HorarioCreate(HorarioBase):
    pass


class HorarioRead(HorarioBase):
    id_horario: int
    resultado_aprendizaje: Optional[ResultadoAprendizajeRead] = None


class HorarioUpdate(SQLModel):
    id_instructor: Optional[int] = None
    id_ficha: Optional[int] = None
    dia: Optional[str] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    id_resultado: Optional[int] = None
    ambiente: Optional[str] = None

    @field_validator("dia")
    @classmethod
    def validar_dia(cls, valor: Optional[str]) -> Optional[str]:
        if valor is not None and valor not in DIAS_VALIDOS:
            raise ValueError(
                f"Día inválido. Debe ser uno de: {', '.join(DIAS_VALIDOS)}"
            )
        return valor
