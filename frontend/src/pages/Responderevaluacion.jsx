import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  obtenerEvaluacion,
  cambiarEstadoEvaluacion,
} from "../services/Evaluacionservice";
import { obtenerAprendiz } from "../services/Aprendizservice";
import { listarInstructoresPorFicha } from "../services/Fichainstructorservice";
import { obtenerInstructor } from "../services/instructorService";
import { listarPreguntasActivas } from "../services/Preguntaservice";
import {
  listarRespuestas,
  crearRespuesta,
  actualizarRespuesta,
} from "../services/Respuestaservice";
import {
  obtenerReporteEvaluacion,
  obtenerReportePorInstructor,
} from "../services/Reporteservice";
import "../styles/Evaluaciones.css";

function claveRespuesta(idPregunta, idInstructor) {
  return `${idPregunta}-${idInstructor}`;
}

function ResponderEvaluacion() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [evaluacion, setEvaluacion] = useState(null);
  const [aprendiz, setAprendiz] = useState(null);
  const [instructores, setInstructores] = useState([]);
  const [preguntas, setPreguntas] = useState([]);
  const [respuestas, setRespuestas] = useState({});
  const [instructorSeleccionado, setInstructorSeleccionado] = useState(null);

  // Respuestas nuevas que aún no se han enviado, por id_pregunta
  const [formulario, setFormulario] = useState({});
  // Preguntas ya respondidas que el usuario decidió editar
  const [editando, setEditando] = useState(new Set());

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [guardando, setGuardando] = useState(false);

  const [reporteGeneral, setReporteGeneral] = useState(null);
  const [reportesPorInstructor, setReportesPorInstructor] = useState({});

  const cargarTodo = async () => {
    try {
      setCargando(true);
      setError("");

      const evaluacionData = await obtenerEvaluacion(id);
      setEvaluacion(evaluacionData);

      const aprendizData = await obtenerAprendiz(evaluacionData.id_aprendiz);
      setAprendiz(aprendizData);

      const relaciones = await listarInstructoresPorFicha(
        aprendizData.id_ficha
      );

      const instructoresData = await Promise.all(
        relaciones.map((rel) => obtenerInstructor(rel.id_instructor))
      );
      setInstructores(instructoresData);

      const preguntasData = await listarPreguntasActivas();
      setPreguntas(preguntasData);

      const todasRespuestas = await listarRespuestas();
      const respuestasEvaluacion = todasRespuestas.filter(
        (r) => r.id_evaluacion === evaluacionData.id_evaluacion
      );

      const mapaRespuestas = {};
      respuestasEvaluacion.forEach((r) => {
        mapaRespuestas[claveRespuesta(r.id_pregunta, r.id_instructor)] = r;
      });
      setRespuestas(mapaRespuestas);

      setInstructorSeleccionado(
        (actual) => actual ?? instructoresData[0]?.id_instructor ?? null
      );

      if (evaluacionData.estado === "Evaluado") {
        const reporte = await obtenerReporteEvaluacion(
          evaluacionData.id_evaluacion
        );
        setReporteGeneral(reporte);

        const reportesMap = {};
        await Promise.all(
          instructoresData.map(async (inst) => {
            reportesMap[inst.id_instructor] =
              await obtenerReportePorInstructor(
                evaluacionData.id_evaluacion,
                inst.id_instructor
              );
          })
        );
        setReportesPorInstructor(reportesMap);
      }
    } catch (err) {
      console.error(err);
      setError("No se pudo cargar la información de la evaluación.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarTodo();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const cambiarInstructor = (idInstructor) => {
    setInstructorSeleccionado(idInstructor);
    setFormulario({});
    setEditando(new Set());
    setError("");
    setMensaje("");
  };

  const manejarCambioCampo = (idPregunta, campo, valor) => {
    setFormulario((prev) => ({
      ...prev,
      [idPregunta]: {
        ...prev[idPregunta],
        [campo]: valor,
      },
    }));
  };

  const iniciarEdicion = (pregunta, respuestaExistente) => {
    setFormulario((prev) => ({
      ...prev,
      [pregunta.id_pregunta]: {
        respuesta: String(respuestaExistente.respuesta),
        comentario: respuestaExistente.comentario || "",
      },
    }));
    setEditando((prev) => new Set(prev).add(pregunta.id_pregunta));
    setMensaje("");
    setError("");
  };

  const cancelarEdicion = (idPregunta) => {
    setEditando((prev) => {
      const copia = new Set(prev);
      copia.delete(idPregunta);
      return copia;
    });
    setFormulario((prev) => {
      const copia = { ...prev };
      delete copia[idPregunta];
      return copia;
    });
  };

  const respuestasDelInstructor = (idInstructor) =>
    preguntas.map(
      (p) => respuestas[claveRespuesta(p.id_pregunta, idInstructor)]
    );

  const instructorCompleto = (idInstructor) =>
    preguntas.length > 0 &&
    respuestasDelInstructor(idInstructor).every((r) => r !== undefined);

  const evaluacionCompleta =
    instructores.length > 0 &&
    instructores.every((inst) => instructorCompleto(inst.id_instructor));

  const preguntasNuevas = preguntas.filter(
    (p) => !respuestas[claveRespuesta(p.id_pregunta, instructorSeleccionado)]
  );

  // Paso 8/10: guarda las respuestas nuevas (no editadas) de las
  // preguntas obligatorias que aún no tienen respuesta.
  const manejarGuardarNuevas = async (e) => {
    e.preventDefault();
    setError("");
    setMensaje("");

    const sinResponder = preguntasNuevas.filter((p) => {
      const valor = formulario[p.id_pregunta]?.respuesta;
      return valor === undefined || valor === "";
    });

    if (sinResponder.length > 0) {
      setError(
        "Debes responder todas las preguntas obligatorias antes de guardar."
      );
      return;
    }

    try {
      setGuardando(true);

      for (const pregunta of preguntasNuevas) {
        const valor = formulario[pregunta.id_pregunta];

        await crearRespuesta({
          respuesta: valor.respuesta === "true",
          comentario: valor.comentario?.trim() || null,
          id_evaluacion: evaluacion.id_evaluacion,
          id_pregunta: pregunta.id_pregunta,
          id_instructor: instructorSeleccionado,
        });
      }

      setMensaje("Respuestas guardadas correctamente.");
      setFormulario({});
      await cargarTodo();
    } catch (err) {
      console.error("Error al guardar respuestas:", err);
      const detalle = err.response?.data?.detail;
      setError(
        typeof detalle === "string"
          ? detalle
          : "No se pudieron guardar las respuestas."
      );
    } finally {
      setGuardando(false);
    }
  };

  // Actualiza una respuesta puntual que ya existía (modo edición).
  const manejarGuardarEdicion = async (respuestaExistente) => {
    setError("");
    setMensaje("");

    const idPregunta = respuestaExistente.id_pregunta;
    const valor = formulario[idPregunta];

    if (!valor || valor.respuesta === undefined || valor.respuesta === "") {
      setError("Selecciona una respuesta antes de guardar el cambio.");
      return;
    }

    try {
      setGuardando(true);

      await actualizarRespuesta(respuestaExistente.id_respuesta, {
        respuesta: valor.respuesta === "true",
        comentario: valor.comentario?.trim() || null,
      });

      setMensaje("Respuesta actualizada correctamente.");
      cancelarEdicion(idPregunta);
      await cargarTodo();
    } catch (err) {
      console.error("Error al actualizar respuesta:", err);
      const detalle = err.response?.data?.detail;
      setError(
        typeof detalle === "string"
          ? detalle
          : "No se pudo actualizar la respuesta."
      );
    } finally {
      setGuardando(false);
    }
  };

  // Paso 9: cambia el estado de la evaluación a "Evaluado".
  const manejarFinalizar = async () => {
    setError("");
    setMensaje("");

    if (!evaluacionCompleta) {
      setError(
        "Debes responder todas las preguntas de todos los instructores antes de enviar la evaluación."
      );
      return;
    }

    if (
      !window.confirm(
        "¿Confirmas enviar la evaluación? Después de enviarla no podrás modificar las respuestas."
      )
    ) {
      return;
    }

    try {
      setGuardando(true);
      await cambiarEstadoEvaluacion(evaluacion.id_evaluacion, "Evaluado");
      setMensaje("Evaluación enviada correctamente.");
      await cargarTodo();
    } catch (err) {
      console.error("Error al finalizar evaluación:", err);
      const detalle = err.response?.data?.detail;
      setError(
        typeof detalle === "string"
          ? detalle
          : "No se pudo enviar la evaluación."
      );
    } finally {
      setGuardando(false);
    }
  };

  if (cargando) {
    return (
      <div className="container-fluid page-content-eval py-4">
        <p className="text-muted">Cargando evaluación...</p>
      </div>
    );
  }

  if (error && !evaluacion) {
    return (
      <div className="container-fluid page-content-eval py-4">
        <p className="text-danger">{error}</p>
      </div>
    );
  }

  if (!evaluacion) {
    return null;
  }

  const esEvaluada = evaluacion.estado === "Evaluado";

  return (
    <div className="container-fluid page-content-eval py-4">
      <button
        className="btn btn-link text-decoration-none ps-0 mb-2"
        onClick={() => navigate("/evaluaciones")}
      >
        <i className="bi bi-arrow-left"></i> Volver a evaluaciones
      </button>

      <div className="evaluation-header">
        <div>
          <h2>
            <i className="bi bi-clipboard-check"></i> Evaluación #{evaluacion.id_evaluacion}
          </h2>
          <p>
            Diligencie la siguiente evaluación de acuerdo con el desarrollo de la
            formación recibida.
          </p>
        </div>

        <span
          className={`badge ${
            esEvaluada ? "badge-evaluado" : "badge-pendiente"
          } px-3 py-2`}
        >
          {evaluacion.estado}
        </span>
      </div>

      <div className="card instructor-card shadow-sm">
        <div className="row align-items-center">
          <div className="col-md-2 text-center">
            <i
              className="bi bi-person-circle"
              style={{ fontSize: "90px", color: "#198754" }}
            ></i>
          </div>
          <div className="col-md-10">
            <div className="row">
              <div className="col-md-6">
                <label>Aprendiz</label>
                <h5>{aprendiz ? `${aprendiz.nombre} ${aprendiz.apellido}` : "-"}</h5>
              </div>
              <div className="col-md-6">
                <label>Estado</label>
                <h5>{evaluacion.estado}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>

      {mensaje && (
        <div className="alert alert-success">
          <i className="bi bi-check-circle-fill me-1"></i>
          {mensaje}
        </div>
      )}
      {error && (
        <div className="alert alert-danger">
          <i className="bi bi-exclamation-triangle-fill me-1"></i>
          {error}
        </div>
      )}

      {instructores.length === 0 && (
        <div className="alert alert-info">
          Esta ficha no tiene instructores asignados.
        </div>
      )}

      {esEvaluada && (
        <div className="evaluation-section">
          <h4>
            <i className="bi bi-bar-chart-fill"></i> Resultado
          </h4>
          <p className="mb-3">
            Puntaje general:{" "}
            <strong className="text-success fs-5">
              {reporteGeneral ? `${reporteGeneral.reporte.toFixed(1)}%` : "-"}
            </strong>
          </p>

          <div className="card shadow-sm">
            <div className="card-body">
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead>
                    <tr>
                      <th>Instructor</th>
                      <th>Competencia</th>
                      <th>Puntaje</th>
                    </tr>
                  </thead>
                  <tbody>
                    {instructores.map((inst) => (
                      <tr key={inst.id_instructor}>
                        <td>
                          {inst.nombre} {inst.apellido}
                        </td>
                        <td>{inst.competencia}</td>
                        <td>
                          {reportesPorInstructor[inst.id_instructor]
                            ? `${reportesPorInstructor[
                                inst.id_instructor
                              ].reporte.toFixed(1)}%`
                            : "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {!esEvaluada && instructores.length > 0 && (
        <div className="evaluation-section">
          <h4>
            <i className="bi bi-people-fill"></i> Instructores a evaluar
          </h4>

          <div className="d-flex flex-wrap gap-2 mb-4">
            {instructores.map((inst) => (
              <button
                key={inst.id_instructor}
                className={`btn instructor-tab ${
                  inst.id_instructor === instructorSeleccionado
                    ? "instructor-tab activo"
                    : "btn-outline-secondary"
                }`}
                onClick={() => cambiarInstructor(inst.id_instructor)}
                disabled={inst.id_instructor === instructorSeleccionado}
              >
                {inst.nombre} {inst.apellido}{" "}
                {instructorCompleto(inst.id_instructor) ? (
                  <i className="bi bi-check-circle-fill ms-1"></i>
                ) : (
                  <span className="ms-1">(pendiente)</span>
                )}
              </button>
            ))}
          </div>

          {instructorSeleccionado && (
            <>
              <h4>
                <i className="bi bi-journal-bookmark-fill"></i> Preguntas
              </h4>

              {preguntas.length === 0 && (
                <p className="text-muted">No hay preguntas activas configuradas.</p>
              )}

              <form onSubmit={manejarGuardarNuevas}>
                {preguntas.map((pregunta) => {
                  const existente =
                    respuestas[
                      claveRespuesta(
                        pregunta.id_pregunta,
                        instructorSeleccionado
                      )
                    ];
                  const enEdicion = editando.has(pregunta.id_pregunta);
                  const valorFormulario = formulario[pregunta.id_pregunta];

                  return (
                    <div className="question-card" key={pregunta.id_pregunta}>
                      <p className="pregunta-texto">
                        {pregunta.orden}. {pregunta.descripcion}
                      </p>

                      {existente && !enEdicion && (
                        <div className="d-flex align-items-center flex-wrap gap-3">
                          <p className="mb-0">
                            Respuesta:{" "}
                            <strong
                              className={
                                existente.respuesta ? "text-success" : "text-danger"
                              }
                            >
                              {existente.respuesta ? "Cumple" : "No cumple"}
                            </strong>
                            {existente.comentario
                              ? ` — "${existente.comentario}"`
                              : ""}
                          </p>
                          <button
                            type="button"
                            className="btn btn-outline-secondary btn-sm"
                            onClick={() => iniciarEdicion(pregunta, existente)}
                          >
                            <i className="bi bi-pencil"></i> Editar
                          </button>
                        </div>
                      )}

                      {(!existente || enEdicion) && (
                        <div>
                          <div className="rating-group mb-3">
                            <div
                              className={`rating-card cumple ${
                                valorFormulario?.respuesta === "true"
                                  ? "seleccionada cumple"
                                  : ""
                              }`}
                              onClick={() =>
                                manejarCambioCampo(
                                  pregunta.id_pregunta,
                                  "respuesta",
                                  "true"
                                )
                              }
                            >
                              <i className="bi bi-check-circle"></i>
                              <span>Cumple</span>
                            </div>
                            <div
                              className={`rating-card no-cumple ${
                                valorFormulario?.respuesta === "false"
                                  ? "seleccionada no-cumple"
                                  : ""
                              }`}
                              onClick={() =>
                                manejarCambioCampo(
                                  pregunta.id_pregunta,
                                  "respuesta",
                                  "false"
                                )
                              }
                            >
                              <i className="bi bi-x-circle"></i>
                              <span>No cumple</span>
                            </div>
                          </div>

                          <div className="mb-2">
                            <label className="form-label small text-muted">
                              Comentario (opcional)
                            </label>
                            <textarea
                              className="form-control"
                              rows={2}
                              value={valorFormulario?.comentario ?? ""}
                              onChange={(e) =>
                                manejarCambioCampo(
                                  pregunta.id_pregunta,
                                  "comentario",
                                  e.target.value
                                )
                              }
                            />
                          </div>

                          {enEdicion && (
                            <div className="d-flex gap-2">
                              <button
                                type="button"
                                className="btn btn-success btn-sm"
                                disabled={guardando}
                                onClick={() =>
                                  manejarGuardarEdicion(existente)
                                }
                              >
                                Guardar cambio
                              </button>
                              <button
                                type="button"
                                className="btn btn-outline-secondary btn-sm"
                                onClick={() =>
                                  cancelarEdicion(pregunta.id_pregunta)
                                }
                              >
                                Cancelar
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}

                {preguntasNuevas.length > 0 && (
                  <button
                    type="submit"
                    className="btn btn-success"
                    disabled={guardando}
                  >
                    <i className="bi bi-save2 me-1"></i>
                    {guardando
                      ? "Guardando..."
                      : "Guardar respuestas de este instructor"}
                  </button>
                )}
              </form>
            </>
          )}

          <div className="text-end mt-4 mb-5">
            <button
              className="btn btn-success btn-lg btn-success-eval"
              onClick={manejarFinalizar}
              disabled={guardando}
            >
              <i className="bi bi-send-fill"></i>{" "}
              {guardando ? "Enviando..." : "Enviar evaluación"}
            </button>
            {!evaluacionCompleta && (
              <p className="mt-2 text-muted">
                <em>
                  Debes responder todas las preguntas de todos los instructores
                  para poder enviar la evaluación.
                </em>
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ResponderEvaluacion;