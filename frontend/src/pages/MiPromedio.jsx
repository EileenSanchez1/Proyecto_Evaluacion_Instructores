import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { obtenerUsuarioSesion } from "../utils/sesion";
import {
  miPromedioInstructor,
  reportePreguntasInstructor,
} from "../services/Reporteservice";
import "../styles/Home.css";

function MiPromedio() {
  const usuario = obtenerUsuarioSesion();
  const [reporte, setReporte] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargarRendimiento = async () => {
      const idInstructor = usuario?.id_instructor;
      if (!idInstructor) {
        setError(
          "No se encontró sesión activa de instructor. Cierra sesión e inicia de nuevo desde «Soy instructor»."
        );
        setCargando(false);
        return;
      }

      try {
        let data = null;
        try {
          data = await miPromedioInstructor(idInstructor);
        } catch (e1) {
          // Fallback al endpoint de admin/detalle
          data = await reportePreguntasInstructor(idInstructor, {});
        }
        setReporte(data);
      } catch (err) {
        console.error("Error al cargar el rendimiento:", err);
        setError(
          err.response?.data?.detail ||
            "No se pudo obtener la información de desempeño. Inténtalo de nuevo."
        );
      } finally {
        setCargando(false);
      }
    };

    cargarRendimiento();
  }, [usuario]);

  const obtenerConfiguracionEstado = (porcentaje, nota) => {
    const n = nota != null ? Number(nota) : null;
    const p = porcentaje != null ? Number(porcentaje) : 0;

    if ((n != null && n >= 4.0) || p >= 80) {
      return {
        color: "#39a900",
        fondo: "#d1fae5",
        textoColor: "#065f46",
        borde: "#a7f3d0",
        icono: "bi-check-circle-fill",
        mensajeDefecto:
          "¡Excelente desempeño! Cumples satisfactoriamente con este criterio.",
      };
    }
    if ((n != null && n >= 3.0) || p >= 60) {
      return {
        color: "#f59e0b",
        fondo: "#fef3c7",
        textoColor: "#92400e",
        borde: "#fde68a",
        icono: "bi-exclamation-triangle-fill",
        mensajeDefecto:
          "Atención: Tienes oportunidad de mejora en este aspecto (nota entre 3.0 y 3.9).",
      };
    }
    return {
      color: "#ef4444",
      fondo: "#fee2e2",
      textoColor: "#991b1b",
      borde: "#fecaca",
      icono: "bi-x-circle-fill",
      mensajeDefecto:
        "Alerta de desempeño: se detectan fallas en este ítem (por ejemplo, impuntualidad o incumplimiento).",
    };
  };

  if (cargando) {
    return (
      <div className="home-page">
        <div className="home-cargando">
          <div className="spinner-home"></div>
          <p>Cargando tu promedio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="home-page">
        <div className="home-alerta home-alerta-error">{error}</div>
        <Link to="/" style={{ color: "#39a900" }}>
          ← Volver al inicio
        </Link>
      </div>
    );
  }

  const preguntas = reporte?.preguntas || [];
  const promedio = reporte?.promedio_general ?? 0;
  const porcentajeG = reporte?.porcentaje_general ?? 0;
  const totalResp = reporte?.total_respuestas ?? 0;
  const fichasAsignadas = reporte?.fichas_asignadas || [];

  return (
    <div className="home-page">
      <div
        style={{
          background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
          color: "#fff",
          padding: "24px",
          borderRadius: "12px",
          boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
          marginBottom: 24,
        }}
      >
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "20px",
          }}
        >
          <div>
            <h1 style={{ margin: "0 0 8px", fontSize: "1.5rem" }}>
              <i className="bi bi-graph-up-arrow"></i> Mi promedio
            </h1>
            <p style={{ margin: 0, opacity: 0.85, fontSize: "0.95rem" }}>
              {reporte?.nombre_instructor ||
                `${usuario?.nombre || ""} ${usuario?.apellido || ""}`.trim() ||
                "Instructor"}{" "}
              — resumen anónimo de las evaluaciones de aprendices
            </p>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "2rem", fontWeight: 800, color: "#39a900" }}>
              {totalResp > 0 ? Number(promedio).toFixed(2) : "—"}
            </div>
            <div style={{ fontSize: "0.85rem", opacity: 0.8 }}>
              {totalResp > 0 ? `${porcentajeG}% de desempeño` : "Sin evaluaciones aún"}
            </div>
          </div>
        </div>
      </div>

      {fichasAsignadas.length > 0 && (
        <div className="home-card" style={{ marginBottom: 20 }}>
          <div className="home-card-header">
            <h3>
              <i className="bi bi-card-list"></i> Fichas asignadas
            </h3>
          </div>
          <div className="home-card-body" style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {fichasAsignadas.map((f, i) => (
              <span
                key={f.id_ficha_instructor || i}
                style={{
                  background: "#f3f4f6",
                  padding: "6px 12px",
                  borderRadius: 8,
                  fontSize: "0.9rem",
                }}
              >
                Ficha {f.numero_ficha || f.id_ficha}
                {f.programa ? ` · ${f.programa}` : ""}
                {f.periodo ? ` · ${f.periodo}` : ""}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="home-card">
        <div className="home-card-header">
          <h3>
            <i className="bi bi-list-check"></i> Desempeño por pregunta
          </h3>
        </div>
        <div className="home-card-body">
          {preguntas.length === 0 ? (
            <div style={{ textAlign: "center", padding: 32, color: "#6b7280" }}>
              <i className="bi bi-inbox" style={{ fontSize: 40 }}></i>
              <p style={{ marginTop: 12 }}>
                Aún no hay respuestas de evaluación asociadas a tu perfil.
              </p>
              <p style={{ fontSize: "0.9rem" }}>
                Cuando los aprendices de tus fichas te evalúen, aquí verás el
                porcentaje por cada pregunta, las fichas que participaron y
                mensajes de felicitación o de mejora.
              </p>
              <Link to="/" style={{ color: "#39a900", fontWeight: 600 }}>
                Volver al inicio
              </Link>
            </div>
          ) : (
            preguntas.map((item) => {
              const nota = Number(item.nota ?? item.promedio ?? 0);
              const porc = Number(item.porcentaje ?? (nota / 5) * 100);
              const config = obtenerConfiguracionEstado(porc, nota);

              return (
                <div
                  key={item.id_pregunta || item.orden}
                  style={{
                    padding: "16px 0",
                    borderBottom: "1px solid #f3f4f6",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 10,
                      marginBottom: 8,
                      flexWrap: "wrap",
                    }}
                  >
                    <p
                      style={{
                        margin: 0,
                        fontWeight: 600,
                        color: "#1f2937",
                        fontSize: "0.95rem",
                      }}
                    >
                      {item.orden != null ? `${item.orden}. ` : ""}
                      {item.pregunta || item.texto_pregunta || "Pregunta"}
                    </p>
                    <span
                      style={{
                        padding: "4px 10px",
                        borderRadius: 20,
                        fontSize: "0.85rem",
                        fontWeight: 700,
                        backgroundColor: config.fondo,
                        color: config.textoColor,
                        whiteSpace: "nowrap",
                      }}
                    >
                      {porc.toFixed(1)}% ({nota.toFixed(1)})
                    </span>
                  </div>

                  <div
                    style={{
                      height: 10,
                      backgroundColor: "#e5e7eb",
                      borderRadius: 5,
                      overflow: "hidden",
                      marginBottom: 10,
                    }}
                  >
                    <div
                      style={{
                        height: "100%",
                        width: `${Math.min(porc, 100)}%`,
                        backgroundColor: config.color,
                        borderRadius: 5,
                        transition: "width 0.4s ease-in-out",
                      }}
                    />
                  </div>

                  <div
                    style={{
                      fontSize: "0.82rem",
                      color: "#6b7280",
                      marginBottom: 8,
                    }}
                  >
                    <strong>Fichas evaluadoras: </strong>
                    {item.fichas && item.fichas.length > 0 ? (
                      item.fichas.map((f, i) => (
                        <span
                          key={i}
                          style={{
                            background: "#f3f4f6",
                            padding: "2px 8px",
                            borderRadius: 4,
                            marginRight: 4,
                          }}
                        >
                          Ficha {f}
                        </span>
                      ))
                    ) : (
                      <span>Sin detalle de ficha</span>
                    )}
                    {item.total_respuestas != null && (
                      <span style={{ marginLeft: 8 }}>
                        · {item.total_respuestas} respuesta(s)
                      </span>
                    )}
                  </div>

                  <div
                    style={{
                      padding: "8px 12px",
                      borderRadius: 6,
                      backgroundColor: config.fondo,
                      color: config.textoColor,
                      fontSize: "0.85rem",
                      fontWeight: 600,
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
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
    </div>
  );
}

export default MiPromedio;
