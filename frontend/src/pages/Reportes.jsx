import { useEffect, useState } from "react";
import api from "../api/axiosConfig";
import { listarPeriodos } from "../services/PeriodoService";
import { listarFichas } from "../services/FichaServices";
import { listarInstructores } from "../services/instructorService";
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

  return (
    <div className="dashboard-content">
      <div className="welcome-section">
        <h1>Reportes de Evaluación</h1>
        <p>Consulta el desempeño de los instructores por periodo.</p>
      </div>

      <div className="card shadow-sm mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-4">
              <label className="form-label">Periodo</label>
              <select
                name="periodo_id"
                className="form-select"
                value={filtros.periodo_id}
                onChange={manejarCambio}
              >
                <option value="">Todos los periodos</option>
                {periodos.map((p) => (
                  <option key={p.id_periodo} value={p.id_periodo}>
                    {p.nombre}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Ficha</label>
              <select
                name="ficha_id"
                className="form-select"
                value={filtros.ficha_id}
                onChange={manejarCambio}
              >
                <option value="">Todas las fichas</option>
                {fichas.map((f) => (
                  <option key={f.id_ficha} value={f.id_ficha}>
                    {f.numero_ficha} - {f.programa}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Instructor</label>
              <select
                name="instructor_id"
                className="form-select"
                value={filtros.instructor_id}
                onChange={manejarCambio}
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

      {error && <div className="alert alert-danger">{error}</div>}

      {cargando && <p className="text-muted">Cargando reporte...</p>}

      {reporte && !cargando && (
        <>
          <section className="stats-section">
            <div className="stat-card">
              <div className="stat-header">
                <div className="stat-icon green">✓</div>
                <span className="stat-label">Promedio General</span>
              </div>
              <div className="stat-number">{reporte.promedio_general}%</div>
            </div>

            <div className="stat-card">
              <div className="stat-header">
                <div className="stat-icon blue">📋</div>
                <span className="stat-label">Evaluaciones</span>
              </div>
              <div className="stat-number">{reporte.total_evaluaciones}</div>
            </div>

            <div className="stat-card">
              <div className="stat-header">
                <div className="stat-icon teal">👤</div>
                <span className="stat-label">Instructores Evaluados</span>
              </div>
              <div className="stat-number">
                {reporte.instructores_evaluados}
              </div>
            </div>
          </section>

          <div className="card shadow-sm mt-4">
            <div className="card-body">
              <h5 className="mb-3">
                <i className="bi bi-bar-chart-fill"></i> Desempeño por Instructor
              </h5>

              {reporte.detalle_instructores.length === 0 ? (
                <p className="text-muted">No hay datos para mostrar.</p>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover align-middle">
                    <thead>
                      <tr>
                        <th>Instructor</th>
                        <th>Promedio</th>
                        <th>Respuestas</th>
                        <th>Visual</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reporte.detalle_instructores.map((inst) => (
                        <tr key={inst.id_instructor}>
                          <td>
                            <strong>{inst.nombre}</strong>
                          </td>
                          <td>
                            <span
                              className={`badge ${
                                inst.promedio >= 80
                                  ? "bg-success"
                                  : inst.promedio >= 60
                                  ? "bg-warning text-dark"
                                  : "bg-danger"
                              }`}
                            >
                              {inst.promedio}%
                            </span>
                          </td>
                          <td>{inst.respuestas}</td>
                          <td style={{ width: "30%" }}>
                            <div className="progress">
                              <div
                                className={`progress-bar ${
                                  inst.promedio >= 80
                                    ? "bg-success"
                                    : inst.promedio >= 60
                                    ? "bg-warning"
                                    : "bg-danger"
                                }`}
                                role="progressbar"
                                style={{ width: `${inst.promedio}%` }}
                                aria-valuenow={inst.promedio}
                                aria-valuemin="0"
                                aria-valuemax="100"
                              >
                                {inst.promedio}%
                              </div>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Reportes;
