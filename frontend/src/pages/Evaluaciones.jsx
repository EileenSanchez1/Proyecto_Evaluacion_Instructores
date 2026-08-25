import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listarEvaluaciones } from "../services/Evaluacionservice";
import { obtenerAprendiz } from "../services/Aprendizservice";
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

function Evaluaciones() {
  const navigate = useNavigate();
  const [evaluaciones, setEvaluaciones] = useState([]);
  const [aprendices, setAprendices] = useState({});
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargarEvaluaciones = async () => {
    try {
      setCargando(true);
      setError("");

      const datos = await listarEvaluaciones();
      setEvaluaciones(datos);

      // Traemos el nombre del aprendiz de cada evaluación para
      // que la tabla sea legible (el backend solo entrega id_aprendiz).
      const idsUnicos = [...new Set(datos.map((ev) => ev.id_aprendiz))];

      const mapa = {};
      await Promise.all(
        idsUnicos.map(async (id) => {
          try {
            mapa[id] = await obtenerAprendiz(id);
          } catch (err) {
            console.error("No se pudo cargar el aprendiz", id, err);
          }
        })
      );
      setAprendices(mapa);
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar las evaluaciones.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarEvaluaciones();
  }, []);

  return (
    <div className="container-fluid page-content-eval py-4">
      <div className="evaluation-header">
        <div>
          <h2>
            <i className="bi bi-clipboard-check"></i> Evaluaciones
          </h2>
          <p>Consulte y responda las evaluaciones de instructores asignadas.</p>
        </div>
      </div>

      <div className="card shadow-sm">
        <div className="card-body">
          {cargando && <p className="text-muted mb-0">Cargando evaluaciones...</p>}
          {error && <p className="text-danger mb-0">{error}</p>}

          {!cargando && !error && evaluaciones.length === 0 && (
            <p className="text-muted mb-0">No hay evaluaciones registradas.</p>
          )}

          {!cargando && evaluaciones.length > 0 && (
            <div className="table-responsive">
              <table className="table table-hover align-middle evaluaciones-table">
                <thead>
                  <tr>
                    <th>Aprendiz</th>
                    <th>Fecha</th>
                    <th>Estado</th>
                    <th className="text-end">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {evaluaciones.map((ev) => {
                    const aprendiz = aprendices[ev.id_aprendiz];
                    const evaluado = ev.estado === "Evaluado";
                    return (
                      <tr key={ev.id_evaluacion}>
                        <td>
                          {aprendiz
                            ? `${aprendiz.nombre} ${aprendiz.apellido}`
                            : `Aprendiz #${ev.id_aprendiz}`}
                        </td>
                        <td>{formatearFecha(ev.fecha)}</td>
                        <td>
                          <span
                            className={`badge ${
                              evaluado ? "badge-evaluado" : "badge-pendiente"
                            } px-3 py-2`}
                          >
                            {ev.estado}
                          </span>
                        </td>
                        <td className="text-end">
                          <button
                            className="btn btn-success btn-sm"
                            onClick={() =>
                              navigate(`/evaluaciones/${ev.id_evaluacion}`)
                            }
                          >
                            <i
                              className={`bi ${
                                evaluado ? "bi-eye" : "bi-pencil-square"
                              } me-1`}
                            ></i>
                            {evaluado ? "Ver resultado" : "Responder"}
                          </button>
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
    </div>
  );
}

export default Evaluaciones;