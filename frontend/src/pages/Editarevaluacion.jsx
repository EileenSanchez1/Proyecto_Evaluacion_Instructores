import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  obtenerEvaluacion,
  actualizarEvaluacion,
} from "../services/evaluacionService";
import { obtenerAprendiz } from "../services/Aprendizservice";

function EditarEvaluacion() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [aprendiz, setAprendiz] = useState(null);
  const [estado, setEstado] = useState("Pendiente");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    const cargar = async () => {
      try {
        setCargando(true);
        setError("");

        const evaluacion = await obtenerEvaluacion(id);
        setEstado(evaluacion.estado);

        const aprendizData = await obtenerAprendiz(evaluacion.id_aprendiz);
        setAprendiz(aprendizData);
      } catch (err) {
        console.error("Error al cargar evaluación:", err);
        setError("No se pudo cargar la evaluación.");
      } finally {
        setCargando(false);
      }
    };

    cargar();
  }, [id]);

  const manejarEnvio = async (e) => {
    e.preventDefault();
    setError("");

    try {
      setGuardando(true);
      await actualizarEvaluacion(id, { estado });
      alert("Evaluación actualizada correctamente.");
      navigate("/evaluaciones");
    } catch (err) {
      console.error("Error al actualizar evaluación:", err);
      const detalle = err.response?.data?.detail;
      setError(
        typeof detalle === "string"
          ? detalle
          : "No se pudo actualizar la evaluación."
      );
    } finally {
      setGuardando(false);
    }
  };

  if (cargando) {
    return <p>Cargando evaluación...</p>;
  }

  return (
    <div>
      <h1>Editar evaluación #{id}</h1>

      {aprendiz && (
        <p>
          <strong>Aprendiz:</strong> {aprendiz.nombre} {aprendiz.apellido}
        </p>
      )}

      {error && <p style={{ color: "red", fontWeight: "bold" }}>{error}</p>}

      <form onSubmit={manejarEnvio}>
        <div>
          <label>Estado *</label>
          <br />
          <select value={estado} onChange={(e) => setEstado(e.target.value)}>
            <option value="Pendiente">Pendiente</option>
            <option value="Evaluado">Evaluado</option>
          </select>
        </div>

        <p>
          <em>
            Nota: los datos de la evaluación (aprendiz, preguntas y
            respuestas) solo se editan desde la pantalla de "Ver detalles".
            Aquí solo puedes cambiar el estado manualmente.
          </em>
        </p>

        <button type="submit" disabled={guardando}>
          {guardando ? "Guardando..." : "Guardar cambios"}
        </button>

        <button type="button" onClick={() => navigate("/evaluaciones")}>
          Cancelar
        </button>
      </form>
    </div>
  );
}

export default EditarEvaluacion;