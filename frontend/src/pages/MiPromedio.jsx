import { useState, useEffect } from "react";
import { obtenerUsuarioSesion } from "../utils/sesion";
import { miPromedioInstructor } from "../services/Reporteservice";
import "../styles/Home.css";

function MiPromedio() {
  const usuario = obtenerUsuarioSesion();
  const [reporte, setReporte] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargarRendimiento = async () => {
      const idInstructor = usuario?.id_instructor || usuario?.id;
      if (!idInstructor) {
        setError("No se encontró sesión activa de instructor.");
        setCargando(false);
        return;
      }

      try {
        // Cargar reporte de evaluación por preguntas
        const data = await miPromedioInstructor(idInstructor);
        setReporte(data);
      } catch (err) {
        console.error("Error al cargar el rendimiento:", err);
        setError("No se pudo obtener la información de desempeño. Inténtalo de nuevo.");
      } finally {
        setCargando(false);
      }
    };

    cargarRendimiento();
  }, [usuario]);

  // Estilos y configuraciones visuales según la nota / porcentaje
  const obtenerConfiguracionEstado = (porcentaje, nota) => {
    // Si nota o porcentaje están entre 4.0 a 5.0 (80% a 100%)
    if (porcentaje >= 80 || (nota && nota >= 4.0)) {
      return {
        color: "#39a900",
        fondo: "#d1fae5",
        textoColor: "#065f46",
        borde: "#a7f3d0",
        icono: "bi-check-circle-fill",
        mensajeDefecto: "¡Excelente desempeño! Cumples satisfactoriamente con este criterio.",
      };
    } 
    // Si nota o porcentaje está entre 3.0 a 3.99 (60% a 79%)
    else if (porcentaje >= 60 || (nota && nota >= 3.0)) {
      return {
        color: "#f59e0b",
        fondo: "#fef3c7",
        textoColor: "#92400e",
        borde: "#fde68a",
        icono: "bi-exclamation-triangle-fill",
        mensajeDefecto: "Atención: Tienes oportunidad de mejora en este aspecto evaluado (Nota entre 3.0 y 3.9).",
      };
    } 
    // Si la nota o porcentaje es menor a 3.0 / 60%
    else {
      return {
        color: "#ef4444",
        fondo: "#fee2e2",
        textoColor: "#991b1b",
        borde: "#fecaca",
        icono: "bi-x-circle-fill",
        mensajeDefecto: "Alerta de Desempeño: Se detectan fallas recurrentes en este ítem (por ejemplo, impuntualidad o incumplimiento).",
      };
    }
  };

  if (cargando) {
    return (
      <div className="home-cargando" style={{ minHeight: "350px", textAlign: "center", paddingTop: "50px" }}>
        <div className="spinner-home"></div>
        <p style={{ marginTop: "16px", color: "#6b7280" }}>Cargando tu reporte de promedio y rendimiento...</p>
      </div>
    );
  }

  const preguntas = reporte?.preguntas || [];
  const promedioGeneral = reporte?.promedio_general || 0;
  const porcentajeGeneral = reporte?.porcentaje_general || Math.round((promedioGeneral / 5) * 100);

  return (
    <div className="home-page" style={{ maxWidth: "900px", margin: "0 auto", padding: "20px" }}>
      {/* ── Encabezado ── */}
      <div className="home-header" style={{ marginBottom: "20px" }}>
        <div>
          <h1 style={{ fontSize: "1.8rem", color: "#111827", marginBottom: "6px" }}>
            <i className="bi bi-graph-up-arrow" style={{ color: "#39a900" }}></i> Mi Promedio y Rendimiento
          </h1>
          <p style={{ color: "#6b7280" }}>
            Consulta las calificaciones otorgadas por las fichas de aprendices y detecta en qué aspectos destacar o mejorar.
          </p>
        </div>
      </div>

      {error && (
        <div
          style={{
            padding: "14px 18px",
            borderRadius: "8px",
            backgroundColor: "#fee2e2",
            color: "#991b1b",
            border: "1px solid #fecaca",
            marginBottom: "20px",
          }}
        >
          <i className="bi bi-exclamation-circle-fill"></i> {error}
        </div>
      )}

      {/* ── Resumen de Promedio General ── */}
      <div
        className="home-card"
        style={{
          marginBottom: "24px",
          background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
          color: "#fff",
          padding: "24px",
          borderRadius: "12px",
          boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
        }}
      >
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "20px" }}>
          <div>
            <span style={{ fontSize: "0.85rem", textTransform: "uppercase", tracking: "1px", color: "#94a3b8", fontWeight: 600 }}>
              Promedio Cumplimiento General
            </span>
            <h2 style={{ fontSize: "2.5rem", margin: "8px 0 0", color: "#ffffff", fontWeight: 800 }}>
              {promedioGeneral ? promedioGeneral.toFixed(1) : "0.0"} <span style={{ fontSize: "1.2rem", color: "#94a3b8" }}>/ 5.0</span>
            </h2>
            <p style={{ margin: "4px 0 0", color: "#cbd5e1", fontSize: "0.95rem" }}>
              Porcentaje global de satisfacción: <strong>{porcentajeGeneral}%</strong>
            </p>
          </div>

          <div
            style={{
              width: "100px",
              height: "100px",
              borderRadius: "50%",
              border: `6px solid ${porcentajeGeneral >= 80 ? "#39a900" : porcentajeGeneral >= 60 ? "#f59e0b" : "#ef4444"}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexDirection: "column",
              background: "rgba(255, 255, 255, 0.05)",
            }}
          >
            <span style={{ fontSize: "1.4rem", fontWeight: 800, color: "#fff" }}>{porcentajeGeneral}%</span>
            <small style={{ fontSize: "0.65rem", color: "#94a3b8" }}>Efectividad</small>
          </div>
        </div>
      </div>

      {/* ── Desglose por Pregunta ── */}
      <div className="home-card" style={{ background: "#fff", borderRadius: "12px", padding: "20px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        <h3 style={{ fontSize: "1.2rem", color: "#1f2937", marginBottom: "16px", borderBottom: "2px solid #f3f4f6", paddingBottom: "10px" }}>
          <i className="bi bi-list-stars" style={{ color: "#39a900" }}></i> Rendimiento por Criterios / Preguntas
        </h3>

        {preguntas.length === 0 ? (
          <div style={{ textAlign: "center", padding: "30px", color: "#6b7280" }}>
            <i className="bi bi-journal-x" style={{ fontSize: "2.5rem" }}></i>
            <p style={{ marginTop: "10px" }}>Aún no se han consolidado respuestas de evaluación para tu usuario.</p>
          </div>
        ) : (
          preguntas.map((item, index) => {
            const porc = item.porcentaje ?? Math.round(((item.nota || 0) / 5) * 100);
            const nota = item.nota || (porc / 100) * 5;
            const config = obtenerConfiguracionEstado(porc, nota);

            return (
              <div
                key={item.id_pregunta || index}
                style={{
                  marginBottom: "20px",
                  padding: "16px",
                  borderRadius: "10px",
                  border: `1px solid ${config.borde}`,
                  backgroundColor: "#fff",
                }}
              >
                {/* Pregunta y Nota */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "12px", marginBottom: "8px" }}>
                  <span style={{ fontWeight: 700, color: "#374151", fontSize: "0.95rem" }}>
                    {index + 1}. {item.pregunta || item.texto_pregunta}
                  </span>
                  <span
                    style={{
                      padding: "4px 10px",
                      borderRadius: "20px",
                      fontSize: "0.85rem",
                      fontWeight: 700,
                      backgroundColor: config.fondo,
                      color: config.textoColor,
                      whiteSpace: "nowrap",
                    }}
                  >
                    {porc}% ({nota.toFixed(1)})
                  </span>
                </div>

                {/* Barra de Progreso */}
                <div style={{ height: "10px", backgroundColor: "#e5e7eb", borderRadius: "5px", overflow: "hidden", marginBottom: "10px" }}>
                  <div
                    style={{
                      height: "100%",
                      width: `${Math.min(porc, 100)}%`,
                      backgroundColor: config.color,
                      borderRadius: "5px",
                      transition: "width 0.4s ease-in-out",
                    }}
                  />
                </div>

                {/* Fichas que evaluaron esta pregunta */}
                <div style={{ fontSize: "0.82rem", color: "#6b7280", marginBottom: "8px" }}>
                  <strong>Fichas evaluadoras: </strong>
                  {item.fichas && item.fichas.length > 0 ? (
                    item.fichas.map((f, i) => (
                      <span key={i} style={{ background: "#f3f4f6", padding: "2px 8px", borderRadius: "4px", marginRight: "4px" }}>
                        Ficha {f}
                      </span>
                    ))
                  ) : (
                    <span>Evaluación general SENA</span>
                  )}
                </div>

                {/* Recomendación / Advertencia según el desempeño */}
                <div
                  style={{
                    padding: "8px 12px",
                    borderRadius: "6px",
                    backgroundColor: config.fondo,
                    color: config.textoColor,
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <i className={`bi ${config.icono}`}></i>
                  <span>{item.mensaje || config.mensajeDefecto}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default MiPromedio;