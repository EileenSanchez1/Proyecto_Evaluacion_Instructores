import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { crearInstructor } from "../services/instructorService";
import "../styles/Instructores.css";

const COMPETENCIAS = [
  "Python",
  "Java",
  "JavaScript",
  "HTML y CSS",
  "Base de Datos",
  "Redes",
  "Seguridad Informática",
  "Desarrollo Web",
  "Análisis de Datos",
];

function CrearInstructor() {
  const navigate = useNavigate();

  const [formulario, setFormulario] = useState({
    nombre: "",
    apellido: "",
    correo: "",
    telefono: "",
    competencia: "",
    foto: "",
  });

  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario({
      ...formulario,
      [name]: value,
    });
  };

  const manejarEnvio = async (e) => {
    e.preventDefault();
    setError("");

    if (
      !formulario.nombre.trim() ||
      !formulario.apellido.trim() ||
      !formulario.correo.trim() ||
      !formulario.telefono.trim() ||
      !formulario.competencia.trim()
    ) {
      setError("Todos los campos obligatorios deben estar completos.");
      return;
    }

    try {
      setGuardando(true);

      // Enviamos el teléfono como string explícito para que Python no falle
      await crearInstructor({
        nombre: formulario.nombre.trim(),
        apellido: formulario.apellido.trim(),
        correo: formulario.correo.trim(),
        telefono: String(formulario.telefono).trim(),
        competencia: formulario.competencia.trim(),
        foto: formulario.foto.trim() || null,
      });

      navigate("/instructores");
    } catch (err) {
      console.error("Error al crear instructor:", err);

      const respuestaError = err.response?.data?.detail;

      if (Array.isArray(respuestaError)) {
        // En caso de que FastAPI retorne array de errores de Pydantic
        setError(respuestaError[0]?.msg || "Error de validación en los datos.");
      } else if (typeof respuestaError === "string") {
        // En caso de error directo del servidor
        setError(respuestaError);
      } else {
        setError("No se pudo crear el instructor (verifica si el correo ya existe).");
      }
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="pagina-formulario">
      <div className="form-container">
        <div className="form-header">
          <i className="bi bi-person-plus-fill"></i>
          <h2>Crear Nuevo Instructor</h2>
          <p>Completa todos los campos para registrar un nuevo instructor</p>
        </div>

        {error && <div className="form-mensaje-error">{error}</div>}

        <form onSubmit={manejarEnvio}>
          <div className="preview-container">
            {formulario.foto ? (
              <img src={formulario.foto} alt="Vista previa" />
            ) : (
              <span className="placeholder">
                <i className="bi bi-camera"></i>
              </span>
            )}
          </div>

          <label className="form-label">
            <i className="bi bi-image"></i> URL de la foto (opcional)
          </label>
          <input
            type="text"
            name="foto"
            className="form-control-form"
            placeholder="https://..."
            value={formulario.foto}
            onChange={manejarCambio}
          />

          <div className="form-row">
            <div>
              <label className="form-label">
                <i className="bi bi-person"></i> Nombre *
              </label>
              <input
                type="text"
                name="nombre"
                className="form-control-form"
                placeholder="Ej: Juan"
                value={formulario.nombre}
                onChange={manejarCambio}
                required
              />
            </div>
            <div>
              <label className="form-label">
                <i className="bi bi-person"></i> Apellido *
              </label>
              <input
                type="text"
                name="apellido"
                className="form-control-form"
                placeholder="Ej: Pérez"
                value={formulario.apellido}
                onChange={manejarCambio}
                required
              />
            </div>
          </div>

          <label className="form-label">
            <i className="bi bi-envelope"></i> Correo *
          </label>
          <input
            type="email"
            name="correo"
            className="form-control-form"
            placeholder="correo@ejemplo.com"
            value={formulario.correo}
            onChange={manejarCambio}
            required
          />

          <label className="form-label">
            <i className="bi bi-telephone"></i> Teléfono *
          </label>
          <input
            type="text"
            name="telefono"
            className="form-control-form"
            placeholder="Ej: 3001234567"
            value={formulario.telefono}
            onChange={manejarCambio}
            required
          />

          <label className="form-label">
            <i className="bi bi-book"></i> Competencia *
          </label>
          <select
            name="competencia"
            className="form-select-form"
            value={formulario.competencia}
            onChange={manejarCambio}
            required
          >
            <option value="" disabled>
              Selecciona una competencia
            </option>
            {COMPETENCIAS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>

          <div className="form-row" style={{ marginTop: "10px" }}>
            <div>
              <button
                type="button"
                className="btn-cancel-form"
                onClick={() => navigate("/instructores")}
              >
                <i className="bi bi-x-circle"></i> Cancelar
              </button>
            </div>
            <div>
              <button type="submit" className="btn-submit-form" disabled={guardando}>
                <i className="bi bi-check-circle"></i>{" "}
                {guardando ? "Guardando..." : "Crear Instructor"}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CrearInstructor;
