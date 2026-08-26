import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  obtenerInstructor,
  eliminarInstructor,
} from "../services/instructorService";
import "../styles/Instructores.css";

function EliminarInstructor() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [instructor, setInstructor] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [eliminando, setEliminando] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargarInstructor = async () => {
      try {
        const datos = await obtenerInstructor(id);
        setInstructor(datos);
      } catch (error) {
        console.error(error);
        setError("No se pudo encontrar el instructor.");
      } finally {
        setCargando(false);
      }
    };

    cargarInstructor();
  }, [id]);

  const confirmarEliminacion = async () => {
    try {
      setEliminando(true);
      setError("");

      await eliminarInstructor(id);

      navigate("/instructores");
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail || "No se pudo eliminar el instructor."
      );
    } finally {
      setEliminando(false);
    }
  };

  if (cargando) {
    return (
      <div className="pagina-formulario">
        <p className="text-muted">Cargando instructor...</p>
      </div>
    );
  }

  if (!instructor) {
    return (
      <div className="pagina-formulario">
        <div className="form-container tarjeta-confirmar">
          <p className="form-mensaje-error">
            {error || "Instructor no encontrado."}
          </p>
          <button className="btn-cancel-form" onClick={() => navigate("/instructores")}>
            <i className="bi bi-arrow-left"></i> Volver
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="pagina-formulario">
      <div className="encabezado">
        <div>
          <h1 className="titulo-rojo">Eliminar Instructor</h1>
          <p className="subtitulo">Elimina permanentemente un instructor del sistema</p>
        </div>
        <button className="btn-volver" onClick={() => navigate("/instructores")}>
          <i className="bi bi-arrow-left"></i> Volver
        </button>
      </div>

      <div className="form-container tarjeta-confirmar">
        <div className="form-header">
          <i className="bi bi-trash-fill" style={{ color: "#dc3545" }}></i>
          <h2>Confirmar Eliminación</h2>
          <p>Esta acción no se puede deshacer</p>
        </div>

        <div className="perfil">
          {instructor.foto ? (
            <img src={instructor.foto} alt={instructor.nombre} className="foto" />
          ) : (
            <div className="foto-placeholder">
              <i className="bi bi-person-fill"></i>
            </div>
          )}
          <div>
            <h4>
              {instructor.nombre} {instructor.apellido}
            </h4>
            <span className="badge-competencia">{instructor.competencia}</span>
          </div>
        </div>

        <p style={{ textAlign: "center", color: "#6c757d" }}>{instructor.correo}</p>

        <div className="alerta-eliminacion">
          <i className="bi bi-exclamation-triangle-fill"></i>
          <div>
            <strong>Advertencia</strong>
            <p>Esta acción eliminará permanentemente al instructor seleccionado. No se puede deshacer.</p>
          </div>
        </div>

        {error && <div className="form-mensaje-error">{error}</div>}

        <div className="acciones-eliminar">
          <button
            className="btn-cancel-form"
            onClick={() => navigate("/instructores")}
            disabled={eliminando}
          >
            Cancelar
          </button>
          <button
            className="btn-submit-form btn-rojo"
            onClick={confirmarEliminacion}
            disabled={eliminando}
          >
            <i className="bi bi-trash"></i>{" "}
            {eliminando ? "Eliminando..." : "Sí, eliminar"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default EliminarInstructor;
