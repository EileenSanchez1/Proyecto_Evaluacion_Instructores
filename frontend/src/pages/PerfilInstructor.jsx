import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { obtenerUsuarioSesion } from "../utils/sesion";
import { obtenerInstructor } from "../services/instructorService";
import api from "../api/axiosConfig";
import "../styles/Home.css";

/**
 * Perfil del instructor.
 * Solo permite ver datos personales, editar foto y cambiar contraseña.
 * No muestra promedios, calificaciones ni resultados de evaluación.
 */
function PerfilInstructor() {
  const usuario = obtenerUsuarioSesion();
  const [instructor, setInstructor] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);

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
    if (!idInstructor) return;

    const formData = new FormData();
    formData.append("foto", file);

    try {
      setCargando(true);
      const { data: actualizado } = await api.post(
        `/instructores/${idInstructor}/foto`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setInstructor(actualizado);

      try {
        const raw = localStorage.getItem("usuario");
        const u = raw ? JSON.parse(raw) : {};
        u.foto = actualizado.foto;
        localStorage.setItem("usuario", JSON.stringify(u));
      } catch {
        /* ignore */
      }

      setEsError(false);
      setMensaje("Foto de perfil actualizada correctamente.");
    } catch (err) {
      console.error(err);
      setEsError(true);
      setMensaje(
        err.response?.data?.detail || "No se pudo actualizar la foto de perfil."
      );
    } finally {
      setCargando(false);
      e.target.value = "";
    }
  };

  if (cargando && !instructor) {
    return (
      <div className="home-cargando" style={{ minHeight: "300px" }}>
        <div className="spinner-home"></div>
        <p>Cargando perfil de instructor...</p>
      </div>
    );
  }

  const vinculacion = (instructor?.planta_contrato || "").toUpperCase();
  const etiquetaVinculacion =
    vinculacion === "PLANTA"
      ? "PLANTA"
      : vinculacion === "CONTRATO"
        ? "CONTRATO"
        : vinculacion || "—";

  return (
    <div className="home-page" style={{ maxWidth: "900px", margin: "0 auto", padding: "20px" }}>
      <div className="home-header">
        <div>
          <h1>Perfil del Instructor</h1>
          <p>Gestiona tu foto de perfil y consulta tus datos institucionales.</p>
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
          <i
            className={`bi ${esError ? "bi-exclamation-triangle-fill" : "bi-check-circle-fill"}`}
          ></i>{" "}
          {mensaje}
        </div>
      )}

      <div className="home-card" style={{ marginBottom: "24px" }}>
        <div className="home-card-header">
          <h3>
            <i className="bi bi-person-badge"></i> Datos Personales
          </h3>
        </div>
        <div className="home-card-body">
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              alignItems: "center",
              gap: "24px",
            }}
          >
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
                    alt="Foto del instructor"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                ) : (
                  <i
                    className="bi bi-person-fill"
                    style={{ fontSize: "3.5rem", color: "#9ca3af" }}
                  ></i>
                )}
              </div>
              <label
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
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleFotoChange}
                  style={{ display: "none" }}
                />
              </label>
            </div>

            <div style={{ flex: 1, minWidth: "250px" }}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                  gap: "16px",
                }}
              >
                <div>
                  <label
                    style={{ fontSize: "0.8rem", color: "#6b7280", fontWeight: 600 }}
                  >
                    Nombre Completo
                  </label>
                  <p style={{ margin: "4px 0 0", fontWeight: 600, color: "#1f2937" }}>
                    {instructor?.nombre || usuario?.nombre || "—"}{" "}
                    {instructor?.apellido || usuario?.apellido || ""}
                  </p>
                </div>
                <div>
                  <label
                    style={{ fontSize: "0.8rem", color: "#6b7280", fontWeight: 600 }}
                  >
                    Correo Institucional
                  </label>
                  <p style={{ margin: "4px 0 0", fontWeight: 600, color: "#1f2937" }}>
                    {instructor?.correo || usuario?.correo || "—"}
                  </p>
                </div>
                <div>
                  <label
                    style={{ fontSize: "0.8rem", color: "#6b7280", fontWeight: 600 }}
                  >
                    Vinculación
                  </label>
                  <p style={{ margin: "4px 0 0" }}>
                    <span
                      style={{
                        background:
                          etiquetaVinculacion === "PLANTA"
                            ? "#dbeafe"
                            : etiquetaVinculacion === "CONTRATO"
                              ? "#fef3c7"
                              : "#f3f4f6",
                        color:
                          etiquetaVinculacion === "PLANTA"
                            ? "#1e40af"
                            : etiquetaVinculacion === "CONTRATO"
                              ? "#92400e"
                              : "#6b7280",
                        padding: "4px 10px",
                        borderRadius: "12px",
                        fontSize: "0.8rem",
                        fontWeight: 700,
                      }}
                    >
                      {etiquetaVinculacion}
                    </span>
                  </p>
                </div>
                <div>
                  <label
                    style={{ fontSize: "0.8rem", color: "#6b7280", fontWeight: 600 }}
                  >
                    Rol en el Sistema
                  </label>
                  <p style={{ margin: "4px 0 0" }}>
                    <span
                      style={{
                        background: "#e0e7ff",
                        color: "#3730a3",
                        padding: "4px 10px",
                        borderRadius: "12px",
                        fontSize: "0.8rem",
                        fontWeight: 700,
                      }}
                    >
                      INSTRUCTOR
                    </span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div
            style={{
              marginTop: "24px",
              borderTop: "1px solid #f3f4f6",
              paddingTop: "16px",
              display: "flex",
              justifyContent: "flex-end",
              gap: "10px",
              flexWrap: "wrap",
            }}
          >
            <Link
              to="/cambiar-contrasena"
              style={{
                padding: "10px 18px",
                borderRadius: "8px",
                background: "#fff",
                color: "#374151",
                border: "1px solid #d1d5db",
                fontWeight: 600,
                textDecoration: "none",
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <i className="bi bi-key"></i> Cambiar contraseña
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PerfilInstructor;
