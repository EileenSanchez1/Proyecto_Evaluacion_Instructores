from sqlmodel import SQLModel


class InstructorCompetenciaBase(SQLModel):
    id_instructor: int
    id_competencia: int


class InstructorCompetenciaCreate(InstructorCompetenciaBase):
    pass


class InstructorCompetenciaRead(InstructorCompetenciaBase):
    id: int
