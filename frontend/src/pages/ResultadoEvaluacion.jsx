import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { obtenerEvaluacion } from "../services/evaluacionServices";
import { obtenerRespuestas } from "../services/Respuestaservice";

function ResultadoEvaluacion() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [evaluacion, setEvaluacion] = useState(null);
  const [respuestas, setRespuestas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        const [ev, resp] = await Promise.all([
          obtenerEvaluacion(id),
          obtenerRespuestas(id),
        ]);
        setEvaluacion(ev);
        setRespuestas(resp);
      } catch (err) {
        setError("Error al cargar el resultado: " + (err.response?.data?.detail || err.message));
      } finally {
        setCargando(false);
      }
    };
    cargarDatos();
  }, [id]);

  if (cargando) return <p>Cargando resultado...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!evaluacion) return <p>No se encontró la evaluación</p>;

  return (
    <div>
      <h2>Resultado de la Evaluación</h2>
      <p><strong>Estado:</strong> {evaluacion.estado}</p>
      <p><strong>Fecha:</strong> {new Date(evaluacion.fecha).toLocaleDateString("es-CO")}</p>
      
      <h3>Respuestas</h3>
      {respuestas.length === 0 ? (
        <p>No hay respuestas registradas.</p>
      ) : (
        <ul>
          {respuestas.map((r) => (
            <li key={r.id_respuesta}>
              <strong>{r.pregunta_texto || `Pregunta #${r.id_pregunta}`}:</strong> {r.texto}
              {r.calificacion !== undefined && (
                <span style={{ marginLeft: "1rem", color: "green" }}>
                  Calificación: {r.calificacion}
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
      <button onClick={() => navigate("/evaluaciones")} style={{ marginTop: "1rem" }}>
        Volver a evaluaciones
      </button>
    </div>
  );
}

export default ResultadoEvaluacion;