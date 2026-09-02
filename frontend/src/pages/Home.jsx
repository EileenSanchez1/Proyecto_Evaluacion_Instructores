import { useEffect, useState, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import { obtenerUsuarioSesion, esAdmin, esAdminOCoordinador } from "../utils/sesion";
import { listarInstructoresPorFichaYPeriodo } from "../services/Fichainstructorservice";
import { listarEvaluaciones } from "../services/Evaluacionservice";
import { listarInstructores } from "../services/instructorService";
import { listarAprendices } from "../services/Aprendizservice";
import { listarFichas } from "../services/FichaServices";
import { historialEvaluaciones } from "../services/Reporteservice";
import { listarPreguntasActivas } from "../services/Preguntaservice";
import { obtenerInstructor } from "../services/instructorService";
import "../styles/Home.css";

function Home() {
  const navigate = useNavigate();
  const [usuario] = useState(() => obtenerUsuarioSesion());
  const esAdminUser = useMemo(() => esAdmin(), []);
  const esAdminCoord = useMemo(() => esAdminOCoordinador(), []);

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  // Datos para Aprendiz
  const [instructoresAsignados, setInstructoresAsignados] = useState([]);
  const [misEvaluaciones, setMisEvaluaciones] = useState([]);
  const [preguntasActivas, setPreguntasActivas] = useState([]);

  // Datos para Admin
  const [totalInstructores, setTotalInstructores] = useState(0);
  const [totalAprendices, setTotalAprendices] = useState(0);
  const [totalFichas, setTotalFichas] = useState(0);
  const [totalEvaluaciones, setTotalEvaluaciones] = useState(0);
  const [evaluacionesPendientes, setEvaluacionesPendientes] = useState(0);
  const [ultimasEvaluaciones, setUltimasEvaluaciones] = useState([]);

  useEffect(() => {
    let cancelado = false;

    const cargarDatos = async () => {
      try {
        setCargando(true);
        setError("");

        if (esAdminCoord) {
          // ── ADMIN / COORDINADOR ──
          const [insts, aprendices, fichas, evals, historial] = await Promise.all([
            listarInstructores().catch(() => []),
            listarAprendices().catch(() => []),
            listarFichas().catch(() => []),
            listarEvaluaciones().catch(() => []),
            historialEvaluaciones().catch(() => [])
          ]);

          if (!cancelado) {
            setTotalInstructores(insts.length);
            setTotalAprendices(aprendices.length);
            setTotalFichas(fichas.length);
            setTotalEvaluaciones(evals.length);
            setEvaluacionesPendientes(evals.filter(e => e.estado === "Pendiente").length);
            setUltimasEvaluaciones(historial.slice(0, 5));
          }
        } else {
          // ── APRENDIZ ──
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
            listarPreguntasActivas().catch(() => [])
          ]);

          // Obtener datos completos de instructores
          const instructoresCompletos = await Promise.all(
            fichaInsts.map(async (fi) => {
              try {
                const inst = await obtenerInstructor(fi.id_instructor);
                return inst;
              } catch { return null; }
            })
          );

          const misEvals = evals.filter(
            (e) => e.id_aprendiz === usuario?.id_aprendiz
          );

          if (!cancelado) {
            setInstructoresAsignados(instructoresCompletos.filter(Boolean));
            setMisEvaluaciones(misEvals);
            setPreguntasActivas(preguntas);
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
    return () => { cancelado = true; };
  }, [esAdminCoord, usuario]);

  const evaluacionesRealizadas = misEvaluaciones.filter(e => e.estado === "Evaluado").length;
  const evaluacionesPendientesAprendiz = instructoresAsignados.length - evaluacionesRealizadas;
  const progresoEvaluacion = instructoresAsignados.length > 0
    ? Math.round((evaluacionesRealizadas / instructoresAsignados.length) * 100)
    : 0;

  const instructoresPendientes = instructoresAsignados.filter(inst =>
    !misEvaluaciones.some(e => e.id_instructor === inst.id_instructor && e.estado === "Evaluado")
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

  return (
    <div className="home-page">
      {/* ── ENCABEZADO ── */}
      <div className="home-header">
        <div>
          <h1>¡Hola, {usuario?.nombre || "Usuario"}!</h1>
          <p>
            {esAdminCoord
              ? "Panel de control del sistema de evaluación de instructores SENA"
              : "Bienvenido al sistema de evaluación de instructores del SENA"}
          </p>
        </div>
        <div className="home-fecha">
          <i className="bi bi-calendar3"></i>
          {new Date().toLocaleDateString("es-CO", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric"
          })}
        </div>
      </div>

      {error && <div className="home-alerta home-alerta-error">{error}</div>}

      {/* ── BANNER PRINCIPAL ── */}
      <section className="home-banner">
        <div className="home-banner-texto">
          <h2>
            {esAdminCoord
              ? "Gestiona y consulta las evaluaciones"
              : "Tu opinión fortalece la calidad de la formación"}
          </h2>
          <p>
            {esAdminCoord
              ? "Monitorea el desempeño de los instructores, consulta reportes y gestiona el proceso de evaluación académica."
              : "Evalúa a tus instructores de forma honesta y constructiva. Tus comentarios contribuyen a mejorar la calidad de la enseñanza en el SENA."}
          </p>
          <Link
            to={esAdminCoord ? "/historial" : "/evaluaciones"}
            className="home-btn-principal"
          >
            <i className={`bi ${esAdminCoord ? "bi-clipboard-data" : "bi-clipboard-check"}`}></i>
            {esAdminCoord ? "Ver evaluaciones realizadas" : "Realizar evaluación"}
          </Link>
        </div>
        <div className="home-banner-imagen">
          <img
            src="/imgs/logo-sena.png"
            alt="Logo SENA"
          />
        </div>
      </section>

      {/* ── STATS ── */}
      <section className="home-stats">
        {esAdminCoord ? (
          <>
            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-verde">
                <i className="bi bi-people"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{totalInstructores}</span>
                <span className="home-stat-label">Instructores registrados</span>
              </div>
            </div>
            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-azul">
                <i className="bi bi-mortarboard"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{totalAprendices}</span>
                <span className="home-stat-label">Aprendices activos</span>
              </div>
            </div>
            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-naranja">
                <i className="bi bi-card-text"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{totalFichas}</span>
                <span className="home-stat-label">Fichas de formación</span>
              </div>
            </div>
            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-morado">
                <i className="bi bi-clipboard-check"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{totalEvaluaciones}</span>
                <span className="home-stat-label">Evaluaciones registradas</span>
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-verde">
                <i className="bi bi-people"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{instructoresAsignados.length}</span>
                <span className="home-stat-label">Instructores asignados</span>
              </div>
            </div>
            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-azul">
                <i className="bi bi-check-circle"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{evaluacionesRealizadas}</span>
                <span className="home-stat-label">Evaluaciones realizadas</span>
              </div>
            </div>
            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-naranja">
                <i className="bi bi-hourglass-split"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{Math.max(0, evaluacionesPendientesAprendiz)}</span>
                <span className="home-stat-label">Evaluaciones pendientes</span>
              </div>
            </div>
            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-morado">
                <i className="bi bi-question-circle"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{preguntasActivas.length}</span>
                <span className="home-stat-label">Preguntas de evaluación</span>
              </div>
            </div>
          </>
        )}
      </section>

      {/* ── CONTENIDO ESPECÍFICO POR ROL ── */}
      <div className="home-grid">
        {/* ── Panel izquierdo ── */}
        <div className="home-col-principal">
          {esAdminCoord ? (
            /* ── ADMIN: Últimas evaluaciones ── */
            <div className="home-card">
              <div className="home-card-header">
                <h3><i className="bi bi-clock-history"></i> Últimas evaluaciones</h3>
                <Link to="/historial" className="home-card-link">Ver todo</Link>
              </div>
              <div className="home-card-body">
                {ultimasEvaluaciones.length === 0 ? (
                  <div className="home-vacio">
                    <i className="bi bi-inbox"></i>
                    <p>No hay evaluaciones registradas aún</p>
                  </div>
                ) : (
                  <div className="home-lista">
                    {ultimasEvaluaciones.map((ev, idx) => (
                      <div className="home-lista-item" key={idx}>
                        <div className="home-lista-icono">
                          <i className={`bi ${ev.estado === "Evaluado" ? "bi-check-circle-fill" : "bi-circle"}`}></i>
                        </div>
                        <div className="home-lista-info">
                          <span className="home-lista-titulo">
                            {ev.instructor || `Instructor #${ev.id_instructor}`}
                          </span>
                          <span className="home-lista-meta">
                            {ev.aprendiz || `Aprendiz`} · {ev.ficha || "Ficha"} · {new Date(ev.fecha).toLocaleDateString("es-CO")}
                          </span>
                        </div>
                        <span className={`home-lista-badge ${ev.estado?.toLowerCase()}`}>
                          {ev.estado}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            /* ── APRENDIZ: Progreso e instructores pendientes ── */
            <>
              {/* Progreso */}
              <div className="home-card">
                <div className="home-card-header">
                  <h3><i className="bi bi-bar-chart-line"></i> Tu progreso de evaluación</h3>
                </div>
                <div className="home-card-body">
                  {instructoresAsignados.length === 0 ? (
                    <div className="home-vacio">
                      <i className="bi bi-inbox"></i>
                      <p>No tienes instructores asignados aún</p>
                    </div>
                  ) : (
                    <>
                      <div className="home-progreso">
                        <div className="home-progreso-info">
                          <span>{evaluacionesRealizadas} de {instructoresAsignados.length} evaluaciones completadas</span>
                          <span className="home-progreso-porcentaje">{progresoEvaluacion}%</span>
                        </div>
                        <div className="home-progreso-barra">
                          <div
                            className="home-progreso-fill"
                            style={{ width: `${progresoEvaluacion}%` }}
                          ></div>
                        </div>
                      </div>

                      {instructoresPendientes.length > 0 && (
                        <div className="home-pendientes">
                          <h4>Instructores pendientes por evaluar</h4>
                          <div className="home-pendientes-lista">
                            {instructoresPendientes.slice(0, 4).map((inst) => (
                              <div className="home-pendiente-item" key={inst.id_instructor}>
                                {inst.foto ? (
                                  <img src={`http://localhost:8000${inst.foto}`} alt={inst.nombre} />
                                ) : (
                                  <div className="home-pendiente-foto-placeholder">
                                    <i className="bi bi-person"></i>
                                  </div>
                                )}
                                <div className="home-pendiente-info">
                                  <span className="home-pendiente-nombre">{inst.nombre} {inst.apellido}</span>
                                  <span className="home-pendiente-meta">{inst.correo}</span>
                                </div>
                                <button
                                  className="home-pendiente-btn"
                                  onClick={() => navigate("/evaluaciones")}
                                >
                                  Evaluar
                                </button>
                              </div>
                            ))}
                          </div>
                          {instructoresPendientes.length > 4 && (
                            <Link to="/evaluaciones" className="home-ver-mas">
                              Ver {instructoresPendientes.length - 4} más →
                            </Link>
                          )}
                        </div>
                      )}

                      {instructoresPendientes.length === 0 && (
                        <div className="home-completado">
                          <i className="bi bi-trophy-fill"></i>
                          <h4>¡Excelente trabajo!</h4>
                          <p>Has evaluado a todos tus instructores. Gracias por tu participación.</p>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </>
          )}
        </div>

        {/* ── Panel derecho ── */}
        <div className="home-col-secundaria">
          {/* Info del sistema */}
          <div className="home-card home-card-info">
            <div className="home-card-header">
              <h3><i className="bi bi-info-circle"></i> Sobre el sistema</h3>
            </div>
            <div className="home-card-body">
              <p>
                Este sistema permite que los aprendices evalúen a los instructores
                correspondientes a su ficha de formación, garantizando confiabilidad
                en los resultados y control de acceso por roles.
              </p>
              <div className="home-info-items">
                <div className="home-info-item">
                  <i className="bi bi-shield-check"></i>
                  <span>Evaluaciones anónimas y seguras</span>
                </div>
                <div className="home-info-item">
                  <i className="bi bi-lock"></i>
                  <span>Acceso restringido por ficha</span>
                </div>
                <div className="home-info-item">
                  <i className="bi bi-graph-up"></i>
                  <span>Reportes y estadísticas en tiempo real</span>
                </div>
              </div>
            </div>
          </div>

          {/* Accesos rápidos */}
          <div className="home-card">
            <div className="home-card-header">
              <h3><i className="bi bi-lightning"></i> Accesos rápidos</h3>
            </div>
            <div className="home-card-body">
              <div className="home-accesos">
                {esAdminCoord ? (
                  <>
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
                  </>
                ) : (
                  <>
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
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
