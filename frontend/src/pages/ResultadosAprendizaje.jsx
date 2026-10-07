import { useEffect, useState } from "react";
import {
  listarResultadosAprendizaje,
  crearResultadoAprendizaje,
  actualizarResultadoAprendizaje,
  eliminarResultadoAprendizaje,
  reactivarResultadoAprendizaje,
} from "../services/resultadoAprendizajeService";
import "../styles/Estructura.css";
import "../styles/Instructores.css";

const FORMULARIO_VACIO = { codigo: "", nombre: "", descripcion: "", estado: true };

function ResultadosAprendizaje() {
  const [items, setItems] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [editandoId, setEditandoId] = useState(null);
  const [formulario, setFormulario] = useState(FORMULARIO_VACIO);

  const cargar = async () => {
    try {
      setCargando(true);
      setError("");
      setItems(await listarResultadosAprendizaje());
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar los resultados de aprendizaje.");
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

  const iniciarEdicion = (ra) => {
    setEditandoId(ra.id_resultado);
    setFormulario({
      codigo: ra.codigo || "",
      nombre: ra.nombre,
      descripcion: ra.descripcion || "",
      estado: ra.estado,
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
      setError("El nombre del resultado de aprendizaje es obligatorio.");
      return;
    }

    const payload = {
      codigo: formulario.codigo.trim() || null,
      nombre: formulario.nombre.trim(),
      descripcion: formulario.descripcion.trim() || null,
      estado: formulario.estado,
    };

    try {
      if (editandoId) {
        await actualizarResultadoAprendizaje(editandoId, payload);
      } else {
        await crearResultadoAprendizaje(payload);
      }

      cancelarEdicion();
      await cargar();
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
          "No se pudo guardar el resultado de aprendizaje."
      );
    }
  };

  const manejarDesactivar = async (id) => {
    if (
      !window.confirm(
        "¿Desactivar este resultado de aprendizaje?\nNo se borrarán las asignaciones a instructores. Podrás reactivarlo después."
      )
    )
      return;

    try {
      await eliminarResultadoAprendizaje(id);
      await cargar();
    } catch (err) {
      console.error(err);
      alert(
        err.response?.data?.detail ||
          "No se pudo desactivar el resultado de aprendizaje."
      );
    }
  };

  const manejarReactivar = async (id) => {
    try {
      await reactivarResultadoAprendizaje(id);
      await cargar();
    } catch (err) {
      console.error(err);
      alert(
        err.response?.data?.detail ||
          "No se pudo reactivar el resultado de aprendizaje."
      );
    }
  };

  return (
    <div className="pagina-estructura">
      <div className="encabezado">
        <div>
          <h1 className="titulo">Resultados de Aprendizaje</h1>
          <p className="subtitulo">
            Gestiona los Resultados de Aprendizaje (RA) del programa, como en el
            horario (ej. 220501-04 CODIFICAR EL SOFTWARE...). Se asignan a los
            instructores. Desactivar no borra el historial ni las asignaciones.
          </p>
        </div>
      </div>

      <div className="form-inline-card">
        <h4>
          {editandoId
            ? "Editar resultado de aprendizaje"
            : "Nuevo resultado de aprendizaje"}
        </h4>
        {error && <div className="form-mensaje-error">{error}</div>}
        <form onSubmit={manejarEnvio} className="form-inline-row">
          <div>
            <label>Código</label>
            <input
              type="text"
              name="codigo"
              value={formulario.codigo}
              onChange={manejarCambio}
              placeholder="Ej: 220501-04"
            />
          </div>
          <div>
            <label>Nombre *</label>
            <input
              type="text"
              name="nombre"
              value={formulario.nombre}
              onChange={manejarCambio}
              placeholder="Ej: CODIFICAR EL SOFTWARE DE ACUERDO CON EL DISEÑO ESTABLECIDO."
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
              Activo
            </label>
          </div>
          <div>
            <button type="submit" className="btn-submit-form">
              {editandoId ? "Guardar cambios" : "Crear"}
            </button>
          </div>
          {editandoId && (
            <div>
              <button
                type="button"
                className="btn-cancel-form"
                onClick={cancelarEdicion}
              >
                Cancelar
              </button>
            </div>
          )}
        </form>
      </div>

      {cargando && (
        <p className="text-muted">Cargando resultados de aprendizaje...</p>
      )}

      {!cargando && (
        <table className="tabla-simple">
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((ra) => (
              <tr key={ra.id_resultado}>
                <td>{ra.codigo || "—"}</td>
                <td>{ra.nombre}</td>
                <td>{ra.descripcion || "—"}</td>
                <td>
                  <span
                    className={`estado-badge ${
                      ra.estado ? "activo" : "inactivo"
                    }`}
                  >
                    {ra.estado ? "Activo" : "Inactivo"}
                  </span>
                </td>
                <td className="acciones-tabla">
                  <button
                    className="editar"
                    onClick={() => iniciarEdicion(ra)}
                    title="Editar"
                  >
                    <i className="bi bi-pencil"></i>
                  </button>
                  {ra.estado ? (
                    <button
                      className="eliminar"
                      onClick={() => manejarDesactivar(ra.id_resultado)}
                      title="Desactivar"
                    >
                      <i className="bi bi-pause-circle"></i>
                    </button>
                  ) : (
                    <button
                      className="editar"
                      onClick={() => manejarReactivar(ra.id_resultado)}
                      title="Reactivar"
                      style={{ background: "#39a900", color: "#fff" }}
                    >
                      <i className="bi bi-play-circle"></i>
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan="5" className="text-muted">
                  Aún no hay resultados de aprendizaje registrados.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default ResultadosAprendizaje;
