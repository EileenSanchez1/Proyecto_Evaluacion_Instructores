import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  obtenerInstructor,
  actualizarInstructor,
} from "../services/instructorService";
import { listarCompetencias } from "../services/competenciaService";
import "../styles/Instructores.css";

function ActualizarInstructor() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [formulario, setFormulario] = useState({
    nombre: "",
    apellido: "",
    correo: "",
    telefono: "",
  });

  const [fotoArchivo, setFotoArchivo] = useState(null);
  const [fotoPreview, setFotoPreview] = useState(null);
  const [fotoActual, setFotoActual] = useState(null);

  const [competenciasDisponibles, setCompetenciasDisponibles] = useState([]);
  const [competenciasSeleccionadas, setCompetenciasSeleccionadas] = useState([]);

  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        const instructor = await obtenerInstructor(id);
        setFormulario({
          nombre: instructor.nombre || "",
          apellido: instructor.apellido || "",
          correo: instructor.correo || "",
          telefono: instructor.telefono || "",
        });
        if (instructor.foto) {
          setFotoActual(instructor.foto);
        }
        if (instructor.competencias) {
          setCompetenciasSeleccionadas(
            instructor.competencias.map((c) => c.id_competencia)
          );
        }
      } catch (err) {
        console.error("Error al cargar instructor:", err);
        setError("No se pudo cargar la informacion del instructor.");
      }
    };

    cargarDatos();

    listarCompetencias()
      .then((datos) => setCompetenciasDisponibles(datos.filter((c) => c.estado)))
      .catch((err) => console.error("No se pudieron cargar las competencias", err));
  }, [id]);

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
      setFotoActual(null);
      setError("");
    }
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

      const formData = new FormData();
      formData.append("nombre", formulario.nombre.trim());
      formData.append("apellido", formulario.apellido.trim());
      formData.append("correo", formulario.correo.trim());
      formData.append("telefono", String(formulario.telefono).trim());
      formData.append("competencias", JSON.stringify(competenciasSeleccionadas));

      if (fotoArchivo) {
        formData.append("foto", fotoArchivo);
      }

      await actualizarInstructor(id, formData);

      navigate("/instructores");
    } catch (err) {
      console.error("Error al actualizar instructor:", err);
      const respuestaError = err.response?.data?.detail;
      if (Array.isArray(respuestaError)) {
        setError(respuestaError[0]?.msg || "Error de validacion en los datos.");
      } else if (typeof respuestaError === "string") {
        setError(respuestaError);
      } else {
        setError("No se pudo actualizar el instructor.");
      }
    } finally {
      setGuardando(false);
    }
  };

  const getFotoUrl = (ruta) => {
    if (!ruta) return null;
    if (ruta.startsWith("http")) return ruta;
    return `http://localhost:8000${ruta}`;
  };

  return (
    <div className="pagina-formulario">
      <div className="form-container">
        <div className="form-header">
          <i className="bi bi-pencil-square"></i>
          <h2>Actualizar Instructor</h2>
          <p>Modifica los campos que deseas actualizar</p>
        </div>

        {error && <div className="form-mensaje-error">{error}</div>}

        <form onSubmit={manejarEnvio}>
          <div className="preview-container">
            {fotoPreview ? (
              <img src={fotoPreview} alt="Vista previa" />
            ) : fotoActual ? (
              <img src={getFotoUrl(fotoActual)} alt="Foto actual" />
            ) : (
              <span className="placeholder">
                <i className="bi bi-camera"></i>
              </span>
            )}
          </div>

          <label className="form-label">
            <i className="bi bi-image"></i> Cambiar foto (opcional)
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
            placeholder="correo@ejemplo.com"
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
            <i className="bi bi-book"></i> Competencias * (selecciona una o varias)
          </label>
          <div className="checkbox-grupo">
            {competenciasDisponibles.length === 0 && (
              <p className="text-muted">
                No hay competencias registradas todavia.
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
                {guardando ? "Guardando..." : "Actualizar Instructor"}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ActualizarInstructor;