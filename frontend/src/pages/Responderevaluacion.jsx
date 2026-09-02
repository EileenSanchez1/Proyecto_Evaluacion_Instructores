import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { obtenerEvaluacion, actualizarEstadoEvaluacion } from "../services/Evaluacionservice";
import { listarPreguntasActivas } from "../services/Preguntaservice";
import { crearRespuestasBulk, listarRespuestasPorEvaluacion } from "../services/Respuestaservice";
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
  const [observacionesGenerales, setObservacionesGenerales] = useState("");
  const [cargando, setCargando] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState("");
  const [promedio, setPromedio] = useState(0);

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

        const yaEvaluado = ev.estado === "Evaluado";

        if (yaEvaluado) {
          // ── CARGAR RESPUESTAS REALES ──
          const respuestasGuardadas = await listarRespuestasPorEvaluacion(Number(id));

          const respuestasMap = {};
          let suma = 0;
          let observacionGeneral = "";

          respuestasGuardadas.forEach((r) => {
            respuestasMap[r.id_pregunta] = {
              calificacion: r.respuesta,
              observacion: r.observaciones || ""
            };
            suma += r.respuesta;
            if (r.observaciones && !observacionGeneral) {
              observacionGeneral = r.observaciones;
            }
          });

          setRespuestas(respuestasMap);
          setObservacionesGenerales(observacionGeneral);

          if (respuestasGuardadas.length > 0) {
            setPromedio((suma / respuestasGuardadas.length).toFixed(1));
          }
        } else {
          // Inicializar respuestas vacías
          const respuestasIniciales = {};
          p.forEach((preg) => {
            respuestasIniciales[preg.id_pregunta] = { calificacion: 0, observacion: "" };
          });
          setRespuestas(respuestasIniciales);
          setPromedio(0);
        }
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

    const faltantes = preguntas.filter((p) => !respuestas[p.id_pregunta]?.calificacion || respuestas[p.id_pregunta]?.calificacion === 0);
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
        <div className="cargando-centrado">
          <div className="spinner"></div>
          <p>Cargando evaluación...</p>
        </div>
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
      <div className="encabezado-evaluacion">
        <div>
          <h1 className="titulo-principal">
            {yaEvaluado ? "Resultado de Evaluación" : "Evaluar Instructor"}
          </h1>
          <p className="subtitulo-principal">
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

      {/* Tarjeta del instructor */}
      <div className="instructor-card-destacado">
        <div className="instructor-perfil">
          {instructor.foto ? (
            <img className="instructor-foto-lg" src={`http://localhost:8000${instructor.foto}`} alt={instructor.nombre} />
          ) : (
            <div className="instructor-foto-placeholder-lg">
              <i className="bi bi-person-fill"></i>
            </div>
          )}
          <div className="instructor-datos">
            <h3>{instructor.nombre} {instructor.apellido}</h3>
            <p><i className="bi bi-envelope"></i> {instructor.correo}</p>
            {instructor.telefono && <p><i className="bi bi-telephone"></i> {instructor.telefono}</p>}
          </div>
        </div>
      </div>

      {/* ── RESUMEN DE RESULTADOS (solo cuando ya evaluado) ── */}
      {yaEvaluado && (
        <div className="resultado-resumen">
          <div className="resultado-promedio">
            <div className="resultado-circulo">
              <span className="resultado-numero">{promedio}</span>
              <span className="resultado-de">de 5</span>
            </div>
            <div className="resultado-texto">
              <h4>Promedio general</h4>
              <p>
                {promedio >= 4.5 && "Excelente desempeño"}
                {promedio >= 3.5 && promedio < 4.5 && "Buen desempeño"}
                {promedio >= 2.5 && promedio < 3.5 && "Desempeño regular"}
                {promedio >= 1.5 && promedio < 2.5 && "Desempeño deficiente"}
                {promedio < 1.5 && "Desempeño muy deficiente"}
              </p>
            </div>
          </div>
        </div>
      )}

      {preguntas.length === 0 ? (
        <div className="estado-vacio">
          <i className="bi bi-exclamation-circle"></i>
          <h4>No hay preguntas configuradas</h4>
          <p>Contacta al administrador para que configure las preguntas de evaluación.</p>
        </div>
      ) : (
        <form onSubmit={manejarEnviar} className="formulario-evaluacion">
          {!yaEvaluado && (
            <div className="progreso-evaluacion">
              <span>Preguntas respondidas: {Object.values(respuestas).filter(r => r.calificacion > 0).length} / {preguntas.length}</span>
              <div className="barra-progreso">
                <div 
                  className="barra-progreso-fill" 
                  style={{ width: `${(Object.values(respuestas).filter(r => r.calificacion > 0).length / preguntas.length) * 100}%` }}
                ></div>
              </div>
            </div>
          )}

          {preguntas.map((pregunta, index) => (
            <div className="pregunta-card" key={pregunta.id_pregunta}>
              <div className="pregunta-header">
                <span className="pregunta-badge">Pregunta {index + 1}</span>
                {pregunta.categoria && (
                  <span className="pregunta-categoria-badge">
                    <i className="bi bi-tag"></i> {pregunta.categoria}
                  </span>
                )}
              </div>
              <h4 className="pregunta-texto">{pregunta.descripcion}</h4>

              <div className="calificacion-grupo">
                <label className="calificacion-label">
                  {yaEvaluado ? "Calificación obtenida" : "Selecciona una calificación"}
                </label>
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
                      <span className={`circulo-calif ${respuestas[pregunta.id_pregunta]?.calificacion === valor ? "seleccionado" : ""} ${yaEvaluado ? "deshabilitado" : ""}`}>
                        {valor}
                      </span>
                      <span className="calif-texto">
                        {valor === 1 && "Muy deficiente"}
                        {valor === 2 && "Deficiente"}
                        {valor === 3 && "Regular"}
                        {valor === 4 && "Bueno"}
                        {valor === 5 && "Excelente"}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="campo-observacion">
                <label>Observaciones sobre este criterio <span className="opcional">(opcional)</span></label>
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
            <label>Observaciones generales de la evaluación <span className="opcional">(opcional)</span></label>
            <textarea
              rows={3}
              placeholder="Comentarios generales sobre el instructor..."
              value={observacionesGenerales}
              onChange={(e) => setObservacionesGenerales(e.target.value)}
              disabled={yaEvaluado}
            />
          </div>

          {!yaEvaluado && (
            <div className="acciones-formulario">
              <button type="button" className="btn-cancelar" onClick={() => navigate("/evaluaciones")}>
                Cancelar
              </button>
              <button type="submit" className="btn-enviar" disabled={enviando}>
                <i className="bi bi-send-fill"></i>
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