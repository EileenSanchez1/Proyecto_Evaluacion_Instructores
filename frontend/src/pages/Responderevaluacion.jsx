import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { obtenerEvaluacion, actualizarEstadoEvaluacion } from "../services/Evaluacionservice";
import { listarPreguntasActivas } from "../services/Preguntaservice";
import { crearRespuestasBulk } from "../services/Respuestaservice";
import { obtenerInstructor } from "../services/instructorService";
import { obtenerUsuarioSesion } from "../utils/sesion";
import "../styles/Evaluaciones.css";

function ResponderEvaluacion() {
  const { id } = useParams();
  const navigate = useNavigate();
  const usuario = obtenerUsuarioSesion();

  const [evaluacion, setEvaluacion] = useState(null);
  const [instructor, setInstructor] = useState(null);
  const [preguntas, setPreguntas] = useState([]);
  const [respuestas, setRespuestas] = useState({});
  const [observaciones, setObservaciones] = useState("");
  const [cargando, setCargando] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        setCargando(true);
        setError("");

        const [ev, p] = await Promise.all([
          obtenerEvaluacion(id),
          listarPreguntasActivas()
        ]);

        setEvaluacion(ev);
        setPreguntas(p);

        const inst = await obtenerInstructor(ev.id_instructor);
        setInstructor(inst);

        // Inicializar respuestas vacías
        const respuestasIniciales = {};
        p.forEach((preg) => {
          respuestasIniciales[preg.id_pregunta] = { calificacion: 3, observacion: "" };
        });
        setRespuestas(respuestasIniciales);
      } catch (err) {
        console.error(err);
        setError("No se pudieron cargar los datos de la evaluación.");
      } finally {
        setCargando(false);
      }
    };

    cargarDatos();
  }, [id]);

  const manejarCalificacion = (idPregunta, valor) => {
    setRespuestas((prev) => ({
      ...prev,
      [idPregunta]: { ...prev[idPregunta], calificacion: Number(valor) }
    }));
  };

  const manejarObservacionPregunta = (idPregunta, valor) => {
    setRespuestas((prev) => ({
      ...prev,
      [idPregunta]: { ...prev[idPregunta], observacion: valor }
    }));
  };

  const manejarEnviar = async (e) => {
    e.preventDefault();
    setError("");

    // Validar que todas las preguntas tengan calificación
    const faltantes = preguntas.filter((p) => !respuestas[p.id_pregunta]?.calificacion);
    if (faltantes.length > 0) {
      setError(`Faltan ${faltantes.length} pregunta(s) por calificar.`);
      return;
    }

    try {
      setEnviando(true);

      const respuestasPayload = preguntas.map((p) => ({
        id_evaluacion: Number(id),
        id_pregunta: p.id_pregunta,
        id_instructor: evaluacion.id_instructor,
        respuesta: respuestas[p.id_pregunta].calificacion,
        observaciones: respuestas[p.id_pregunta].observacion || null
      }));

      await crearRespuestasBulk(respuestasPayload);
      await actualizarEstadoEvaluacion(Number(id), "Evaluado");

      navigate("/evaluaciones");
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(typeof detalle === "string" ? detalle : "Error al enviar la evaluación.");
    } finally {
      setEnviando(false);
    }
  };

  if (cargando) {
    return (
      <div className="pagina-evaluaciones">
        <p className="text-muted">Cargando evaluación...</p>
      </div>
    );
  }

  if (!evaluacion || !instructor) {
    return (
      <div className="pagina-evaluaciones">
        <div className="alerta alerta-error">Evaluación no encontrada.</div>
      </div>
    );
  }

  const yaEvaluado = evaluacion.estado === "Evaluado";

  return (
    <div className="pagina-evaluaciones">
      <div className="encabezado">
        <div>
          <h1 className="titulo">
            {yaEvaluado ? "Resultado de Evaluación" : "Evaluar Instructor"}
          </h1>
          <p className="subtitulo">
            {yaEvaluado
              ? `Evaluación realizada el ${new Date(evaluacion.fecha).toLocaleDateString()}`
              : `Califica a ${instructor.nombre} ${instructor.apellido} según cada criterio`}
          </p>
        </div>
        <button className="btn-volver" onClick={() => navigate("/evaluaciones")}>
          <i className="bi bi-arrow-left"></i> Volver
        </button>
      </div>

      {error && <div className="alerta alerta-error">{error}</div>}

      <div className="instructor-info-card">
        <div className="perfil">
          {instructor.foto ? (
            <img className="foto" src={`http://localhost:8000${instructor.foto}`} alt={instructor.nombre} />
          ) : (
            <div className="foto-placeholder"><i className="bi bi-person-fill"></i></div>
          )}
          <div>
            <h3>{instructor.nombre} {instructor.apellido}</h3>
            <p>{instructor.correo}</p>
          </div>
        </div>
      </div>

      {preguntas.length === 0 ? (
        <div className="estado-vacio">
          <i className="bi bi-exclamation-circle"></i>
          <h4>No hay preguntas configuradas</h4>
          <p>Contacta al administrador para que configure las preguntas de evaluación.</p>
        </div>
      ) : (
        <form onSubmit={manejarEnviar} className="formulario-evaluacion">
          {preguntas.map((pregunta, index) => (
            <div className="pregunta-card" key={pregunta.id_pregunta}>
              <div className="pregunta-numero">Pregunta {index + 1}</div>
              <h4 className="pregunta-texto">{pregunta.texto}</h4>
              <p className="pregunta-categoria">
                <i className="bi bi-tag"></i> {pregunta.categoria}
              </p>

              <div className="calificacion-grupo">
                <label>Calificación (1 = Muy deficiente, 5 = Excelente)</label>
                <div className="escala-calificacion">
                  {[1, 2, 3, 4, 5].map((valor) => (
                    <label key={valor} className="opcion-calificacion">
                      <input
                        type="radio"
                        name={`calificacion-${pregunta.id_pregunta}`}
                        value={valor}
                        checked={respuestas[pregunta.id_pregunta]?.calificacion === valor}
                        onChange={() => manejarCalificacion(pregunta.id_pregunta, valor)}
                        disabled={yaEvaluado}
                      />
                      <span className={`circulo ${respuestas[pregunta.id_pregunta]?.calificacion === valor ? "seleccionado" : ""}`}>
                        {valor}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="campo-observacion">
                <label>Observaciones (opcional)</label>
                <textarea
                  rows={2}
                  placeholder="Escribe tus comentarios sobre este criterio..."
                  value={respuestas[pregunta.id_pregunta]?.observacion || ""}
                  onChange={(e) => manejarObservacionPregunta(pregunta.id_pregunta, e.target.value)}
                  disabled={yaEvaluado}
                />
              </div>
            </div>
          ))}

          <div className="campo-observacion-general">
            <label>Observaciones generales de la evaluación</label>
            <textarea
              rows={3}
              placeholder="Comentarios generales sobre el instructor..."
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
              disabled={yaEvaluado}
            />
          </div>

          {!yaEvaluado && (
            <div className="acciones-formulario">
              <button type="button" className="btn-cancelar" onClick={() => navigate("/evaluaciones")}>
                Cancelar
              </button>
              <button type="submit" className="btn-enviar" disabled={enviando}>
                <i className="bi bi-send"></i>
                {enviando ? "Enviando..." : "Enviar evaluación"}
              </button>
            </div>
          )}
        </form>
      )}
    </div>
  );
}

export default ResponderEvaluacion;
