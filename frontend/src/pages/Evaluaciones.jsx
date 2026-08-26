import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  listarEvaluaciones,
  eliminarEvaluacion,
} from "../services/evaluacionService";
import { obtenerAprendiz } from "../services/Aprendizservice";

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
  const [eliminandoId, setEliminandoId] = useState(null);

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

  const manejarEliminar = async (ev) => {
    const aprendiz = aprendices[ev.id_aprendiz];
    const nombre = aprendiz
      ? `${aprendiz.nombre} ${aprendiz.apellido}`
      : `#${ev.id_evaluacion}`;

    if (
      !window.confirm(
        `¿Eliminar la evaluación de ${nombre}? Esta acción no se puede deshacer y también elimina sus respuestas.`
      )
    ) {
      return;
    }

    setError("");
    try {
      setEliminandoId(ev.id_evaluacion);
      await eliminarEvaluacion(ev.id_evaluacion);
      await cargarEvaluaciones();
    } catch (err) {
      console.error("Error al eliminar evaluación:", err);
      const detalle = err.response?.data?.detail;
      setError(
        typeof detalle === "string"
          ? detalle
          : "No se pudo eliminar la evaluación."
      );
    } finally {
      setEliminandoId(null);
    }
  };

  return (
    <div>
      <h1>Evaluaciones</h1>

      <button onClick={() => navigate("/evaluaciones/crear")}>
        + Crear evaluación
      </button>

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
                      Ver detalles
                    </button>{" "}
                    <button
                      onClick={() =>
                        navigate(`/evaluaciones/editar/${ev.id_evaluacion}`)
                      }
                    >
                      Editar
                    </button>{" "}
                    <button
                      onClick={() => manejarEliminar(ev)}
                      disabled={eliminandoId === ev.id_evaluacion}
                    >
                      {eliminandoId === ev.id_evaluacion
                        ? "Eliminando..."
                        : "Eliminar"}
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