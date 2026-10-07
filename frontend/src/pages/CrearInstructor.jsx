import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { crearInstructor } from "../services/instructorService";
import { listarResultadosAprendizaje } from "../services/resultadoAprendizajeService";
import "../styles/Instructores.css";

function CrearInstructor() {
  const navigate = useNavigate();

  const [formulario, setFormulario] = useState({
    nombre: "",
    apellido: "",
    correo: "",
    telefono: "",
  });

  const [fotoArchivo, setFotoArchivo] = useState(null);
  const [fotoPreview, setFotoPreview] = useState(null);

  const [resultadosDisponibles, setResultadosDisponibles] = useState([]);
  const [resultadosSeleccionados, setResultadosSeleccionados] = useState([]);

  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    listarResultadosAprendizaje()
      .then((datos) => setResultadosDisponibles(datos.filter((c) => c.estado)))
      .catch((err) => console.error("No se pudieron cargar los resultados de aprendizaje", err));
  }, []);

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario({ ...formulario, [name]: value });
  };

  const manejarFoto = (e) => {
    const archivo = e.target.files[0];
    if (archivo) {
      const tiposValidos = ["image/jpeg", "image/png", "image/gif", "image/webp"];
      if (!tiposValidos.includes(archivo.type)) {
        setError("Formato no valido. Use JPG, PNG, GIF o WEBP.");
        return;
      }
      if (archivo.size > 5 * 1024 * 1024) {
        setError("La imagen no debe superar los 5MB.");
        return;
      }
      setFotoArchivo(archivo);
      setFotoPreview(URL.createObjectURL(archivo));
      setError("");
    }
  };

  const alternarResultado = (idCompetencia) => {
    setResultadosSeleccionados((prev) =>
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

    const correoNorm = formulario.correo.trim().toLowerCase();
    if (!correoNorm.endsWith("@sena.edu.co")) {
      setError("El correo del instructor debe ser institucional (@sena.edu.co).");
      return;
    }

    if (resultadosSeleccionados.length === 0) {
      setError("Selecciona al menos un resultado de aprendizaje.");
      return;
    }

    try {
      setGuardando(true);

      const formData = new FormData();
      formData.append("nombre", formulario.nombre.trim());
      formData.append("apellido", formulario.apellido.trim());
      formData.append("correo", correoNorm);
      formData.append("telefono", String(formulario.telefono).trim());
      formData.append("resultados_aprendizaje", JSON.stringify(resultadosSeleccionados));

      if (fotoArchivo) {
        formData.append("foto", fotoArchivo);
      }

      await crearInstructor(formData);

      navigate("/instructores");
    } catch (err) {
      console.error("Error al crear instructor:", err);
      const respuestaError = err.response?.data?.detail;
      if (Array.isArray(respuestaError)) {
        setError(respuestaError[0]?.msg || "Error de validacion en los datos.");
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
            {fotoPreview ? (
              <img src={fotoPreview} alt="Vista previa" />
            ) : (
              <span className="placeholder">
                <i className="bi bi-camera"></i>
              </span>
            )}
          </div>

          <label className="form-label">
            <i className="bi bi-image"></i> Foto del instructor (opcional)
          </label>
          <input
            type="file"
            name="foto"
            className="form-control-form"
            accept="image/jpeg,image/png,image/gif,image/webp"
            onChange={manejarFoto}
          />
          <small className="text-muted">JPG, PNG, GIF o WEBP. Max 5MB.</small>

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
                placeholder="Ej: Perez"
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
            placeholder="nombre.apellido@sena.edu.co"
            value={formulario.correo}
            onChange={manejarCambio}
            required
          />

          <label className="form-label">
            <i className="bi bi-telephone"></i> Telefono *
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
            <i className="bi bi-book"></i> Resultados de Aprendizaje * (selecciona una o varias)
          </label>
          <div className="checkbox-grupo">
            {resultadosDisponibles.length === 0 && (
              <p className="text-muted">
                No hay resultados de aprendizaje registrados todavía. Crealas primero en
                la seccion de Resultados de Aprendizaje.
              </p>
            )}
            {resultadosDisponibles.map((c) => (
              <label key={c.id_resultado} className="checkbox-item">
                <input
                  type="checkbox"
                  checked={resultadosSeleccionados.includes(c.id_resultado)}
                  onChange={() => alternarResultado(c.id_resultado)}
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