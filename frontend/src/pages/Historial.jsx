import { useEffect, useState } from "react";
import api from "../api/axiosConfig";
import { listarPeriodos } from "../services/PeriodoService";
import { listarFichas } from "../services/FichaServices";
import "../styles/Evaluaciones.css";

function formatearFecha(fecha) {
  if (!fecha) return "-";
  const f = new Date(fecha);
  if (Number.isNaN(f.getTime())) return fecha;
  return f.toLocaleDateString("es-CO", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

function Historial() {
  const [historial, setHistorial] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [fichas, setFichas] = useState([]);
  const [filtros, setFiltros] = useState({
    periodo_id: "",
    ficha_id: "",
  });
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    listarPeriodos().then(setPeriodos).catch(console.error);
    listarFichas().then(setFichas).catch(console.error);
  }, []);

  const cargarHistorial = async () => {
    try {
      setCargando(true);
      setError("");
      const params = {};
      if (filtros.periodo_id) params.periodo_id = filtros.periodo_id;
      if (filtros.ficha_id) params.ficha_id = filtros.ficha_id;

      const response = await api.get("/reportes/historial", { params });
      setHistorial(response.data);
    } catch (err) {
      setError("No se pudo cargar el historial.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarHistorial();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtros.periodo_id, filtros.ficha_id]);

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFiltros((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="container-fluid page-content-eval py-4">
      <div className="evaluation-header">
        <div>
          <h2>
            <i className="bi bi-clock-history"></i> Historial de Evaluaciones
          </h2>
          <p>Consulta el historial completo de evaluaciones del sistema.</p>
        </div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-md-4">
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
          <select
            name="ficha_id"
            className="form-select"
            value={filtros.ficha_id}
            onChange={manejarCambio}
          >
            <option value="">Todas las fichas</option>
            {fichas.map((f) => (
              <option key={f.id_ficha} value={f.id_ficha}>
                {f.numero_ficha}
              </option>
            ))}
          </select>
        </div>
      </div>

      {cargando && <p className="text-muted">Cargando historial...</p>}
      {error && <p className="text-danger">{error}</p>}

      {!cargando && historial.length === 0 && (
        <p className="text-muted">No hay evaluaciones registradas.</p>
      )}

      {!cargando && historial.length > 0 && (
        <div className="table-responsive">
          <table className="table table-hover align-middle evaluaciones-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Periodo</th>
                <th>Aprendiz</th>
                <th>Ficha</th>
                <th>Programa</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {historial.map((h) => (
                <tr key={h.id_evaluacion}>
                  <td>#{h.id_evaluacion}</td>
                  <td>{formatearFecha(h.fecha)}</td>
                  <td>{h.periodo}</td>
                  <td>{h.aprendiz}</td>
                  <td>{h.ficha}</td>
                  <td>{h.programa}</td>
                  <td>
                    <span
                      className={`badge ${
                        h.estado === "Evaluado"
                          ? "badge-evaluado"
                          : "badge-pendiente"
                      } px-3 py-2`}
                    >
                      {h.estado}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Historial;
