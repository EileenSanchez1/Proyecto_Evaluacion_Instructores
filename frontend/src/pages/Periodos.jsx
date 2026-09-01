import { useEffect, useState } from "react";
import {
  listarPeriodos,
  crearPeriodo,
  actualizarPeriodo,
  eliminarPeriodo,
} from "../services/PeriodoService";
import "../styles/Fichas.css";

function Periodos() {
  const [periodos, setPeriodos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [editando, setEditando] = useState(null);

  const [formulario, setFormulario] = useState({
    nombre: "",
    descripcion: "",
    fecha_inicio: "",
    fecha_fin: "",
    estado: "Activo",
  });

  const cargarPeriodos = async () => {
    try {
      setCargando(true);
      const datos = await listarPeriodos();
      setPeriodos(datos);
    } catch (err) {
      setError("No se pudieron cargar los periodos.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarPeriodos();
  }, []);

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario({ ...formulario, [name]: value });
  };

  const manejarSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      if (editando) {
        await actualizarPeriodo(editando.id_periodo, formulario);
      } else {
        await crearPeriodo(formulario);
      }
      setMostrarFormulario(false);
      setEditando(null);
      setFormulario({
        nombre: "",
        descripcion: "",
        fecha_inicio: "",
        fecha_fin: "",
        estado: "Activo",
      });
      await cargarPeriodos();
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(
        typeof detalle === "string"
          ? detalle
          : "Error al guardar el periodo."
      );
    }
  };

  const iniciarEdicion = (periodo) => {
    setEditando(periodo);
    setFormulario({
      nombre: periodo.nombre,
      descripcion: periodo.descripcion || "",
      fecha_inicio: periodo.fecha_inicio,
      fecha_fin: periodo.fecha_fin,
      estado: periodo.estado,
    });
    setMostrarFormulario(true);
  };

  const manejarEliminar = async (id) => {
    if (window.confirm("¿Eliminar este periodo?")) {
      try {
        await eliminarPeriodo(id);
        await cargarPeriodos();
      } catch {
        setError("Error al eliminar el periodo.");
      }
    }
  };

  return (
    <div className="container-fluid page-content py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>
            <i className="bi bi-calendar-range"></i> Periodos Académicos
          </h2>
          <p className="text-muted">Gestiona los periodos de evaluación.</p>
        </div>
        <button
          className="btn btn-success"
          onClick={() => {
            setMostrarFormulario(!mostrarFormulario);
            setEditando(null);
            setFormulario({
              nombre: "",
              descripcion: "",
              fecha_inicio: "",
              fecha_fin: "",
              estado: "Activo",
            });
          }}
        >
          <i className="bi bi-plus-circle"></i>{" "}
          {mostrarFormulario ? "Cancelar" : "Nuevo Periodo"}
        </button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {mostrarFormulario && (
        <div className="card shadow-sm mb-4">
          <div className="card-body">
            <h5>{editando ? "Editar Periodo" : "Crear Periodo"}</h5>
            <form onSubmit={manejarSubmit}>
              <div className="row g-3">
                <div className="col-md-3">
                  <label className="form-label">Nombre *</label>
                  <input
                    type="text"
                    name="nombre"
                    className="form-control"
                    placeholder="Ej: 2026-T3"
                    value={formulario.nombre}
                    onChange={manejarCambio}
                    required
                  />
                </div>
                <div className="col-md-3">
                  <label className="form-label">Fecha Inicio *</label>
                  <input
                    type="date"
                    name="fecha_inicio"
                    className="form-control"
                    value={formulario.fecha_inicio}
                    onChange={manejarCambio}
                    required
                  />
                </div>
                <div className="col-md-3">
                  <label className="form-label">Fecha Fin *</label>
                  <input
                    type="date"
                    name="fecha_fin"
                    className="form-control"
                    value={formulario.fecha_fin}
                    onChange={manejarCambio}
                    required
                  />
                </div>
                <div className="col-md-3">
                  <label className="form-label">Estado</label>
                  <select
                    name="estado"
                    className="form-select"
                    value={formulario.estado}
                    onChange={manejarCambio}
                  >
                    <option value="Activo">Activo</option>
                    <option value="Inactivo">Inactivo</option>
                  </select>
                </div>
                <div className="col-12">
                  <label className="form-label">Descripción</label>
                  <input
                    type="text"
                    name="descripcion"
                    className="form-control"
                    value={formulario.descripcion}
                    onChange={manejarCambio}
                  />
                </div>
              </div>
              <div className="mt-3 text-end">
                <button type="submit" className="btn btn-primary">
                  <i className="bi bi-check-circle"></i>{" "}
                  {editando ? "Actualizar" : "Guardar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {cargando && <p className="text-muted">Cargando periodos...</p>}

      {!cargando && periodos.length === 0 && (
        <p className="text-muted">No hay periodos registrados.</p>
      )}

      {!cargando && periodos.length > 0 && (
        <div className="table-responsive">
          <table className="table table-hover align-middle">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th>Estado</th>
                <th className="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {periodos.map((p) => (
                <tr key={p.id_periodo}>
                  <td>
                    <strong>{p.nombre}</strong>
                    {p.descripcion && (
                      <div className="text-muted small">{p.descripcion}</div>
                    )}
                  </td>
                  <td>{p.fecha_inicio}</td>
                  <td>{p.fecha_fin}</td>
                  <td>
                    <span
                      className={`badge ${
                        p.estado === "Activo"
                          ? "bg-success"
                          : "bg-secondary"
                      }`}
                    >
                      {p.estado}
                    </span>
                  </td>
                  <td className="text-end">
                    <button
                      className="btn btn-sm btn-outline-primary me-1"
                      onClick={() => iniciarEdicion(p)}
                    >
                      <i className="bi bi-pencil"></i>
                    </button>
                    <button
                      className="btn btn-sm btn-outline-danger"
                      onClick={() => manejarEliminar(p.id_periodo)}
                    >
                      <i className="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Periodos;
