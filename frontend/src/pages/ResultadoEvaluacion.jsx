import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { obtenerEvaluacion } from "../services/evaluacionServices";
import { obtenerRespuestas } from "../services/Respuestaservice";
import {
  formatearRespuesta,
  porcentajeDesdeValor,
  colorDesdePorcentaje,
  porcentajeDesdePromedio,
  interpretacionPromedio,
} from "../utils/escalaEvaluacion";

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
        setRespuestas(resp || []);
      } catch (err) {
        setError(
          "Error al cargar el resultado: " +
            (err.response?.data?.detail || err.message)
        );
      } finally {
        setCargando(false);
      }
    };
    cargarDatos();
  }, [id]);

  if (cargando) return <p>Cargando resultado...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!evaluacion) return <p>No se encontró la evaluación</p>;

  const valores = (respuestas || [])
    .map((r) => Number(r.calificacion ?? r.respuesta ?? r.valor ?? 0))
    .filter((v) => v > 0);
  const promedio =
    valores.length > 0
      ? valores.reduce((a, b) => a + b, 0) / valores.length
      : 0;
  const pctGeneral = porcentajeDesdePromedio(promedio);

  return (
    <div style={{ padding: "24px 32px", maxWidth: 900, margin: "0 auto" }}>
      <h2 style={{ color: "#1a3c28" }}>Resultado de la Evaluación</h2>
      <p>
        <strong>Estado:</strong> {evaluacion.estado}
      </p>
      <p>
        <strong>Fecha:</strong>{" "}
        {new Date(evaluacion.fecha).toLocaleDateString("es-CO")}
      </p>

      {valores.length > 0 && (
        <div
          style={{
            margin: "16px 0",
            padding: 16,
            background: "#f0fdf4",
            borderRadius: 12,
            border: "1px solid #bbf7d0",
          }}
        >
          <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#166534" }}>
            {pctGeneral}% de desempeño
          </div>
          <div style={{ color: "#374151", marginTop: 4 }}>
            {interpretacionPromedio(promedio)}
          </div>
          <p style={{ margin: "8px 0 0", fontSize: "0.85rem", color: "#6b7280" }}>
            Escala de evaluación: Siempre · Algunas veces · Nunca
          </p>
        </div>
      )}

      <h3>Respuestas por pregunta</h3>
      {respuestas.length === 0 ? (
        <p>No hay respuestas registradas.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {respuestas.map((r) => {
            const valor = r.calificacion ?? r.respuesta ?? r.valor;
            const pct = porcentajeDesdeValor(valor);
            const color = colorDesdePorcentaje(pct);
            return (
              <li
                key={r.id_respuesta || r.id_pregunta}
                style={{
                  padding: "12px 0",
                  borderBottom: "1px solid #f3f4f6",
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 12,
                  flexWrap: "wrap",
                  alignItems: "center",
                }}
              >
                <span>
                  <strong>
                    {r.pregunta_texto || `Pregunta #${r.id_pregunta}`}
                  </strong>
                  {r.texto ? `: ${r.texto}` : ""}
                </span>
                <span
                  style={{
                    fontWeight: 700,
                    padding: "4px 12px",
                    borderRadius: 20,
                    background: color.fondo,
                    color: color.texto,
                    border: `1px solid ${color.borde}`,
                  }}
                >
                  {formatearRespuesta(valor)}
                </span>
              </li>
            );
          })}
        </ul>
      )}
      <button
        onClick={() => navigate("/evaluaciones")}
        style={{
          marginTop: "1rem",
          padding: "8px 16px",
          borderRadius: 8,
          border: "1px solid #e5e7eb",
          background: "#f3f4f6",
          cursor: "pointer",
        }}
      >
        Volver a evaluaciones
      </button>
    </div>
  );
}

export default ResultadoEvaluacion;
