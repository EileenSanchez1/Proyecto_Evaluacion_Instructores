import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { crearEvaluacion } from "../services/evaluacionServices";
import { listarInstructores } from "../services/instructorService";
import { listarFichas } from "../services/FichaServices";
import { listarAprendices } from "../services/Aprendizservice"; // ← Importar bien

function CrearEvaluacion() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    id_aprendiz: "",
    fecha: "",
    estado: "Pendiente",
  });
  const [aprendices, setAprendices] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargarAprendices = async () => {
      try {
        const data = await listarAprendices();
        setAprendices(data);
      } catch (err) {
        setError("Error al cargar aprendices: " + err.message);
      }
    };
    cargarAprendices();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCargando(true);
    setError("");

    try {
      await crearEvaluacion(formData);
      alert("✅ Evaluación creada exitosamente");
      navigate("/evaluaciones");
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || "Error al crear";
      setError(msg);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div>
      <h2>Crear Evaluación</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Aprendiz a evaluar:</label>
          <select
            name="id_aprendiz"
            value={formData.id_aprendiz}
            onChange={handleChange}
            required
          >
            <option value="">Selecciona un aprendiz...</option>
            {aprendices.map((ap) => (
              <option key={ap.id_aprendiz} value={ap.id_aprendiz}>
                {ap.nombre} {ap.apellido} (Ficha: {ap.id_ficha})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Fecha:</label>
          <input
            type="date"
            name="fecha"
            value={formData.fecha}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Estado:</label>
          <select
            name="estado"
            value={formData.estado}
            onChange={handleChange}
          >
            <option value="Pendiente">Pendiente</option>
            <option value="En progreso">En progreso</option>
            <option value="Evaluada">Evaluada</option>
          </select>
        </div>

        <button type="submit" disabled={cargando}>
          {cargando ? "Creando..." : "Crear Evaluación"}
        </button>
      </form>
    </div>
  );
}

export default CrearEvaluacion;