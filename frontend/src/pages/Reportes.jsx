import { useEffect, useState } from "react";
import api from "../api/axiosConfig";
import { listarPeriodos } from "../services/PeriodoService";
import { listarFichas } from "../services/FichaServices";
import { listarInstructores } from "../services/instructorService";
import { reportePreguntasInstructor } from "../services/Reporteservice";
import "../styles/Home.css";

function Reportes() {
  const [periodos, setPeriodos] = useState([]);
  const [fichas, setFichas] = useState([]);
  const [instructores, setInstructores] = useState([]);

  const [filtros, setFiltros] = useState({
    periodo_id: "",
    ficha_id: "",
    instructor_id: "",
  });

  const [reporte, setReporte] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  // Estados para el detalle por pregunta
  const [instructorSeleccionado, setInstructorSeleccionado] = useState(null);
  const [detallePreguntas, setDetallePreguntas] = useState([]);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);

  useEffect(() => {
    listarPeriodos().then(setPeriodos).catch(console.error);
    listarFichas().then(setFichas).catch(console.error);
    listarInstructores().then(setInstructores).catch(console.error);
  }, []);

  const cargarReporte = async () => {
    try {
      setCargando(true);
      setError("");
      const params = {};
      if (filtros.periodo_id) params.periodo_id = filtros.periodo_id;
      if (filtros.ficha_id) params.ficha_id = filtros.ficha_id;
      if (filtros.instructor_id) params.instructor_id = filtros.instructor_id;

      const response = await api.get("/reportes/dashboard", { params });
      setReporte(response.data);
    } catch (err) {
      setError("No se pudo cargar el reporte.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarReporte();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtros.periodo_id, filtros.ficha_id, filtros.instructor_id]);

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFiltros((prev) => ({ ...prev, [name]: value }));
  };

  const verDetalleInstructor = async (inst) => {
    try {
      setCargandoDetalle(true);
      setInstructorSeleccionado(inst);
      const params = {};
      if (filtros.periodo_id) params.periodo_id = filtros.periodo_id;
      if (filtros.ficha_id) params.ficha_id = filtros.ficha_id;
      const data = await reportePreguntasInstructor(inst.id_instructor, params);
      setDetallePreguntas(data.preguntas || []);
    } catch (err) {
      console.error(err);
      setDetallePreguntas([]);
    } finally {
      setCargandoDetalle(false);
    }
  };

  // ── Helpers de color según promedio (escala 1–5) ──
  const getColorClass = (valor) => {
    const escala = valor > 5 ? valor / 20 : valor;
    if (escala >= 4.0) return "verde";
    if (escala >= 3.0) return "amarillo";
    return "rojo";
  };

  const getBadgeStyle = (valor) => {
    const escala = valor > 5 ? valor / 20 : valor;
    if (escala >= 4.0)
      return { background: "#d1fae5", color: "#065f46", border: "1px solid #a7f3d0" };
    if (escala >= 3.0)
      return { background: "#fef3c7", color: "#92400e", border: "1px solid #fde68a" };
    return { background: "#fee2e2", color: "#991b1b", border: "1px solid #fecaca" };
  };

  const getBarGradient = (valor) => {
    const escala = valor > 5 ? valor / 20 : valor;
    if (escala >= 4.0) return "linear-gradient(90deg, #39a900, #2d7a4f)";
    if (escala >= 3.0) return "linear-gradient(90deg, #f59e0b, #d97706)";
    return "linear-gradient(90deg, #ef4444, #b91c1c)";
  };

  const formatPromedio = (valor) => {
    const escala = valor > 5 ? valor / 20 : valor;
    return escala.toFixed(1);
  };

  return (
    <div className="home-page">
      {/* ── Encabezado ── */}
      <div className="home-header">
        <div>
          <h1>Reportes de Evaluación</h1>
          <p>Consulta el desempeño de los instructores por periodo, ficha o instructor.</p>
        </div>
      </div>

      {/* ── Filtros ── */}
      <div className="home-card" style={{ marginBottom: "24px" }}>
        <div className="home-card-header">
          <h3><i className="bi bi-funnel"></i> Filtros de consulta</h3>
        </div>
        <div className="home-card-body">
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px" }}>
            <div>
              <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "#374151", marginBottom: "6px", display: "block" }}>
                Periodo
              </label>
              <select
                name="periodo_id"
                value={filtros.periodo_id}
                onChange={manejarCambio}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  borderRadius: "10px",
                  border: "1px solid #e5e7eb",
                  fontSize: "0.85rem",
                  color: "#374151",
                  background: "#fff",
                  outline: "none",
                  cursor: "pointer",
                }}
              >
                <option value="">Todos los periodos</option>
                {periodos.map((p) => (
                  <option key={p.id_periodo} value={p.id_periodo}>
                    {p.nombre}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "#374151", marginBottom: "6px", display: "block" }}>
                Ficha
              </label>
              <select
                name="ficha_id"
                value={filtros.ficha_id}
                onChange={manejarCambio}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  borderRadius: "10px",
                  border: "1px solid #e5e7eb",
                  fontSize: "0.85rem",
                  color: "#374151",
                  background: "#fff",
                  outline: "none",
                  cursor: "pointer",
                }}
              >
                <option value="">Todas las fichas</option>
                {fichas.map((f) => (
                  <option key={f.id_ficha} value={f.id_ficha}>
                    {f.numero_ficha} - {f.programa}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "#374151", marginBottom: "6px", display: "block" }}>
                Instructor
              </label>
              <select
                name="instructor_id"
                value={filtros.instructor_id}
                onChange={manejarCambio}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  borderRadius: "10px",
                  border: "1px solid #e5e7eb",
                  fontSize: "0.85rem",
                  color: "#374151",
                  background: "#fff",
                  outline: "none",
                  cursor: "pointer",
                }}
              >
                <option value="">Todos los instructores</option>
                {instructores.map((i) => (
                  <option key={i.id_instructor} value={i.id_instructor}>
                    {i.nombre} {i.apellido}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="home-alerta home-alerta-error" style={{ marginBottom: "20px" }}>
          <i className="bi bi-exclamation-triangle-fill"></i> {error}
        </div>
      )}

      {cargando && (
        <div className="home-cargando" style={{ minHeight: "200px" }}>
          <div className="spinner-home"></div>
          <p>Cargando reporte...</p>
        </div>
      )}

      {reporte && !cargando && (
        <>
          {/* ── Stats Cards ── */}
          <section className="home-stats" style={{ gridTemplateColumns: "repeat(3, 1fr)" }}>
            <div className="home-stat-card">
              <div className={`home-stat-icon home-stat-${getColorClass(reporte.promedio_general)}`}>
                <i className="bi bi-star-fill"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{formatPromedio(reporte.promedio_general)}</span>
                <span className="home-stat-label">Promedio General</span>
              </div>
            </div>

            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-azul">
                <i className="bi bi-clipboard-check"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{reporte.total_evaluaciones}</span>
                <span className="home-stat-label">Evaluaciones</span>
              </div>
            </div>

            <div className="home-stat-card">
              <div className="home-stat-icon home-stat-morado">
                <i className="bi bi-people"></i>
              </div>
              <div className="home-stat-info">
                <span className="home-stat-num">{reporte.instructores_evaluados}</span>
                <span className="home-stat-label">Instructores Evaluados</span>
              </div>
            </div>
          </section>

          {/* ── Tabla de desempeño ── */}
          <div className="home-card" style={{ marginTop: "24px" }}>
            <div className="home-card-header">
              <h3><i className="bi bi-bar-chart-line"></i> Desempeño por Instructor</h3>
            </div>
            <div className="home-card-body">
              {reporte.detalle_instructores.length === 0 ? (
                <div className="home-vacio">
                  <i className="bi bi-inbox"></i>
                  <p>No hay datos para mostrar.</p>
                </div>
              ) : (
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                    <thead>
                      <tr style={{ borderBottom: "2px solid #f3f4f6" }}>
                        <th style={{ textAlign: "left", padding: "12px 14px", color: "#6b7280", fontWeight: 600, fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                          Instructor
                        </th>
                        <th style={{ textAlign: "center", padding: "12px 14px", color: "#6b7280", fontWeight: 600, fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                          Promedio
                        </th>
                        <th style={{ textAlign: "center", padding: "12px 14px", color: "#6b7280", fontWeight: 600, fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                          Respuestas
                        </th>
                        <th style={{ textAlign: "left", padding: "12px 14px", color: "#6b7280", fontWeight: 600, fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.04em", width: "35%" }}>
                          Barra de progreso
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {reporte.detalle_instructores.map((inst) => {
                        const color = getColorClass(inst.promedio);
                        const badgeStyle = getBadgeStyle(inst.promedio);
                        const barGradient = getBarGradient(inst.promedio);
                        const promedioFormateado = formatPromedio(inst.promedio);
                        const porcentajeBarra = Math.min((inst.promedio > 5 ? inst.promedio : inst.promedio * 20), 100);

                        return (
                          <tr
                            key={inst.id_instructor}
                            onClick={() => verDetalleInstructor(inst)}
                            style={{ borderBottom: "1px solid #f3f4f6", transition: "background 0.15s", cursor: "pointer" }}
                            onMouseEnter={(e) => (e.currentTarget.style.background = "#f9fafb")}
                            onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                          >
                            <td style={{ padding: "14px" }}>
                              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                                <div
                                  style={{
                                    width: "36px",
                                    height: "36px",
                                    borderRadius: "50%",
                                    background: color === "verde" ? "#ecfdf5" : color === "amarillo" ? "#fffbeb" : "#fef2f2",
                                    color: color === "verde" ? "#065f46" : color === "amarillo" ? "#92400e" : "#991b1b",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    fontSize: "0.9rem",
                                    fontWeight: 700,
                                    flexShrink: 0,
                                  }}
                                >
                                  {inst.nombre?.charAt(0)?.toUpperCase() || "I"}
                                </div>
                                <span style={{ fontWeight: 600, color: "#1f2937" }}>
                                  {inst.nombre} <small style={{ color: "#9ca3af" }}> · ver detalle</small>
                                </span>
                              </div>
                            </td>
                            <td style={{ padding: "14px", textAlign: "center" }}>
                              <span
                                style={{
                                  display: "inline-block",
                                  padding: "6px 14px",
                                  borderRadius: "20px",
                                  fontSize: "0.85rem",
                                  fontWeight: 700,
                                  ...badgeStyle,
                                }}
                              >
                                {promedioFormateado}
                              </span>
                            </td>
                            <td style={{ padding: "14px", textAlign: "center", color: "#6b7280", fontWeight: 500 }}>
                              {inst.respuestas}
                            </td>
                            <td style={{ padding: "14px" }}>
                              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                                <div
                                  style={{
                                    flex: 1,
                                    height: "10px",
                                    background: "#e5e7eb",
                                    borderRadius: "5px",
                                    overflow: "hidden",
                                  }}
                                >
                                  <div
                                    style={{
                                      height: "100%",
                                      width: `${porcentajeBarra}%`,
                                      background: barGradient,
                                      borderRadius: "5px",
                                      transition: "width 0.6s ease",
                                    }}
                                  />
                                </div>
                                <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "#6b7280", minWidth: "36px", textAlign: "right" }}>
                                  {porcentajeBarra.toFixed(0)}%
                                </span>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* ── Detalle por pregunta al oprimir un instructor ── */}
          {instructorSeleccionado && (
            <div className="home-card" style={{ marginTop: "24px" }}>
              <div className="home-card-header" style={{ display: "flex", justifyContent: "space-between" }}>
                <h3><i className="bi bi-list-check"></i> Detalle: {instructorSeleccionado.nombre}</h3>
                <button onClick={() => setInstructorSeleccionado(null)} style={{ width: "auto", margin: 0, padding: "6px 14px" }}>Cerrar</button>
              </div>
              <div className="home-card-body">
                {cargandoDetalle && <p>Cargando detalle...</p>}
                {!cargandoDetalle && detallePreguntas.length === 0 && (
                  <p style={{ color: "#6b7280" }}>No hay respuestas registradas para este instructor.</p>
                )}
                {!cargandoDetalle && detallePreguntas.map((p) => {
                  const colores = {
                    verde: { fondo: "#d1fae5", texto: "#065f46", borde: "#a7f3d0", barra: "linear-gradient(90deg,#39a900,#2d7a4f)" },
                    amarillo: { fondo: "#fef3c7", texto: "#92400e", borde: "#fde68a", barra: "linear-gradient(90deg,#f59e0b,#d97706)" },
                    rojo: { fondo: "#fee2e2", texto: "#991b1b", borde: "#fecaca", barra: "linear-gradient(90deg,#ef4444,#b91c1c)" },
                  };
                  const c = colores[p.color] || colores.verde;
                  return (
                    <div key={p.id_pregunta} style={{ padding: "14px 0", borderBottom: "1px solid #f3f4f6" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", gap: "10px", marginBottom: "6px" }}>
                        <p style={{ margin: 0, fontWeight: 600 }}>{p.orden}. {p.pregunta}</p>
                        <span style={{ padding: "4px 12px", borderRadius: "20px", fontWeight: 700, fontSize: "0.85rem", background: c.fondo, color: c.texto, border: `1px solid ${c.borde}` }}>
                          {p.porcentaje}%
                        </span>
                      </div>
                      <div style={{ height: "10px", background: "#e5e7eb", borderRadius: "5px", overflow: "hidden", marginBottom: "6px" }}>
                        <div style={{ height: "100%", width: `${Math.min(p.porcentaje, 100)}%`, background: c.barra }} />
                      </div>
                      <small style={{ color: "#6b7280" }}>Fichas que evaluaron: {p.fichas.join(", ") || "—"}</small>
                      {/* 3.0–4.0: advertencia de mejora · <3.0: alerta roja */}
                      {p.color !== "verde" && (
                        <p style={{ margin: "6px 0 0", fontSize: "0.82rem", fontWeight: 600, color: c.texto }}>
                          {p.mensaje}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Reportes;