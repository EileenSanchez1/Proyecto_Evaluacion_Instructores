import { useState, useEffect } from "react";
import { obtenerUsuarioSesion } from "../utils/sesion";
import { obtenerInstructor } from "../services/instructorService";
import { reportePreguntasInstructor } from "../services/Reporteservice";
import api from "../api/axiosConfig";
import "../styles/Home.css";

function PerfilInstructor() {
  const usuario = obtenerUsuarioSesion();
  const [instructor, setInstructor] = useState(null);
  const [detallePreguntas, setDetallePreguntas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [cargandoPreguntas, setCargandoPreguntas] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [mostrarPromedio, setMostrarPromedio] = useState(false);

  // Cargar datos del instructor
  useEffect(() => {
    const cargarDatos = async () => {
      const idInstructor = usuario?.id_instructor;
      if (idInstructor) {
        try {
          const data = await obtenerInstructor(idInstructor);
          setInstructor(data);
        } catch (err) {
          console.error(err);
          setEsError(true);
          setMensaje("No se pudo cargar la información del perfil.");
        }
      } else {
        setEsError(true);
        setMensaje("No se encontró sesión de instructor activa.");
      }
      setCargando(false);
    };
    cargarDatos();
  }, [usuario]);

  // Cargar reporte de desempeño por preguntas
  const cargarPromedioPreguntas = async () => {
    const idInstructor = usuario?.id_instructor;
    if (!idInstructor) return;

    try {
      setCargandoPreguntas(true);
      const data = await reportePreguntasInstructor(idInstructor, {});
      setDetallePreguntas(data.preguntas || []);
      setMostrarPromedio(true);
    } catch (err) {
      console.error(err);
      setEsError(true);
      setMensaje("No se pudo cargar el reporte de desempeño por preguntas.");
    } finally {
      setCargandoPreguntas(false);
    }
  };

  // Subir / Cambiar Foto de Perfil
  const urlFoto = (ruta) => {
    if (!ruta) return null;
    if (ruta.startsWith("http")) return ruta;
    const base = "http://127.0.0.1:8000";
    return `${base}${ruta}${ruta.includes("?") ? "&" : "?"}t=${Date.now()}`;
  };

  const handleFotoChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setEsError(true);
      setMensaje("Selecciona un archivo de imagen (JPG, PNG o WEBP).");
      return;
    }

    const idInstructor = usuario?.id_instructor;
    if (!idInstructor) {
      setEsError(true);
      setMensaje("Sesión de instructor no válida.");
      return;
    }

    const formData = new FormData();
    formData.append("foto", file);

    try {
      setCargando(true);
      setMensaje("");
      const response = await api.post(
        `/instructores/${idInstructor}/foto`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      const actualizado = response.data;
      setInstructor(actualizado);

      // Actualizar sesión local para que navbar y demás vean la nueva foto
      try {
        const raw = localStorage.getItem("usuario");
        const u = raw ? JSON.parse(raw) : {};
        u.foto = actualizado.foto;
        localStorage.setItem("usuario", JSON.stringify(u));
      } catch {
        /* ignore */
      }

      setEsError(false);
      setMensaje("Foto de perfil actualizada. Admin y aprendices verán el cambio al recargar la lista de instructores.");
    } catch (err) {
      console.error(err);
      setEsError(true);
      setMensaje(err.response?.data?.detail || "No se pudo actualizar la foto de perfil.");
    } finally {
      setCargando(false);
      // limpiar input para permitir volver a elegir el mismo archivo
      e.target.value = "";
    }
  };

  if (cargando) {
    return (
      <div className="home-cargando" style={{ minHeight: "300px" }}>
        <div className="spinner-home"></div>
        <p>Cargando perfil de instructor...</p>
      </div>
    );
  }

  const coloresDetalle = {
    verde: {
      fondo: "#d1fae5",
      texto: "#065f46",
      borde: "#a7f3d0",
      barra: "linear-gradient(90deg, #39a900, #2d7a4f)",
      mensajeDefecto: "¡Excelente desempeño en este aspecto! Continúa así.",
    },
    amarillo: {
      fondo: "#fef3c7",
      texto: "#92400e",
      borde: "#fde68a",
      barra: "linear-gradient(90deg, #f59e0b, #d97706)",
      mensajeDefecto: "Atención: Tienes margen de mejora en este criterio evaluado.",
    },
    rojo: {
      fondo: "#fee2e2",
      texto: "#991b1b",
      borde: "#fecaca",
      barra: "linear-gradient(90deg, #ef4444, #b91c1c)",
      mensajeDefecto: "Alerta crítica: Se detectan fallas recurrentes en este aspecto.",
    },
  };

  return (
    <div className="home-page" style={{ maxWidth: "900px", margin: "0 auto", padding: "20px" }}>
      {/* ── Encabezado ── */}
      <div className="home-header">
        <div>
          <h1>Perfil del Instructor</h1>
          <p>Gestiona tu foto de perfil y consulta tu rendimiento evaluativo por preguntas.</p>
        </div>
      </div>

      {mensaje && (
        <div
          className={`home-alerta ${esError ? "home-alerta-error" : ""}`}
          style={{
            marginBottom: "20px",
            padding: "12px 16px",
            borderRadius: "8px",
            background: esError ? "#fee2e2" : "#d1fae5",
            color: esError ? "#991b1b" : "#065f46",
            border: `1px solid ${esError ? "#fecaca" : "#a7f3d0"}`,
          }}
        >
          <i className={`bi ${esError ? "bi-exclamation-triangle-fill" : "bi-check-circle-fill"}`}></i> {mensaje}
        </div>
      )}

      {/* ── Tarjeta de Datos e Información Personal ── */}
      <div className="home-card" style={{ marginBottom: "24px" }}>
        <div className="home-card-header">
          <h3><i className="bi bi-person-badge"></i> Datos Personales</h3>
        </div>
        <div className="home-card-body">
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "24px" }}>
            {/* Foto y botón para cambiarla */}
            <div style={{ textAlign: "center" }}>
              <div
                style={{
                  width: "110px",
                  height: "110px",
                  borderRadius: "50%",
                  overflow: "hidden",
                  border: "3px solid #39a900",
                  margin: "0 auto 12px",
                  background: "#f3f4f6",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {instructor?.foto ? (
                  <img
                    src={urlFoto(instructor.foto)}
                    alt="Foto actual del instructor"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                ) : (
                  <i className="bi bi-person-fill" style={{ fontSize: "3.5rem", color: "#9ca3af" }}></i>
                )}
              </div>
              <label
                className="btn-primario"
                style={{
                  cursor: "pointer",
                  fontSize: "0.82rem",
                  padding: "6px 12px",
                  display: "inline-block",
                  borderRadius: "6px",
                  background: "#39a900",
                  color: "#fff",
                }}
              >
                <i className="bi bi-camera"></i> Cambiar Foto
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFotoChange}
                  style={{ display: "none" }}
                />
              </label>
            </div>

            {/* Información del Instructor */}
            <div style={{ flex: 1, minWidth: "250px" }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px" }}>
                <div>
                  <label style={{ fontSize: "0.8rem", color: "#6b7280", fontWeight: 600 }}>Nombre Completo</label>
                  <p style={{ margin: "4px 0", fontSize: "1rem", fontWeight: 700, color: "#1f2937" }}>
                    {instructor?.nombre || usuario?.nombre || "—"} {instructor?.apellido || usuario?.apellido || ""}
                  </p>
                </div>

                <div>
                  <label style={{ fontSize: "0.8rem", color: "#6b7280", fontWeight: 600 }}>Correo Institucional</label>
                  <p style={{ margin: "4px 0", fontSize: "0.95rem", fontWeight: 600, color: "#374151" }}>
                    {instructor?.correo || usuario?.correo || "—"}
                  </p>
                </div>

                <div>
                  <label style={{ fontSize: "0.8rem", color: "#6b7280", fontWeight: 600 }}>Rol en el Sistema</label>
                  <p style={{ margin: "4px 0" }}>
                    <span style={{ background: "#e0e7ff", color: "#3730a3", padding: "4px 10px", borderRadius: "12px", fontSize: "0.8rem", fontWeight: 700 }}>
                      INSTRUCTOR
                    </span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div style={{ marginTop: "24px", borderTop: "1px solid #f3f4f6", paddingTop: "16px", textAlign: "right" }}>
            <button
              onClick={cargarPromedioPreguntas}
              style={{
                padding: "10px 20px",
                borderRadius: "8px",
                background: "#39a900",
                color: "#fff",
                border: "none",
                fontWeight: 600,
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <i className="bi bi-bar-chart-line-fill"></i> Ver Mi Promedio y Rendimiento
            </button>
          </div>
        </div>
      </div>

      {/* ── Detalle de Desempeño por Preguntas ── */}
      {mostrarPromedio && (
        <div className="home-card">
          <div className="home-card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3><i className="bi bi-list-check"></i> Evaluación Detallada por Preguntas</h3>
            <button
              onClick={() => setMostrarPromedio(false)}
              style={{
                background: "transparent",
                border: "1px solid #d1d5db",
                padding: "4px 12px",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "0.82rem",
              }}
            >
              Ocultar
            </button>
          </div>
          <div className="home-card-body">
            {cargandoPreguntas && (
              <div style={{ padding: "20px", textAlign: "center" }}>
                <p>Cargando tus resultados evaluativos...</p>
              </div>
            )}

            {!cargandoPreguntas && detallePreguntas.length === 0 && (
              <div className="home-vacio" style={{ textAlign: "center", padding: "20px" }}>
                <i className="bi bi-inbox" style={{ fontSize: "2rem", color: "#9ca3af" }}></i>
                <p style={{ color: "#6b7280", marginTop: "8px" }}>Aún no se han registrado evaluaciones para tu perfil.</p>
              </div>
            )}

            {!cargandoPreguntas &&
              detallePreguntas.map((p) => {
                const c = coloresDetalle[p.color] || coloresDetalle.verde;
                return (
                  <div key={p.id_pregunta || p.orden} style={{ padding: "16px 0", borderBottom: "1px solid #f3f4f6" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: "10px", marginBottom: "8px" }}>
                      <p style={{ margin: 0, fontWeight: 600, color: "#1f2937", fontSize: "0.92rem" }}>
                        {p.orden}. {p.pregunta}
                      </p>
                      <span
                        style={{
                          padding: "4px 12px",
                          borderRadius: "20px",
                          fontWeight: 700,
                          fontSize: "0.85rem",
                          background: c.fondo,
                          color: c.texto,
                          border: `1px solid ${c.borde}`,
                          whiteSpace: "nowrap",
                        }}
                      >
                        {p.porcentaje}%
                      </span>
                    </div>

                    <div style={{ height: "10px", background: "#e5e7eb", borderRadius: "5px", overflow: "hidden", marginBottom: "8px" }}>
                      <div
                        style={{
                          height: "100%",
                          width: `${Math.min(p.porcentaje, 100)}%`,
                          background: c.barra,
                          borderRadius: "5px",
                          transition: "width 0.6s ease",
                        }}
                      />
                    </div>

                    <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "8px" }}>
                      <small style={{ color: "#6b7280" }}>
                        <strong>Fichas evaluadoras:</strong> {p.fichas && p.fichas.length > 0 ? p.fichas.join(", ") : "Sin información de ficha"}
                      </small>
                    </div>

                    {/* Alerta / Recomendación según la nota o porcentaje */}
                    <p style={{ margin: "8px 0 0", fontSize: "0.85rem", fontWeight: 600, color: c.texto }}>
                      <i className={`bi ${p.color === "verde" ? "bi-check-circle" : p.color === "amarillo" ? "bi-exclamation-circle" : "bi-x-circle"}`}></i>{" "}
                      {p.mensaje || c.mensajeDefecto}
                    </p>
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
}

export default PerfilInstructor;