import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { crearInstructor } from "../services/instructorService";
import { listarCompetencias } from "../services/competenciaService";
import "../styles/Instructores.css";

function CrearInstructor() {
  const navigate = useNavigate();

  const [formulario, setFormulario] = useState({
    nombre: "",
    apellido: "",
    correo: "",
    telefono: "",
    foto: "",
  });

  const [competenciasDisponibles, setCompetenciasDisponibles] = useState([]);
  const [competenciasSeleccionadas, setCompetenciasSeleccionadas] = useState([]);

  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    listarCompetencias()
      .then((datos) => setCompetenciasDisponibles(datos.filter((c) => c.estado)))
      .catch((err) => console.error("No se pudieron cargar las competencias", err));
  }, []);

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario({
      ...formulario,
      [name]: value,
    });
  };

  const alternarCompetencia = (idCompetencia) => {
    setCompetenciasSeleccionadas((prev) =>
      prev.includes(idCompetencia)
        ? prev.filter((id) => id !== idCompetencia)
        : [...prev, idCompetencia]
    );
  };

  const manejarEnvio = async (e) => {
    e.preventDefault();
    setError("");

    if (
      !formulario.nombre.trim() ||
      !formulario.apellido.trim() ||
      !formulario.correo.trim() ||
      !formulario.telefono.trim()
    ) {
      setError("Todos los campos obligatorios deben estar completos.");
      return;
    }

    if (competenciasSeleccionadas.length === 0) {
      setError("Selecciona al menos una competencia.");
      return;
    }

    try {
      setGuardando(true);

      await crearInstructor({
        nombre: formulario.nombre.trim(),
        apellido: formulario.apellido.trim(),
        correo: formulario.correo.trim(),
        telefono: String(formulario.telefono).trim(),
        foto: formulario.foto.trim() || null,
        competencias: competenciasSeleccionadas,
      });

      navigate("/instructores");
    } catch (err) {
      console.error("Error al crear instructor:", err);

      const respuestaError = err.response?.data?.detail;

      if (Array.isArray(respuestaError)) {
        setError(respuestaError[0]?.msg || "Error de validación en los datos.");
      } else if (typeof respuestaError === "string") {
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
            <i className="bi bi-book"></i> Competencias * (selecciona una o varias)
          </label>
          <div className="checkbox-grupo">
            {competenciasDisponibles.length === 0 && (
              <p className="text-muted">
                No hay competencias registradas todavía. Créalas primero en
                la sección de Competencias.
              </p>
            )}
            {competenciasDisponibles.map((c) => (
              <label key={c.id_competencia} className="checkbox-item">
                <input
                  type="checkbox"
                  checked={competenciasSeleccionadas.includes(c.id_competencia)}
                  onChange={() => alternarCompetencia(c.id_competencia)}
                />
                {c.nombre}
              </label>
            ))}
          </div>

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
