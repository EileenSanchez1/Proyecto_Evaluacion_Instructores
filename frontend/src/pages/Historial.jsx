import { useEffect, useState } from "react";
import api from "../api/axiosConfig";
import { detalleEvaluacion } from "../services/Reporteservice";
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
  const [detalle, setDetalle] = useState(null);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);

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

  const verDetalle = async (id) => {
    try {
      setCargandoDetalle(true);
      setDetalle(null);
      const data = await detalleEvaluacion(id);
      setDetalle(data);
    } catch (err) {
      alert(err.response?.data?.detail || "No se pudo cargar el detalle.");
    } finally {
      setCargandoDetalle(false);
    }
  };

  return (
    <div className="container-fluid page-content-eval py-4">
      <div className="evaluation-header">
        <div>
          <h2>
            <i className="bi bi-clock-history"></i> Evaluaciones
          </h2>
          <p>Consulta el registro completo de evaluaciones del sistema.</p>
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
                <th>Detalle</th>
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
                      className="badge px-3 py-2"
                      style={{
                        backgroundColor:
                          h.estado === "Evaluado" || h.estado === "Completada"
                            ? "#d1fae5"
                            : "#fef3c7",
                        color:
                          h.estado === "Evaluado" || h.estado === "Completada"
                            ? "#065f46"
                            : "#92400e",
                        border:
                          h.estado === "Evaluado" || h.estado === "Completada"
                            ? "1px solid #a7f3d0"
                            : "1px solid #fde68a",
                        fontWeight: 700,
                        borderRadius: "20px",
                        display: "inline-block",
                      }}
                    >
                      {h.estado}
                    </span>
                  </td>
                  <td>
                    <button
                      type="button"
                      className="btn-evaluar"
                      style={{ padding: "6px 12px", fontSize: "0.85rem" }}
                      onClick={() => verDetalle(h.id_evaluacion)}
                    >
                      Ver detalle
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {(detalle || cargandoDetalle) && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(15,23,42,0.45)",
            zIndex: 1000,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 16,
          }}
          onClick={() => !cargandoDetalle && setDetalle(null)}
        >
          <div
            style={{
              background: "#fff",
              borderRadius: 16,
              maxWidth: 720,
              width: "100%",
              maxHeight: "90vh",
              overflow: "auto",
              padding: 24,
              boxShadow: "0 20px 50px rgba(0,0,0,.2)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {cargandoDetalle && <p>Cargando detalle...</p>}
            {detalle && (
              <>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 12,
                    marginBottom: 16,
                  }}
                >
                  <div>
                    <h3 style={{ margin: 0 }}>Detalle de evaluación</h3>
                    <p style={{ color: "#6b7280", margin: "6px 0 0" }}>
                      {detalle.fecha
                        ? new Date(detalle.fecha).toLocaleDateString("es-CO")
                        : ""}{" "}
                      · Ficha {detalle.ficha} · {detalle.programa}
                    </p>
                    <p style={{ margin: "4px 0 0" }}>
                      <strong>Instructor:</strong> {detalle.instructor} ·{" "}
                      <strong>Periodo:</strong> {detalle.periodo}
                    </p>
                    <p style={{ margin: "4px 0 0" }}>
                      <strong>Aprendiz:</strong> {detalle.aprendiz} ·{" "}
                      <strong>Estado:</strong> {detalle.estado}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setDetalle(null)}
                    style={{
                      border: "none",
                      background: "#f3f4f6",
                      borderRadius: 8,
                      padding: "8px 12px",
                      cursor: "pointer",
                    }}
                  >
                    Cerrar
                  </button>
                </div>

                <h4 style={{ marginTop: 8 }}>Calificaciones por pregunta</h4>
                <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                  {(detalle.respuestas || []).map((r) => (
                    <li
                      key={r.id_pregunta}
                      style={{
                        padding: "12px 0",
                        borderBottom: "1px solid #f3f4f6",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          gap: 12,
                          flexWrap: "wrap",
                        }}
                      >
                        <span>
                          <strong>{r.orden}.</strong> {r.pregunta}
                        </span>
                        <span style={{ fontWeight: 700, color: "#39a900" }}>
                          {r.calificacion} / 5
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>

                {detalle.observacion_general && (
                  <div
                    style={{
                      marginTop: 20,
                      padding: 16,
                      background: "#ecfdf5",
                      border: "1px solid #a7f3d0",
                      borderRadius: 12,
                    }}
                  >
                    <h4 style={{ margin: "0 0 8px", color: "#065f46" }}>
                      <i className="bi bi-chat-quote"></i> Observación general del
                      aprendiz
                    </h4>
                    <p style={{ margin: 0, color: "#1f2937", lineHeight: 1.5 }}>
                      {detalle.observacion_general}
                    </p>
                  </div>
                )}

                {!detalle.observacion_general && (
                  <p style={{ color: "#9ca3af", marginTop: 12 }}>
                    Esta evaluación no tiene observación general registrada.
                  </p>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Historial;
