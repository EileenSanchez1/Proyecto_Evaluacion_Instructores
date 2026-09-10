import { useEffect, useState, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  obtenerUsuarioSesion,
  esAdmin,
  esAdminOCoordinador,
  esInstructor,
} from "../utils/sesion";
import { listarInstructoresPorFichaYPeriodo, listarFichasPorInstructor } from "../services/Fichainstructorservice";
import { listarEvaluaciones } from "../services/Evaluacionservice";
import { listarInstructores, obtenerInstructor } from "../services/instructorService";
import { listarAprendices } from "../services/Aprendizservice";
import { listarFichas } from "../services/FichaServices";
import { historialEvaluaciones, miPromedioInstructor, reportePreguntasInstructor } from "../services/Reporteservice";
import { listarPreguntasActivas } from "../services/Preguntaservice";
import "../styles/Home.css";

function Home() {
  const navigate = useNavigate();
  const [usuario] = useState(() => obtenerUsuarioSesion());
  const esAdminUser = useMemo(() => esAdmin(), []);
  const esAdminCoord = useMemo(() => esAdminOCoordinador(), []);
  const esInstructorUser = useMemo(() => esInstructor(), []);

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  // Aprendiz
  const [instructoresAsignados, setInstructoresAsignados] = useState([]);
  const [misEvaluaciones, setMisEvaluaciones] = useState([]);
  const [preguntasActivas, setPreguntasActivas] = useState([]);

  // Admin
  const [totalInstructores, setTotalInstructores] = useState(0);
  const [totalAprendices, setTotalAprendices] = useState(0);
  const [totalFichas, setTotalFichas] = useState(0);
  const [totalEvaluaciones, setTotalEvaluaciones] = useState(0);
  const [evaluacionesPendientes, setEvaluacionesPendientes] = useState(0);
  const [ultimasEvaluaciones, setUltimasEvaluaciones] = useState([]);

  // Instructor
  const [fichasInstructor, setFichasInstructor] = useState([]);
  const [reporteInstructor, setReporteInstructor] = useState(null);

  useEffect(() => {
    let cancelado = false;

    const cargarDatos = async () => {
      try {
        setCargando(true);
        setError("");

        if (esAdminCoord) {
          const [insts, aprendices, fichas, evals, historial] = await Promise.all([
            listarInstructores().catch(() => []),
            listarAprendices().catch(() => []),
            listarFichas().catch(() => []),
            listarEvaluaciones().catch(() => []),
            historialEvaluaciones().catch(() => []),
          ]);

          if (!cancelado) {
            setTotalInstructores(insts.length);
            setTotalAprendices(aprendices.length);
            setTotalFichas(fichas.length);
            setTotalEvaluaciones(evals.length);
            setEvaluacionesPendientes(evals.filter((e) => e.estado === "Pendiente").length);
            setUltimasEvaluaciones((historial || []).slice(0, 5));
          }
        } else if (esInstructorUser) {
          let idInstructor = usuario?.id_instructor;
          if (!idInstructor) {
            // Intentar recuperar id_instructor por correo si la sesión es antigua
            try {
              const todos = await listarInstructores().catch(() => []);
              const yo = (todos || []).find(
                (i) => (i.correo || "").toLowerCase() === (usuario?.correo || "").toLowerCase()
              );
              if (yo?.id_instructor) {
                idInstructor = yo.id_instructor;
                const u = { ...usuario, id_instructor: idInstructor };
                localStorage.setItem("usuario", JSON.stringify(u));
              }
            } catch {
              /* ignore */
            }
          }
          if (!idInstructor) {
            setError("No se encontró el identificador de instructor en la sesión. Cierra sesión e inicia de nuevo como instructor.");
            setCargando(false);
            return;
          }

          const [asignaciones, reporte] = await Promise.all([
            listarFichasPorInstructor(idInstructor).catch(() => []),
            (async () => {
              try {
                return await miPromedioInstructor(idInstructor);
              } catch (e1) {
                try {
                  return await reportePreguntasInstructor(idInstructor, {});
                } catch (e2) {
                  console.error("No se pudo cargar el promedio del instructor", e1, e2);
                  return null;
                }
              }
            })(),
          ]);

          // Enriquecer fichas si el reporte ya trae detalle
          let fichas = asignaciones || [];
          if (reporte?.fichas_asignadas?.length) {
            fichas = reporte.fichas_asignadas;
          } else if (fichas.length) {
            // Completar número de ficha consultando listado de fichas
            try {
              const todas = await listarFichas().catch(() => []);
              const mapa = Object.fromEntries((todas || []).map((f) => [f.id_ficha, f]));
              fichas = fichas.map((a) => {
                const f = mapa[a.id_ficha];
                return {
                  ...a,
                  numero_ficha: f?.numero_ficha || a.numero_ficha,
                  programa: f?.programa || a.programa,
                };
              });
            } catch {
              /* ignore */
            }
          }

          if (!cancelado) {
            setFichasInstructor(fichas);
            setReporteInstructor(reporte);
          }
        } else {
          // Aprendiz
          const idFicha = usuario?.id_ficha;
          const idPeriodo = usuario?.id_periodo;

          if (!idFicha) {
            setError("No tienes una ficha de formación asignada.");
            setCargando(false);
            return;
          }

          const [fichaInsts, evals, preguntas] = await Promise.all([
            listarInstructoresPorFichaYPeriodo(idFicha, idPeriodo || 1).catch(() => []),
            listarEvaluaciones().catch(() => []),
            listarPreguntasActivas().catch(() => []),
          ]);

          const instructoresCompletos = await Promise.all(
            (fichaInsts || []).map(async (fi) => {
              try {
                return await obtenerInstructor(fi.id_instructor);
              } catch {
                return null;
              }
            })
          );

          const misEvals = (evals || []).filter((e) => e.id_aprendiz === usuario?.id_aprendiz);

          if (!cancelado) {
            setInstructoresAsignados(instructoresCompletos.filter(Boolean));
            setMisEvaluaciones(misEvals);
            setPreguntasActivas(preguntas || []);
          }
        }
      } catch (err) {
        console.error(err);
        if (!cancelado) setError("Error al cargar los datos del inicio.");
      } finally {
        if (!cancelado) setCargando(false);
      }
    };

    cargarDatos();
    return () => {
      cancelado = true;
    };
  }, [esAdminCoord, esInstructorUser, usuario]);

  const evaluacionesRealizadas = misEvaluaciones.filter((e) => e.estado === "Evaluado").length;
  const progresoEvaluacion =
    instructoresAsignados.length > 0
      ? Math.round((evaluacionesRealizadas / instructoresAsignados.length) * 100)
      : 0;

  const instructoresPendientes = instructoresAsignados.filter(
    (inst) =>
      !misEvaluaciones.some(
        (e) => e.id_instructor === inst.id_instructor && e.estado === "Evaluado"
      )
  );

  if (cargando) {
    return (
      <div className="home-page">
        <div className="home-cargando">
          <div className="spinner-home"></div>
          <p>Cargando panel...</p>
        </div>
      </div>
    );
  }

  const subtitulo = esAdminCoord
    ? "Panel de control del sistema de evaluación de instructores SENA"
    : esInstructorUser
    ? "Panel del instructor — consulta tu desempeño y fichas asignadas"
    : "Bienvenido al sistema de evaluación de instructores del SENA";

  return (
    <div className="home-page">
      <div className="home-header">
        <div>
          <h1>¡Hola, {usuario?.nombre || "Usuario"}!</h1>
          <p>{subtitulo}</p>
        </div>
        <div className="home-fecha">
          <i className="bi bi-calendar3"></i>
          {new Date().toLocaleDateString("es-CO", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </div>
      </div>

      {error && <div className="home-alerta home-alerta-error">{error}</div>}

      {/* ═══════════════ INSTRUCTOR ═══════════════ */}
      {esInstructorUser && (
        <>
          <section className="home-banner">
            <div className="home-banner-texto">
              <h2>Tu espacio como instructor</h2>
              <p>
                Revisa las fichas donde estás asignado, el promedio general de tus
                evaluaciones y el detalle por pregunta para saber en qué aspectos
                destacar y en cuáles mejorar.
              </p>
              <div className="home-banner-actions">
                <Link to="/mi-promedio" className="home-banner-btn">
                  <i className="bi bi-graph-up-arrow"></i>
                  <span>Ver mi promedio</span>
                </Link>
                <Link to="/perfil-instructor" className="home-banner-btn home-banner-btn-secondary">
                  <i className="bi bi-person-badge"></i>
                  <span>Mi perfil</span>
                </Link>
              </div>
            </div>
          </section>

          <div className="home-stats">
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
                  {reporteInstructor != null && reporteInstructor.promedio_general != null
                    ? Number(reporteInstructor.promedio_general).toFixed(2)
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
                  {reporteInstructor != null && reporteInstructor.porcentaje_general != null
                    ? `${Number(reporteInstructor.porcentaje_general).toFixed(1)}%`
                    : "—"}
                </span>
                <span className="home-stat-label">Desempeño global</span>
              </div>
            </div>
          </div>

          <div className="home-grid">
            <div className="home-card">
              <div className="home-card-header">
                <h3>
                  <i className="bi bi-journal-bookmark"></i> Fichas donde impartes
                </h3>
              </div>
              <div className="home-card-body">
                {fichasInstructor.length === 0 ? (
                  <div style={{ textAlign: "center", padding: "24px 8px", color: "#6b7280" }}>
                    <i className="bi bi-inbox" style={{ fontSize: 32 }}></i>
                    <p style={{ marginTop: 8 }}>
                      Aún no tienes fichas asignadas. Cuando el administrador te
                      asigne a una ficha y periodo, aparecerán aquí.
                    </p>
                  </div>
                ) : (
                  <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                    {fichasInstructor.map((f, idx) => (
                      <li
                        key={f.id_ficha_instructor || f.id || idx}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          padding: "12px 0",
                          borderBottom: "1px solid #f3f4f6",
                          gap: 12,
                          flexWrap: "wrap",
                        }}
                      >
                        <div>
                          <strong style={{ color: "#1f2937" }}>
                            Ficha {f.numero_ficha || f.id_ficha}
                          </strong>
                          {f.programa && (
                            <div style={{ fontSize: "0.85rem", color: "#6b7280" }}>
                              {f.programa}
                            </div>
                          )}
                        </div>
                        {f.periodo && (
                          <span
                            style={{
                              background: "#ecfdf5",
                              color: "#065f46",
                              padding: "4px 10px",
                              borderRadius: 20,
                              fontSize: "0.8rem",
                              fontWeight: 600,
                            }}
                          >
                            {f.periodo}
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className="home-card">
              <div className="home-card-header">
                <h3>
                  <i className="bi bi-lightning"></i> Accesos rápidos
                </h3>
              </div>
              <div className="home-card-body">
                <div className="home-accesos">
                  <Link to="/mi-promedio" className="home-acceso">
                    <i className="bi bi-graph-up-arrow"></i>
                    <span>Mi promedio por pregunta</span>
                  </Link>
                  <Link to="/perfil-instructor" className="home-acceso">
                    <i className="bi bi-camera"></i>
                    <span>Actualizar foto de perfil</span>
                  </Link>
                  <Link to="/evaluaciones" className="home-acceso">
                    <i className="bi bi-clipboard-data"></i>
                    <span>Resumen de evaluaciones</span>
                  </Link>
                </div>
                {reporteInstructor?.preguntas?.length > 0 && (
                  <p style={{ marginTop: 16, fontSize: "0.9rem", color: "#4b5563" }}>
                    Tienes detalle de {reporteInstructor.preguntas.length} pregunta(s)
                    evaluada(s). Entra a <strong>Mi promedio</strong> para ver alertas
                    de mejora o felicitaciones.
                  </p>
                )}
                {reporteInstructor &&
                  (reporteInstructor.total_respuestas === 0 ||
                    !reporteInstructor.preguntas?.length) && (
                    <p style={{ marginTop: 16, fontSize: "0.9rem", color: "#6b7280" }}>
                      Todavía no has recibido evaluaciones de aprendices. Cuando las
                      haya, el promedio y las alertas se mostrarán aquí.
                    </p>
                  )}
              </div>
            </div>
          </div>
        </>
      )}

      {/* ═══════════════ ADMIN ═══════════════ */}
      {esAdminCoord && (
        <>
          <section className="home-banner">
            <div className="home-banner-texto">
              <h2>Gestión del sistema</h2>
              <p>
                Monitorea el desempeño de los instructores, consulta reportes y
                gestiona el proceso de evaluación académica.
              </p>
            </div>
          </section>

          <div className="home-stats">
            <div className="home-stat-card">
              <i className="bi bi-people"></i>
              <span className="home-stat-num">{totalInstructores}</span>
              <span className="home-stat-label">Instructores registrados</span>
            </div>
            <div className="home-stat-card">
              <i className="bi bi-mortarboard"></i>
              <span className="home-stat-num">{totalAprendices}</span>
              <span className="home-stat-label">Aprendices</span>
            </div>
            <div className="home-stat-card">
              <i className="bi bi-card-text"></i>
              <span className="home-stat-num">{totalFichas}</span>
              <span className="home-stat-label">Fichas</span>
            </div>
            <div className="home-stat-card">
              <i className="bi bi-clipboard-check"></i>
              <span className="home-stat-num">{totalEvaluaciones}</span>
              <span className="home-stat-label">Evaluaciones</span>
            </div>
          </div>

          <div className="home-grid">
            <div className="home-card">
              <div className="home-card-header">
                <h3>
                  <i className="bi bi-clock-history"></i> Últimas evaluaciones
                </h3>
              </div>
              <div className="home-card-body">
                {ultimasEvaluaciones.length === 0 ? (
                  <p style={{ color: "#6b7280" }}>Sin evaluaciones registradas aún.</p>
                ) : (
                  <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                    {ultimasEvaluaciones.map((ev, i) => (
                      <li
                        key={ev.id_evaluacion || i}
                        style={{
                          padding: "10px 0",
                          borderBottom: "1px solid #f3f4f6",
                          fontSize: "0.9rem",
                        }}
                      >
                        <strong>{ev.instructor || `Instructor #${ev.id_instructor}`}</strong>
                        {" · "}
                        Ficha {ev.ficha || "—"}
                        {ev.estado && (
                          <span style={{ marginLeft: 8, color: "#39a900", fontWeight: 600 }}>
                            {ev.estado}
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className="home-card">
              <div className="home-card-header">
                <h3>
                  <i className="bi bi-lightning"></i> Accesos rápidos
                </h3>
              </div>
              <div className="home-card-body">
                <div className="home-accesos">
                  <Link to="/instructores" className="home-acceso">
                    <i className="bi bi-people"></i>
                    <span>Gestionar instructores</span>
                  </Link>
                  <Link to="/fichas" className="home-acceso">
                    <i className="bi bi-card-text"></i>
                    <span>Administrar fichas</span>
                  </Link>
                  <Link to="/preguntas" className="home-acceso">
                    <i className="bi bi-journal-bookmark"></i>
                    <span>Configurar preguntas</span>
                  </Link>
                  <Link to="/reportes" className="home-acceso">
                    <i className="bi bi-bar-chart"></i>
                    <span>Ver reportes</span>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* ═══════════════ APRENDIZ ═══════════════ */}
      {!esAdminCoord && !esInstructorUser && (
        <>
          <section className="home-banner">
            <div className="home-banner-texto">
              <h2>Tu evaluación cuenta</h2>
              <p>
                Evalúa a tus instructores de forma honesta y constructiva. Tus
                comentarios contribuyen a mejorar la calidad de la enseñanza en el
                SENA.
              </p>
            </div>
          </section>

          <div className="home-stats">
            <div className="home-stat-card">
              <i className="bi bi-people"></i>
              <span className="home-stat-num">{instructoresAsignados.length}</span>
              <span className="home-stat-label">Instructores asignados</span>
            </div>
            <div className="home-stat-card">
              <i className="bi bi-check2-circle"></i>
              <span className="home-stat-num">{evaluacionesRealizadas}</span>
              <span className="home-stat-label">Evaluaciones completadas</span>
            </div>
            <div className="home-stat-card">
              <i className="bi bi-hourglass-split"></i>
              <span className="home-stat-num">{instructoresPendientes.length}</span>
              <span className="home-stat-label">Pendientes</span>
            </div>
            <div className="home-stat-card">
              <i className="bi bi-pie-chart"></i>
              <span className="home-stat-num">{progresoEvaluacion}%</span>
              <span className="home-stat-label">Progreso</span>
            </div>
          </div>

          <div className="home-grid">
            <div className="home-card">
              <div className="home-card-header">
                <h3>
                  <i className="bi bi-clipboard-check"></i> Progreso de evaluación
                </h3>
              </div>
              <div className="home-card-body">
                {instructoresAsignados.length === 0 ? (
                  <div style={{ textAlign: "center", color: "#6b7280" }}>
                    <p>No tienes instructores asignados aún</p>
                  </div>
                ) : (
                  <>
                    <p>
                      <span>
                        {evaluacionesRealizadas} de {instructoresAsignados.length}{" "}
                        evaluaciones completadas
                      </span>
                    </p>
                    <div
                      style={{
                        height: 10,
                        background: "#e5e7eb",
                        borderRadius: 5,
                        overflow: "hidden",
                        margin: "12px 0",
                      }}
                    >
                      <div
                        style={{
                          height: "100%",
                          width: `${progresoEvaluacion}%`,
                          background: "#39a900",
                        }}
                      />
                    </div>

                    {instructoresPendientes.length > 0 && (
                      <>
                        <h4>Instructores pendientes por evaluar</h4>
                        <div>
                          <div className="home-pendientes-lista">
                            {instructoresPendientes.slice(0, 4).map((inst) => (
                              <div className="home-pendiente-item" key={inst.id_instructor}>
                                <div className="home-pendiente-foto-placeholder">
                                  <i className="bi bi-person-fill"></i>
                                </div>
                                <div className="home-pendiente-info">
                                  <span className="home-pendiente-nombre">
                                    {inst.nombre} {inst.apellido}
                                  </span>
                                  <span className="home-pendiente-meta">Pendiente de evaluar</span>
                                </div>
                                <button
                                  type="button"
                                  className="home-pendiente-btn"
                                  onClick={() => navigate("/evaluaciones")}
                                >
                                  Evaluar
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                        {instructoresPendientes.length > 4 && (
                          <Link to="/evaluaciones">
                            Ver {instructoresPendientes.length - 4} más →
                          </Link>
                        )}
                      </>
                    )}

                    {instructoresPendientes.length === 0 && (
                      <div style={{ textAlign: "center", color: "#065f46" }}>
                        <i className="bi bi-emoji-smile"></i>
                        <p>Has evaluado a todos tus instructores. Gracias por tu participación.</p>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>

            <div className="home-card">
              <div className="home-card-header">
                <h3>
                  <i className="bi bi-lightning"></i> Accesos rápidos
                </h3>
              </div>
              <div className="home-card-body">
                <div className="home-accesos">
                  <Link to="/evaluaciones" className="home-acceso">
                    <i className="bi bi-clipboard-check"></i>
                    <span>Mis evaluaciones</span>
                  </Link>
                  <Link to="/instructores" className="home-acceso">
                    <i className="bi bi-people"></i>
                    <span>Mis instructores</span>
                  </Link>
                  <Link to="/contacto" className="home-acceso">
                    <i className="bi bi-envelope"></i>
                    <span>Contactar coordinador</span>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Home;
