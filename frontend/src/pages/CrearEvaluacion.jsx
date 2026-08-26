import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { crearEvaluacion } from "../services/evaluacionService";
import { listarAprendices } from "../services/Aprendizservice";

function CrearEvaluacion() {
  const navigate = useNavigate();

  const [aprendices, setAprendices] = useState([]);
  const [idAprendiz, setIdAprendiz] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    const cargarAprendices = async () => {
      try {
        setCargando(true);
        const datos = await listarAprendices();
        setAprendices(datos);
      } catch (err) {
        console.error("Error al cargar aprendices:", err);
        setError("No se pudieron cargar los aprendices.");
      } finally {
        setCargando(false);
      }
    };

    cargarAprendices();
  }, []);

  const manejarEnvio = async (e) => {
    e.preventDefault();
    setError("");

    if (!idAprendiz) {
      setError("Debes seleccionar un aprendiz.");
      return;
    }

    try {
      setGuardando(true);
      await crearEvaluacion({ id_aprendiz: Number(idAprendiz) });
      alert("Evaluación creada correctamente.");
      navigate("/evaluaciones");
    } catch (err) {
      console.error("Error al crear evaluación:", err);
      const detalle = err.response?.data?.detail;
      setError(
        typeof detalle === "string"
          ? detalle
          : "No se pudo crear la evaluación."
      );
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div>
      <h1>Crear evaluación</h1>

      {cargando && <p>Cargando aprendices...</p>}
      {error && <p style={{ color: "red", fontWeight: "bold" }}>{error}</p>}

      {!cargando && aprendices.length === 0 && !error && (
        <p>
          No hay aprendices registrados todavía. Debes crear al menos uno
          antes de poder generar una evaluación.
        </p>
      )}

      {!cargando && aprendices.length > 0 && (
        <form onSubmit={manejarEnvio}>
          <div>
            <label>Aprendiz *</label>
            <br />
            <select
              value={idAprendiz}
              onChange={(e) => setIdAprendiz(e.target.value)}
              required
            >
              <option value="">Seleccione un aprendiz...</option>
              {aprendices.map((a) => (
                <option key={a.id_aprendiz} value={a.id_aprendiz}>
                  {a.nombre} {a.apellido}
                </option>
              ))}
            </select>
          </div>

          <button type="submit" disabled={guardando}>
            {guardando ? "Guardando..." : "Crear evaluación"}
          </button>

          <button type="button" onClick={() => navigate("/evaluaciones")}>
            Cancelar
          </button>
        </form>
      )}
    </div>
  );
}

export default CrearEvaluacion;