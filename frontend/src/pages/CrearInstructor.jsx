import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { crearInstructor } from "../services/instructorService";

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

      alert("Instructor creado correctamente.");
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
    <div>
      <h1>Crear instructor</h1>

      {error && <p style={{ color: "red", fontWeight: "bold" }}>{error}</p>}

      <form onSubmit={manejarEnvio}>
        <div>
          <label>Nombre *</label>
          <input
            type="text"
            name="nombre"
            value={formulario.nombre}
            onChange={manejarCambio}
            required
          />
        </div>

        <div>
          <label>Apellido *</label>
          <input
            type="text"
            name="apellido"
            value={formulario.apellido}
            onChange={manejarCambio}
            required
          />
        </div>

        <div>
          <label>Correo *</label>
          <input
            type="email"
            name="correo"
            value={formulario.correo}
            onChange={manejarCambio}
            required
          />
        </div>

        <div>
          <label>Teléfono *</label>
          <input
            type="text"
            name="telefono"
            value={formulario.telefono}
            onChange={manejarCambio}
            required
          />
        </div>

        <div>
          <label>Competencia *</label>
          <input
            type="text"
            name="competencia"
            value={formulario.competencia}
            onChange={manejarCambio}
            required
          />
        </div>

        <div>
          <label>Foto</label>
          <input
            type="text"
            name="foto"
            value={formulario.foto}
            onChange={manejarCambio}
            placeholder="URL de la foto (opcional)"
          />
        </div>

        <button type="submit" disabled={guardando}>
          {guardando ? "Guardando..." : "Crear instructor"}
        </button>

        <button
          type="button"
          onClick={() => navigate("/instructores")}
        >
          Cancelar
        </button>
      </form>
    </div>
  );
}

export default CrearInstructor;