from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.aprendiz import Aprendiz
from app.models.instructor import Instructor
from app.models.ficha import Ficha
from app.models.resultado_aprendizaje import ResultadoAprendizaje
from app.models.periodo import Periodo
from app.models.pregunta import Pregunta
from app.models.evaluacion import Evaluacion
from app.models.respuesta import Respuesta
from app.models.ficha_instructor import FichaInstructor
from app.models.instructor_resultado_aprendizaje import InstructorResultadoAprendizaje
from app.models.horario import Horario
from app.models.auditoria import Auditoria
from app.models.notificacion import Notificacion
from app.models.novedad import Novedad

# Compatibilidad temporal: alias Competencia → ResultadoAprendizaje
# (por si algún script antiguo aún importa Competencia)
Competencia = ResultadoAprendizaje
InstructorCompetencia = InstructorResultadoAprendizaje
