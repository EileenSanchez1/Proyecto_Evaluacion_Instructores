import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  obtenerInstructor,
  eliminarInstructor,
} from "../services/instructorService";

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

      alert("Instructor eliminado correctamente.");

      navigate("/instructores");
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
        "No se pudo eliminar el instructor."
      );
    } finally {
      setEliminando(false);
    }
  };

  if (cargando) {
    return <p>Cargando instructor...</p>;
  }

  if (!instructor) {
    return (
      <div>
        <p>{error || "Instructor no encontrado."}</p>

        <button onClick={() => navigate("/instructores")}>
          Volver
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1>Eliminar instructor</h1>

      <p>
        ¿Está seguro de eliminar este instructor?
      </p>

      <p>
        <strong>
          {instructor.nombre} {instructor.apellido}
        </strong>
      </p>

      <p>{instructor.correo}</p>

      {error && <p>{error}</p>}

      <button
        onClick={confirmarEliminacion}
        disabled={eliminando}
      >
        {eliminando ? "Eliminando..." : "Sí, eliminar"}
      </button>

      <button
        onClick={() => navigate("/instructores")}
        disabled={eliminando}
      >
        Cancelar
      </button>
    </div>
  );
}

export default EliminarInstructor;