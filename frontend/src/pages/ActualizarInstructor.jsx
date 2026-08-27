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
    foto: "",
  });

  const [competenciasDisponibles, setCompetenciasDisponibles] = useState([]);
  const [competenciasSeleccionadas, setCompetenciasSeleccionadas] = useState([]);

  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        const [datos, competencias] = await Promise.all([
          obtenerInstructor(id),
          listarCompetencias(),
        ]);

        setFormulario({
          nombre: datos.nombre || "",
          apellido: datos.apellido || "",
          correo: datos.correo || "",
          telefono: datos.telefono || "",
          foto: datos.foto || "",
        });

        setCompetenciasDisponibles(competencias.filter((c) => c.estado));
        setCompetenciasSeleccionadas(
          (datos.competencias || []).map((c) => c.id_competencia)
        );
      } catch (error) {
        console.error(error);
        setError("No se pudo cargar el instructor.");
      } finally {
        setCargando(false);
      }
    };

    cargarDatos();
  }, [id]);

  const handleChange = (e) => {
    setFormulario({
      ...formulario,
      [e.target.name]: e.target.value,
    });
  };

  const alternarCompetencia = (idCompetencia) => {
    setCompetenciasSeleccionadas((prev) =>
      prev.includes(idCompetencia)
        ? prev.filter((cid) => cid !== idCompetencia)
        : [...prev, idCompetencia]
    );
  };

  const validarFormulario = () => {
    if (
      !formulario.nombre.trim() ||
      !formulario.apellido.trim() ||
      !formulario.correo.trim() ||
      !formulario.telefono.trim()
    ) {
      return "Todos los campos obligatorios deben estar completos.";
    }

    const correoValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formulario.correo);

    if (!correoValido) {
      return "Ingrese un correo electrónico válido.";
    }

    if (competenciasSeleccionadas.length === 0) {
      return "Selecciona al menos una competencia.";
    }

    return "";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setMensaje("");

    const errorValidacion = validarFormulario();

    if (errorValidacion) {
      setError(errorValidacion);
      return;
    }

    try {
      await actualizarInstructor(id, {
        ...formulario,
        foto: formulario.foto || null,
        competencias: competenciasSeleccionadas,
      });

      setMensaje("Instructor actualizado correctamente.");

      setTimeout(() => {
        navigate("/instructores");
      }, 1000);
    } catch (error) {
      console.error(error);

      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError("No se pudo actualizar el instructor.");
      }
    }
  };

  if (cargando) {
    return (
      <div className="pagina-formulario">
        <p className="text-muted">Cargando instructor...</p>
      </div>
    );
  }

  return (
    <div className="pagina-formulario">
      <div className="form-container">
        <div className="form-header">
          <i className="bi bi-pencil-square" style={{ color: "#198754" }}></i>
          <h2>Actualizar Instructor</h2>
          <p>
            Editando a <strong>{formulario.nombre} {formulario.apellido}</strong>
          </p>
        </div>

        {mensaje && <div className="form-mensaje-exito">{mensaje}</div>}
        {error && <div className="form-mensaje-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="preview-container">
            {formulario.foto ? (
              <img src={formulario.foto} alt="Foto del instructor" />
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
            onChange={handleChange}
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
                value={formulario.nombre}
                onChange={handleChange}
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
                value={formulario.apellido}
                onChange={handleChange}
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
            value={formulario.correo}
            onChange={handleChange}
          />

          <label className="form-label">
            <i className="bi bi-telephone"></i> Teléfono *
          </label>
          <input
            type="text"
            name="telefono"
            className="form-control-form"
            value={formulario.telefono}
            onChange={handleChange}
          />

          <label className="form-label">
            <i className="bi bi-book"></i> Competencias * (selecciona una o varias)
          </label>
          <div className="checkbox-grupo">
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
              <button type="submit" className="btn-submit-form">
                <i className="bi bi-check-circle"></i> Guardar Cambios
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ActualizarInstructor;
