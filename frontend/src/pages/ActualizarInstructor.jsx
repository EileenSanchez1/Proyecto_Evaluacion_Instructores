import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  obtenerInstructor,
  actualizarInstructor,
} from "../services/instructorService";
import { listarResultadosAprendizaje } from "../services/resultadoAprendizajeService";
import "../styles/Instructores.css";
import "../styles/agregar-a-Instructores.css";

function dividirNombreCompleto(completo) {
  const partes = (completo || "").trim().split(/\s+/).filter(Boolean);
  if (partes.length === 0) return { nombre: "", apellido: "" };
  if (partes.length === 1) return { nombre: partes[0], apellido: "-" };
  if (partes.length === 2) return { nombre: partes[0], apellido: partes[1] };
  if (partes.length >= 4) {
    return {
      nombre: partes.slice(0, -2).join(" "),
      apellido: partes.slice(-2).join(" "),
    };
  }
  return {
    nombre: partes.slice(0, -1).join(" "),
    apellido: partes[partes.length - 1],
  };
}

function ActualizarInstructor() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [formulario, setFormulario] = useState({
    nombre_completo: "",
    documento: "",
    planta_contrato: "",
    correo_personal: "",
    correo: "",
  });

  const [resultadosDisponibles, setResultadosDisponibles] = useState([]);
  const [resultadosSeleccionados, setResultadosSeleccionados] = useState([]);

  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        const instructor = await obtenerInstructor(id);
        const nombreCompleto = [instructor.nombre, instructor.apellido]
          .filter(Boolean)
          .join(" ")
          .trim();
        setFormulario({
          nombre_completo: nombreCompleto,
          documento: instructor.telefono || "",
          planta_contrato: (instructor.planta_contrato || "").toUpperCase(),
          correo_personal: "",
          correo: instructor.correo || "",
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
      !formulario.nombre_completo.trim() ||
      !formulario.documento.trim() ||
      !formulario.planta_contrato.trim() ||
      !formulario.correo.trim()
    ) {
      setError(
        "Completa: Nombres y Apellidos, Número Documento, Planta/Contrato y Correo @SENA.EDU.CO."
      );
      return;
    }

    const correoNorm = formulario.correo.trim().toLowerCase();
    if (!correoNorm.endsWith("@sena.edu.co")) {
      setError("El correo institucional debe ser @sena.edu.co.");
      return;
    }

    if (resultadosSeleccionados.length === 0) {
      setError("Selecciona al menos un resultado de aprendizaje.");
      return;
    }

    const { nombre, apellido } = dividirNombreCompleto(formulario.nombre_completo);

    try {
      setGuardando(true);

      await actualizarInstructor(id, {
        nombre,
        apellido,
        correo: correoNorm,
        telefono: String(formulario.documento).trim(),
        planta_contrato: formulario.planta_contrato.trim().toUpperCase(),
        resultados_aprendizaje: resultadosSeleccionados,
      });

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
          <p>
            Modifica los campos
          </p>
        </div>

        {error && <div className="form-mensaje-error">{error}</div>}

        <form onSubmit={manejarEnvio}>
          <p
            className="text-muted"
            style={{ marginBottom: "1rem", fontSize: "0.9rem" }}
          >
            <i className="bi bi-info-circle"></i> La foto del instructor solo se
            puede actualizar desde el perfil del propio instructor tras iniciar
            sesión.
          </p>

          <label className="form-label">
            <i className="bi bi-person"></i> Nombres y Apellidos Completos *
          </label>
          <input
            type="text"
            name="nombre_completo"
            className="form-control-form"
            placeholder="Ej: Adriana Maritza Vega Gómez"
            value={formulario.nombre_completo}
            onChange={manejarCambio}
            required
          />

          <label className="form-label" style={{ marginTop: "0.75rem" }}>
            <i className="bi bi-person-vcard"></i> Número Documento *
          </label>
          <input
            type="text"
            name="documento"
            className="form-control-form"
            placeholder="Ej: 52014102"
            value={formulario.documento}
            onChange={manejarCambio}
            required
          />

          <label className="form-label" style={{ marginTop: "0.75rem" }}>
            <i className="bi bi-building"></i> Planta / Contrato *
          </label>
          <select
            name="planta_contrato"
            className="form-control-form"
            value={formulario.planta_contrato}
            onChange={manejarCambio}
            required
          >
            <option value="">Seleccione...</option>
            <option value="PLANTA">PLANTA</option>
            <option value="CONTRATO">CONTRATO</option>
          </select>

          <label className="form-label" style={{ marginTop: "0.75rem" }}>
            <i className="bi bi-envelope"></i> Correo Electrónico Personal
          </label>
          <input
            type="email"
            name="correo_personal"
            className="form-control-form"
            placeholder="ejemplo@gmail.com (opcional, solo referencia)"
            value={formulario.correo_personal}
            onChange={manejarCambio}
          />

          <label className="form-label" style={{ marginTop: "0.75rem" }}>
            <i className="bi bi-envelope-at"></i> Correo Electrónico @SENA.EDU.CO *
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

          <label className="form-label" style={{ marginTop: "1rem" }}>
            <i className="bi bi-book"></i> Resultados de Aprendizaje * (selecciona
            una o varias)
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
