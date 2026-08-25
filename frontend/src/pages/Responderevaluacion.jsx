import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  obtenerEvaluacion,
  cambiarEstadoEvaluacion,
} from "../services/evaluacionService";
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
    return <p>Cargando evaluación...</p>;
  }

  if (error && !evaluacion) {
    return <p style={{ color: "red" }}>{error}</p>;
  }

  if (!evaluacion) {
    return null;
  }

  const esEvaluada = evaluacion.estado === "Evaluado";

  return (
    <div>
      <button onClick={() => navigate("/evaluaciones")}>
        &larr; Volver a evaluaciones
      </button>

      <h1>Evaluación #{evaluacion.id_evaluacion}</h1>

      <p>
        <strong>Aprendiz:</strong>{" "}
        {aprendiz ? `${aprendiz.nombre} ${aprendiz.apellido}` : "-"}
        <br />
        <strong>Estado:</strong>{" "}
        <span
          style={{
            color: esEvaluada ? "green" : "#b8860b",
            fontWeight: "bold",
          }}
        >
          {evaluacion.estado}
        </span>
      </p>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {instructores.length === 0 && (
        <p>Esta ficha no tiene instructores asignados.</p>
      )}

      {esEvaluada && (
        <div>
          <h2>Resultado</h2>
          <p>
            <strong>Puntaje general:</strong>{" "}
            {reporteGeneral ? `${reporteGeneral.reporte.toFixed(1)}%` : "-"}
          </p>

          <table>
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
      )}

      {!esEvaluada && instructores.length > 0 && (
        <div>
          <h2>Instructores a evaluar</h2>

          <div>
            {instructores.map((inst) => (
              <button
                key={inst.id_instructor}
                onClick={() => cambiarInstructor(inst.id_instructor)}
                disabled={inst.id_instructor === instructorSeleccionado}
                style={{ marginRight: "8px", marginBottom: "8px" }}
              >
                {inst.nombre} {inst.apellido}{" "}
                {instructorCompleto(inst.id_instructor) ? "✔" : "(pendiente)"}
              </button>
            ))}
          </div>

          {instructorSeleccionado && (
            <>
              <h3>Preguntas</h3>

              {preguntas.length === 0 && (
                <p>No hay preguntas activas configuradas.</p>
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
                    <div
                      key={pregunta.id_pregunta}
                      style={{
                        border: "1px solid var(--border)",
                        padding: "12px",
                        marginBottom: "10px",
                      }}
                    >
                      <p>
                        <strong>{pregunta.orden}.</strong>{" "}
                        {pregunta.descripcion}
                      </p>

                      {existente && !enEdicion && (
                        <div>
                          <p>
                            Respuesta:{" "}
                            <strong>
                              {existente.respuesta ? "Cumple" : "No cumple"}
                            </strong>
                            {existente.comentario
                              ? ` — "${existente.comentario}"`
                              : ""}
                          </p>
                          <button
                            type="button"
                            onClick={() => iniciarEdicion(pregunta, existente)}
                          >
                            Editar
                          </button>
                        </div>
                      )}

                      {(!existente || enEdicion) && (
                        <div>
                          <label>
                            Respuesta *{" "}
                            <select
                              value={valorFormulario?.respuesta ?? ""}
                              onChange={(e) =>
                                manejarCambioCampo(
                                  pregunta.id_pregunta,
                                  "respuesta",
                                  e.target.value
                                )
                              }
                              required
                            >
                              <option value="">Seleccione...</option>
                              <option value="true">Cumple</option>
                              <option value="false">No cumple</option>
                            </select>
                          </label>

                          <div>
                            <label>
                              Comentario (opcional)
                              <br />
                              <textarea
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
                            </label>
                          </div>

                          {enEdicion && (
                            <div>
                              <button
                                type="button"
                                disabled={guardando}
                                onClick={() =>
                                  manejarGuardarEdicion(existente)
                                }
                              >
                                Guardar cambio
                              </button>
                              <button
                                type="button"
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
                  <button type="submit" disabled={guardando}>
                    {guardando
                      ? "Guardando..."
                      : "Guardar respuestas de este instructor"}
                  </button>
                )}
              </form>
            </>
          )}

          <hr />

          <button onClick={manejarFinalizar} disabled={guardando}>
            {guardando ? "Enviando..." : "Enviar evaluación"}
          </button>
          {!evaluacionCompleta && (
            <p>
              <em>
                Debes responder todas las preguntas de todos los instructores
                para poder enviar la evaluación.
              </em>
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default ResponderEvaluacion;