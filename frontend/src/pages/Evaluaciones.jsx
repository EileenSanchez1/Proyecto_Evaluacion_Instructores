import { useEffect, useState, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  listarInstructoresPorFichaYPeriodo,
  listarFichasPorInstructor,
} from "../services/Fichainstructorservice";
import { listarInstructores, obtenerInstructor } from "../services/instructorService";
import { iniciarEvaluacion, listarEvaluaciones } from "../services/Evaluacionservice";
import { listarPreguntasActivas } from "../services/Preguntaservice";
import { listarFichas } from "../services/FichaServices";
import {
  obtenerUsuarioSesion,
  esAdmin,
  esInstructor,
} from "../utils/sesion";
import {
  historialEvaluaciones,
  miPromedioInstructor,
  reportePreguntasInstructor,
  misEvaluacionesInstructor,
} from "../services/Reporteservice";
import "../styles/Evaluaciones.css";
import "../styles/Home.css";

function Evaluaciones() {
  const navigate = useNavigate();

  const [usuario] = useState(() => obtenerUsuarioSesion());
  const esAdminUser = useMemo(() => esAdmin(), []);
  const esInstructorUser = useMemo(() => esInstructor(), []);

  const [instructores, setInstructores] = useState([]);
  const [evaluaciones, setEvaluaciones] = useState([]);
  const [preguntas, setPreguntas] = useState([]);
  const [historial, setHistorial] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  // Instructor view
  const [fichasInstructor, setFichasInstructor] = useState([]);
  const [reporteInst, setReporteInst] = useState(null);
  const [historialInst, setHistorialInst] = useState([]);

  useEffect(() => {
    let cancelado = false;

    const cargarDatos = async () => {
      try {
        if (cancelado) return;
        setCargando(true);
        setError("");

        if (esAdminUser) {
          const hist = await historialEvaluaciones();
          if (!cancelado) setHistorial(hist || []);
        } else if (esInstructorUser) {
          let idInstructor = usuario?.id_instructor;
          if (!idInstructor) {
            try {
              const todos = await listarInstructores().catch(() => []);
              const yo = (todos || []).find(
                (i) =>
                  (i.correo || "").toLowerCase() ===
                  (usuario?.correo || "").toLowerCase()
              );
              if (yo?.id_instructor) {
                idInstructor = yo.id_instructor;
                localStorage.setItem(
                  "usuario",
                  JSON.stringify({ ...usuario, id_instructor: idInstructor })
                );
              }
            } catch {
              /* ignore */
            }
          }
          if (!idInstructor) {
            setError(
              "No se encontró el identificador de instructor. Vuelve a iniciar sesión como instructor."
            );
            setCargando(false);
            return;
          }

          const cargarReporte = async () => {
            try {
              return await miPromedioInstructor(idInstructor);
            } catch {
              try {
                return await reportePreguntasInstructor(idInstructor, {});
              } catch {
                return null;
              }
            }
          };

          const [asignaciones, reporte, todasFichas, hist] = await Promise.all([
            listarFichasPorInstructor(idInstructor).catch(() => []),
            cargarReporte(),
            listarFichas().catch(() => []),
            misEvaluacionesInstructor(idInstructor).catch(() => []),
          ]);

          const mapa = Object.fromEntries(
            (todasFichas || []).map((f) => [f.id_ficha, f])
          );

          let fichas =
            reporte?.fichas_asignadas?.length > 0
              ? reporte.fichas_asignadas
              : (asignaciones || []).map((a) => {
                  const f = mapa[a.id_ficha];
                  return {
                    ...a,
                    numero_ficha: f?.numero_ficha,
                    programa: f?.programa,
                  };
                });

          if (!cancelado) {
            setFichasInstructor(fichas);
            setReporteInst(reporte);
            setHistorialInst(hist || []);
          }
        } else {
          // Aprendiz
          const idFicha = usuario?.id_ficha;
          const idPeriodo = usuario?.id_periodo;

          if (!idFicha) {
            setError(
              "No tienes una ficha de formación asignada. Contacta al coordinador."
            );
            setCargando(false);
            return;
          }

          const [fichaInstructores, evals, p] = await Promise.all([
            listarInstructoresPorFichaYPeriodo(idFicha, idPeriodo || 1),
            listarEvaluaciones(),
            listarPreguntasActivas(),
          ]);

          const instructoresCompletos = await Promise.all(
            (fichaInstructores || []).map(async (fi) => {
              try {
                const inst = await obtenerInstructor(fi.id_instructor);
                return {
                  ...inst,
                  id_ficha_instructor: fi.id_ficha_instructor || fi.id,
                };
              } catch {
                return null;
              }
            })
          );

          if (!cancelado) {
            setInstructores(instructoresCompletos.filter(Boolean));
            setEvaluaciones(evals || []);
            setPreguntas(p || []);
          }
        }
      } catch (err) {
        console.error(err);
        if (!cancelado) setError("Error al cargar las evaluaciones.");
      } finally {
        if (!cancelado) setCargando(false);
      }
    };

    cargarDatos();
    return () => {
      cancelado = true;
    };
  }, [esAdminUser, esInstructorUser, usuario]);

  const obtenerEstadoInstructor = (idInstructor) => {
    const ev = evaluaciones.find(
      (e) =>
        e.id_instructor === idInstructor &&
        e.id_aprendiz === usuario?.id_aprendiz
    );
    return {
      estado: ev?.estado || "Pendiente",
      id_evaluacion: ev?.id_evaluacion,
    };
  };

  const manejarEvaluar = async (idInstructor) => {
    try {
      const idPeriodo = usuario?.id_periodo || 1;
      const ev = await iniciarEvaluacion(
        usuario.id_aprendiz,
        idInstructor,
        idPeriodo
      );
      navigate(`/evaluaciones/responder/${ev.id_evaluacion}`);
    } catch (err) {
      setError(
        err.response?.data?.detail || "No se pudo iniciar la evaluación."
      );
    }
  };

  const manejarVerResultado = (idEvaluacion) => {
    navigate(`/evaluaciones/${idEvaluacion}`);
  };

  if (cargando) {
    return (
      <div className="pagina-evaluaciones">
        <div className="cargando-centrado">
          <div className="spinner"></div>
          <p>Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pagina-evaluaciones">
      <div className="encabezado-evaluacion">
        <div>
          <h2>
            {esAdminUser
              ? "Historial de Evaluaciones"
              : esInstructorUser
              ? "Mis evaluaciones recibidas"
              : "Evaluación de Instructores"}
          </h2>
          <p>
            {esAdminUser
              ? "Consulta el historial completo de evaluaciones del sistema"
              : esInstructorUser
              ? "Resumen de fichas asignadas y evaluaciones que has recibido (anónimas)"
              : "Evalúa a los instructores asignados a tu ficha de formación"}
          </p>
        </div>
      </div>

      {error && (
        <div
          className="alerta-error"
          style={{
            background: "#fee2e2",
            color: "#991b1b",
            padding: 12,
            borderRadius: 8,
            marginBottom: 16,
          }}
        >
          {error}
        </div>
      )}

      {/* ── ADMIN ── */}
      {esAdminUser && (
        <div className="tabla-container">
          {historial.length === 0 ? (
            <p style={{ color: "#6b7280" }}>No hay evaluaciones registradas.</p>
          ) : (
            <table className="tabla-evaluaciones">
              <thead>
                <tr>
                  <th>Ficha</th>
                  <th>Instructor</th>
                  <th>Periodo</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {historial.map((h, i) => (
                  <tr key={h.id_evaluacion || i}>
                    <td>{h.ficha}</td>
                    <td>{h.instructor}</td>
                    <td>{h.periodo}</td>
                    <td>
                      <span
                        className={`badge-estado ${
                          h.estado === "Evaluado" ? "evaluado" : "pendiente"
                        }`}
                      >
                        {h.estado}
                      </span>
                    </td>
                    <td>{h.fecha || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* ── INSTRUCTOR ── */}
      {esInstructorUser && (
        <>
          <div className="home-stats" style={{ marginBottom: 24 }}>
            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-verde">
                <i className="bi bi-card-list"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{fichasInstructor.length}</span>
                <span className="home-stat-label">Fichas asignadas</span>
              </div>
            </div>
            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-naranja">
                <i className="bi bi-star-fill"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">
                  {reporteInst != null && reporteInst.promedio_general != null
                    ? Number(reporteInst.promedio_general).toFixed(2)
                    : "—"}
                </span>
                <span className="home-stat-label">Promedio general (1–5)</span>
              </div>
            </div>
            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-azul">
                <i className="bi bi-graph-up"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">
                  {reporteInst != null && reporteInst.porcentaje_general != null
                    ? `${Number(reporteInst.porcentaje_general).toFixed(1)}%`
                    : "—"}
                </span>
                <span className="home-stat-label">Desempeño global</span>
              </div>
            </div>
          </div>

          <div
            style={{
              background: "#fff",
              borderRadius: 12,
              padding: 20,
              marginBottom: 20,
              boxShadow: "0 1px 3px rgba(0,0,0,.08)",
            }}
          >
            <h3 style={{ marginTop: 0 }}>
              <i className="bi bi-card-list"></i> Fichas donde estás asignado
            </h3>
            {fichasInstructor.length === 0 ? (
              <p style={{ color: "#6b7280" }}>
                No tienes fichas asignadas todavía. Cuando el administrador te
                asigne a una ficha y periodo, aparecerán aquí.
              </p>
            ) : (
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {fichasInstructor.map((f, idx) => (
                  <li
                    key={f.id_ficha_instructor || f.id || idx}
                    style={{
                      padding: "12px 0",
                      borderBottom: "1px solid #f3f4f6",
                      display: "flex",
                      justifyContent: "space-between",
                      flexWrap: "wrap",
                      gap: 8,
                    }}
                  >
                    <span>
                      <strong>Ficha {f.numero_ficha || f.id_ficha}</strong>
                      {f.programa ? ` — ${f.programa}` : ""}
                    </span>
                    {f.periodo && (
                      <span style={{ color: "#065f46", fontWeight: 600 }}>
                        {f.periodo}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div
            style={{
              background: "#fff",
              borderRadius: 12,
              padding: 20,
              boxShadow: "0 1px 3px rgba(0,0,0,.08)",
            }}
          >
            <h3 style={{ marginTop: 0 }}>
              <i className="bi bi-clipboard-check"></i> Evaluaciones recibidas
            </h3>
            <p style={{ color: "#6b7280", fontSize: "0.95rem" }}>
              Listado anónimo: ves ficha, programa, fecha y estado. No se muestra quién evaluó.
            </p>
            {historialInst.length === 0 ? (
              <p style={{ color: "#9ca3af", marginTop: 12 }}>
                Aún no has recibido evaluaciones. Cuando los aprendices de tus fichas te evalúen, aparecerán aquí.
              </p>
            ) : (
              <div className="table-responsive" style={{ marginTop: 12 }}>
                <table className="table table-hover" style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ textAlign: "left", borderBottom: "2px solid #e5e7eb", color: "#6b7280", fontSize: "0.85rem" }}>
                      <th style={{ padding: "10px 8px" }}>Fecha</th>
                      <th style={{ padding: "10px 8px" }}>Ficha</th>
                      <th style={{ padding: "10px 8px" }}>Programa</th>
                      <th style={{ padding: "10px 8px" }}>Periodo</th>
                      <th style={{ padding: "10px 8px" }}>Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historialInst.map((h) => (
                      <tr key={h.id_evaluacion} style={{ borderBottom: "1px solid #f3f4f6" }}>
                        <td style={{ padding: "12px 8px" }}>
                          {h.fecha
                            ? new Date(h.fecha).toLocaleDateString("es-CO", {
                                year: "numeric",
                                month: "short",
                                day: "numeric",
                              })
                            : "—"}
                        </td>
                        <td style={{ padding: "12px 8px" }}>
                          <strong>{h.ficha ?? "—"}</strong>
                        </td>
                        <td style={{ padding: "12px 8px" }}>{h.programa || "—"}</td>
                        <td style={{ padding: "12px 8px" }}>{h.periodo || "—"}</td>
                        <td style={{ padding: "12px 8px" }}>
                          <span
                            style={{
                              display: "inline-block",
                              padding: "4px 10px",
                              borderRadius: 999,
                              fontSize: "0.8rem",
                              fontWeight: 600,
                              background:
                                h.estado === "Evaluado" ? "#d1fae5" : "#fef3c7",
                              color:
                                h.estado === "Evaluado" ? "#065f46" : "#92400e",
                            }}
                          >
                            {h.estado || "—"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <Link
              to="/mi-promedio"
              className="btn-evaluar"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                textDecoration: "none",
                marginTop: 16,
              }}
            >
              <i className="bi bi-graph-up-arrow"></i> Ir a Mi promedio
            </Link>
          </div>
        </>
      )}

      {/* ── APRENDIZ ── */}
      {!esAdminUser && !esInstructorUser && (
        <>
          {instructores.length === 0 ? (
            <div className="sin-datos">
              <i className="bi bi-inbox"></i>
              <h4>No tienes instructores asignados</h4>
              <p>
                Contacta al coordinador para que te asigne instructores a tu
                ficha.
              </p>
            </div>
          ) : (
            <div className="grid-evaluaciones">
              {instructores.map((inst) => {
                const { estado, id_evaluacion } = obtenerEstadoInstructor(
                  inst.id_instructor
                );
                const yaEvaluado = estado === "Evaluado";

                return (
                  <div className="evaluacion-card" key={inst.id_instructor}>
                    <div className="card-header">
                      <div className="card-foto-wrap">
                        {inst.foto ? (
                          <img
                            className="card-foto"
                            src={`http://localhost:8000${inst.foto}`}
                            alt={inst.nombre}
                          />
                        ) : (
                          <div className="card-foto-placeholder">
                            <i className="bi bi-person-fill"></i>
                          </div>
                        )}
                      </div>
                      <div className="card-info">
                        <h4>
                          {inst.nombre} {inst.apellido}
                        </h4>
                        <p className="card-email">
                          <i className="bi bi-envelope"></i> {inst.correo}
                        </p>
                        {inst.telefono && (
                          <p className="card-tel">
                            <i className="bi bi-telephone"></i> {inst.telefono}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="card-competencias">
                      {(inst.competencias || []).slice(0, 3).map((c) => (
                        <span
                          className="badge-competencia"
                          key={c.id_competencia}
                        >
                          {c.nombre}
                        </span>
                      ))}
                      {(inst.competencias || []).length > 3 && (
                        <span className="badge-competencia mas">
                          +{(inst.competencias || []).length - 3}
                        </span>
                      )}
                    </div>

                    <div className="card-footer">
                      <span
                        className={`badge-estado ${
                          yaEvaluado ? "evaluado" : "pendiente"
                        }`}
                      >
                        {yaEvaluado ? "Evaluado" : "Pendiente"}
                      </span>
                      <button
                        className={yaEvaluado ? "btn-ver" : "btn-evaluar"}
                        onClick={() =>
                          yaEvaluado
                            ? manejarVerResultado(id_evaluacion)
                            : manejarEvaluar(inst.id_instructor)
                        }
                      >
                        <i
                          className={`bi ${
                            yaEvaluado ? "bi-eye" : "bi-pencil-square"
                          }`}
                        ></i>
                        {yaEvaluado ? "Ver resultado" : "Evaluar"}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Evaluaciones;
