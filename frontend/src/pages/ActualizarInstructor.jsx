import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  obtenerInstructor,
  actualizarInstructor,
} from "../services/instructorService";
import { listarResultadosAprendizaje } from "../services/resultadoAprendizajeService";
import "../styles/Instructores.css";
import "../styles/agregar-a-Instructores.css";

function ActualizarInstructor() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [formulario, setFormulario] = useState({
    nombre: "",
    apellido: "",
    correo: "",
    telefono: "", // almacena el número de documento (mismo campo del Excel)
  });

  const [resultadosDisponibles, setResultadosDisponibles] = useState([]);
  const [resultadosSeleccionados, setResultadosSeleccionados] = useState([]);

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
        if (instructor.resultados_aprendizaje) {
          setResultadosSeleccionados(
            instructor.resultados_aprendizaje.map((c) => c.id_resultado)
          );
        }
      } catch (err) {
        console.error("Error al cargar instructor:", err);
        setError("No se pudo cargar la información del instructor.");
      }
    };

    cargarDatos();

    listarResultadosAprendizaje()
      .then((datos) => setResultadosDisponibles(datos.filter((c) => c.estado)))
      .catch((err) =>
        console.error("No se pudieron cargar los resultados de aprendizaje", err)
      );
  }, [id]);

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario({ ...formulario, [name]: value });
  };

  const alternarResultado = (idResultado) => {
    setResultadosSeleccionados((prev) =>
      prev.includes(idResultado)
        ? prev.filter((id) => id !== idResultado)
        : [...prev, idResultado]
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

    if (resultadosSeleccionados.length === 0) {
      setError("Selecciona al menos un resultado de aprendizaje.");
      return;
    }

    try {
      setGuardando(true);

      const formData = new FormData();
      formData.append("nombre", formulario.nombre.trim());
      formData.append("apellido", formulario.apellido.trim());
      formData.append("correo", formulario.correo.trim());
      formData.append("telefono", String(formulario.telefono).trim());
      formData.append(
        "resultados_aprendizaje",
        JSON.stringify(resultadosSeleccionados)
      );
      // Sin foto: la foto solo la gestiona el instructor en su perfil.

      await actualizarInstructor(id, formData);

      navigate("/instructores");
    } catch (err) {
      console.error("Error al actualizar instructor:", err);
      const respuestaError = err.response?.data?.detail;
      if (Array.isArray(respuestaError)) {
        setError(respuestaError[0]?.msg || "Error de validación en los datos.");
      } else if (typeof respuestaError === "string") {
        setError(respuestaError);
      } else {
        setError("No se pudo actualizar el instructor.");
      }
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="pagina-formulario">
      <div className="form-container">
        <div className="form-header">
          <i className="bi bi-pencil-square"></i>
          <h2>Actualizar Instructor</h2>
          <p>Modifica los campos que deseas actualizar. Los datos deben coincidir con el Excel de carga.</p>
        </div>

        {error && <div className="form-mensaje-error">{error}</div>}

        <form onSubmit={manejarEnvio}>
          <p className="text-muted" style={{ marginBottom: "1rem", fontSize: "0.9rem" }}>
            <i className="bi bi-info-circle"></i> La foto del instructor solo se puede
            actualizar desde el perfil del propio instructor tras iniciar sesión.
          </p>

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
            <i className="bi bi-person-vcard"></i> N° Documento *
          </label>
          <input
            type="text"
            name="telefono"
            className="form-control-form"
            placeholder="Ej: 52014102"
            value={formulario.telefono}
            onChange={manejarCambio}
            required
          />
          <small className="text-muted">
            Número de documento de identidad (el mismo del Excel de carga). No es teléfono.
          </small>

          <label className="form-label" style={{ marginTop: "1rem" }}>
            <i className="bi bi-book"></i> Resultados de Aprendizaje * (selecciona una o varias)
          </label>
          <div className="checkbox-grupo">
            {resultadosDisponibles.length === 0 && (
              <p className="text-muted">
                No hay resultados de aprendizaje registrados todavía.
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
              <button
                type="submit"
                className="btn-submit-form"
                disabled={guardando}
              >
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
