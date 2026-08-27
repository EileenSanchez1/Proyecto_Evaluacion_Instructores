import { useEffect, useState } from "react";
import {
  listarCompetencias,
  crearCompetencia,
  actualizarCompetencia,
  eliminarCompetencia,
} from "../services/competenciaService";
import "../styles/Estructura.css";

const FORMULARIO_VACIO = { nombre: "", descripcion: "", estado: true };

function Competencias() {
  const [competencias, setCompetencias] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [editandoId, setEditandoId] = useState(null);
  const [formulario, setFormulario] = useState(FORMULARIO_VACIO);

  const cargar = async () => {
    try {
      setCargando(true);
      setError("");
      setCompetencias(await listarCompetencias());
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar las competencias.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  const manejarCambio = (e) => {
    const { name, value, type, checked } = e.target;
    setFormulario({
      ...formulario,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const iniciarEdicion = (competencia) => {
    setEditandoId(competencia.id_competencia);
    setFormulario({
      nombre: competencia.nombre,
      descripcion: competencia.descripcion || "",
      estado: competencia.estado,
    });
  };

  const cancelarEdicion = () => {
    setEditandoId(null);
    setFormulario(FORMULARIO_VACIO);
  };

  const manejarEnvio = async (e) => {
    e.preventDefault();
    setError("");

    if (!formulario.nombre.trim()) {
      setError("El nombre de la competencia es obligatorio.");
      return;
    }

    try {
      if (editandoId) {
        await actualizarCompetencia(editandoId, formulario);
      } else {
        await crearCompetencia(formulario);
      }

      cancelarEdicion();
      await cargar();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "No se pudo guardar la competencia.");
    }
  };

  const manejarEliminar = async (id) => {
    if (!window.confirm("¿Eliminar esta competencia?")) return;

    try {
      await eliminarCompetencia(id);
      await cargar();
    } catch (err) {
      console.error(err);
      alert(
        err.response?.data?.detail ||
          "No se pudo eliminar (puede estar asignada a instructores)."
      );
    }
  };

  return (
    <div className="pagina-estructura">
      <div className="encabezado">
        <div>
          <h1 className="titulo">Competencias</h1>
          <p className="subtitulo">
            Gestiona las competencias que se pueden asignar a los instructores
          </p>
        </div>
      </div>

      <div className="form-inline-card">
        <h4>{editandoId ? "Editar competencia" : "Nueva competencia"}</h4>
        {error && <div className="form-mensaje-error">{error}</div>}
        <form onSubmit={manejarEnvio} className="form-inline-row">
          <div>
            <label>Nombre *</label>
            <input
              type="text"
              name="nombre"
              value={formulario.nombre}
              onChange={manejarCambio}
              placeholder="Ej: Python"
            />
          </div>
          <div>
            <label>Descripción</label>
            <input
              type="text"
              name="descripcion"
              value={formulario.descripcion}
              onChange={manejarCambio}
              placeholder="Opcional"
            />
          </div>
          <div>
            <label>
              <input
                type="checkbox"
                name="estado"
                checked={formulario.estado}
                onChange={manejarCambio}
              />{" "}
              Activa
            </label>
          </div>
          <div>
            <button type="submit" className="btn-submit-form">
              {editandoId ? "Guardar cambios" : "Crear"}
            </button>
          </div>
          {editandoId && (
            <div>
              <button type="button" className="btn-cancel-form" onClick={cancelarEdicion}>
                Cancelar
              </button>
            </div>
          )}
        </form>
      </div>

      {cargando && <p className="text-muted">Cargando competencias...</p>}

      {!cargando && (
        <table className="tabla-simple">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {competencias.map((c) => (
              <tr key={c.id_competencia}>
                <td>{c.nombre}</td>
                <td>{c.descripcion || "—"}</td>
                <td>
                  <span className={`estado-badge ${c.estado ? "activo" : "inactivo"}`}>
                    {c.estado ? "Activa" : "Inactiva"}
                  </span>
                </td>
                <td className="acciones-tabla">
                  <button className="editar" onClick={() => iniciarEdicion(c)}>
                    <i className="bi bi-pencil"></i>
                  </button>
                  <button className="eliminar" onClick={() => manejarEliminar(c.id_competencia)}>
                    <i className="bi bi-trash"></i>
                  </button>
                </td>
              </tr>
            ))}
            {competencias.length === 0 && (
              <tr>
                <td colSpan="4" className="text-muted">
                  Aún no hay competencias registradas.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Competencias;
