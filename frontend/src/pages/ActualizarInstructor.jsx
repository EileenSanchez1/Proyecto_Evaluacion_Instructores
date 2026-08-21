import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  obtenerInstructor,
  actualizarInstructor,
} from "../services/instructorService";

function ActualizarInstructor() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [formulario, setFormulario] = useState({
    nombre: "",
    apellido: "",
    correo: "",
    telefono: "",
    competencia: "",
    foto: "",
  });

  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const cargarInstructor = async () => {
      try {
        const datos = await obtenerInstructor(id);

        setFormulario({
          nombre: datos.nombre || "",
          apellido: datos.apellido || "",
          correo: datos.correo || "",
          telefono: datos.telefono || "",
          competencia: datos.competencia || "",
          foto: datos.foto || "",
        });
      } catch (error) {
        console.error(error);
        setError("No se pudo cargar el instructor.");
      } finally {
        setCargando(false);
      }
    };

    cargarInstructor();
  }, [id]);

  const handleChange = (e) => {
    setFormulario({
      ...formulario,
      [e.target.name]: e.target.value,
    });
  };

  const validarFormulario = () => {
    if (
      !formulario.nombre.trim() ||
      !formulario.apellido.trim() ||
      !formulario.correo.trim() ||
      !formulario.telefono.trim() ||
      !formulario.competencia.trim()
    ) {
      return "Todos los campos obligatorios deben estar completos.";
    }

    const correoValido =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formulario.correo);

    if (!correoValido) {
      return "Ingrese un correo electrónico válido.";
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
    return <p>Cargando instructor...</p>;
  }

  return (
    <div>
      <h1>Actualizar Instructor</h1>

      {mensaje && <p>{mensaje}</p>}
      {error && <p>{error}</p>}

      <form onSubmit={handleSubmit}>
        <div>
          <label>Nombre *</label>
          <input
            type="text"
            name="nombre"
            value={formulario.nombre}
            onChange={handleChange}
          />
        </div>

        <div>
          <label>Apellido *</label>
          <input
            type="text"
            name="apellido"
            value={formulario.apellido}
            onChange={handleChange}
          />
        </div>

        <div>
          <label>Correo *</label>
          <input
            type="email"
            name="correo"
            value={formulario.correo}
            onChange={handleChange}
          />
        </div>

        <div>
          <label>Teléfono *</label>
          <input
            type="text"
            name="telefono"
            value={formulario.telefono}
            onChange={handleChange}
          />
        </div>

        <div>
          <label>Competencia *</label>
          <input
            type="text"
            name="competencia"
            value={formulario.competencia}
            onChange={handleChange}
          />
        </div>

        <div>
          <label>Foto</label>
          <input
            type="text"
            name="foto"
            value={formulario.foto}
            onChange={handleChange}
            placeholder="URL de la foto (opcional)"
          />
        </div>

        <button type="submit">
          Guardar cambios
        </button>

        <button
          type="button"
          onClick={() => navigate("/instructores")}
        >
          Cancelar
        </button>
      </form>
    </div>
  );
}

export default ActualizarInstructor;