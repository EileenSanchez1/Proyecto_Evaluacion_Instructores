import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listarEvaluaciones } from "../services/evaluacionService";
import { obtenerAprendiz } from "../services/aprendizService";

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
    <div>
      <h1>Evaluaciones</h1>

      {cargando && <p>Cargando evaluaciones...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!cargando && !error && evaluaciones.length === 0 && (
        <p>No hay evaluaciones registradas.</p>
      )}

      {!cargando && evaluaciones.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Aprendiz</th>
              <th>Fecha</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {evaluaciones.map((ev) => {
              const aprendiz = aprendices[ev.id_aprendiz];
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
                      style={{
                        color: ev.estado === "Evaluado" ? "green" : "#b8860b",
                        fontWeight: "bold",
                      }}
                    >
                      {ev.estado}
                    </span>
                  </td>
                  <td>
                    <button
                      onClick={() =>
                        navigate(`/evaluaciones/${ev.id_evaluacion}`)
                      }
                    >
                      {ev.estado === "Evaluado"
                        ? "Ver resultado"
                        : "Responder"}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Evaluaciones;