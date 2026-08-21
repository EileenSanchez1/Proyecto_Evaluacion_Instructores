import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listarInstructores, eliminarInstructor } from "../services/instructorService";

function Instructores() {
  const navigate = useNavigate();
  const [instructores, setInstructores] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargarInstructores = async () => {
    try {
      setCargando(true);
      setError("");
      const datos = await listarInstructores();
      setInstructores(datos);
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar los instructores.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarInstructores();
  }, []);

  const manejarEliminar = async (id) => {
    if (window.confirm("¿Está seguro de eliminar este instructor?")) {
      try {
        await eliminarInstructor(id);
        setInstructores(instructores.filter((inst) => inst.id_instructor !== id));
      } catch (err) {
        console.error(err);
        alert("Error al intentar eliminar el instructor.");
      }
    }
  };

  return (
    <div>
      <h1>Instructores</h1>

      <button onClick={() => navigate("/instructores/crear")}>
        Crear nuevo instructor
      </button>

      {cargando && <p>Cargando instructores...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!cargando && !error && instructores.length === 0 && (
        <p>No hay instructores registrados.</p>
      )}

      {!cargando && instructores.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Apellido</th>
              <th>Correo</th>
              <th>Teléfono</th>
              <th>Competencia</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {instructores.map((ins) => (
              <tr key={ins.id_instructor}>
                <td>{ins.nombre}</td>
                <td>{ins.apellido}</td>
                <td>{ins.correo}</td>
                <td>{ins.telefono}</td>
                <td>{ins.competencia}</td>
                <td>
                  <button onClick={() => navigate(`/instructores/editar/${ins.id_instructor}`)}>
                    Editar
                  </button>
                  <button onClick={() => manejarEliminar(ins.id_instructor)}>
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Instructores;