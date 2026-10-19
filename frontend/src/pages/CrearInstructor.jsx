import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { crearInstructor } from "../services/instructorService";
import { listarResultadosAprendizaje } from "../services/resultadoAprendizajeService";
import "../styles/Instructores.css";

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

function CrearInstructor() {
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
    listarResultadosAprendizaje()
      .then((datos) => setResultadosDisponibles(datos.filter((c) => c.estado)))
      .catch((err) =>
        console.error("No se pudieron cargar los resultados de aprendizaje", err)
      );
  }, []);

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

      const formData = new FormData();
      formData.append("nombre", nombre);
      formData.append("apellido", apellido);
      formData.append("correo", correoNorm);
      formData.append("telefono", String(formulario.documento).trim());
      formData.append(
        "planta_contrato",
        formulario.planta_contrato.trim().toUpperCase()
      );
      formData.append(
        "resultados_aprendizaje",
        JSON.stringify(resultadosSeleccionados)
      );

      await crearInstructor(formData);

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
          <p>Completa los campos</p>
        </div>

        {error && <div className="form-mensaje-error">{error}</div>}

        <form onSubmit={manejarEnvio}>
          <p
            className="text-muted"
            style={{ marginBottom: "1rem", fontSize: "0.9rem" }}
          >
            <i className="bi bi-info-circle"></i> Al crear el instructor se enviará
            un correo a su cuenta institucional con una <strong>contraseña temporal</strong>.
            Podrá cambiarla al ingresar y actualizar su foto desde el perfil.
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
            <i className="bi bi-envelope"></i> Correo Electrónico Personal(Opcional)
          </label>
          <input
            type="email"
            name="correo_personal"
            className="form-control-form"
            placeholder="ejemplo@gmail.com"
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
          <small className="text-muted">
            Se le enviará la contraseña temporal para iniciar sesion
          </small>

          <label className="form-label" style={{ marginTop: "1rem" }}>
            <i className="bi bi-book"></i> Resultados de Aprendizaje * (selecciona
            una o varias)
          </label>
          <div className="checkbox-grupo">
            {resultadosDisponibles.length === 0 && (
              <p className="text-muted">
                No hay resultados de aprendizaje registrados. Cárgalos o créalos
                primero en la sección de Resultados de Aprendizaje (los del Excel
                de resultados).
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
