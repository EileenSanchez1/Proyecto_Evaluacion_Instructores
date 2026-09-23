import { useEffect, useState } from "react";
import {
  listarPeriodos,
  crearPeriodo,
  actualizarPeriodo,
  desactivarPeriodo,
  reactivarPeriodo,
} from "../services/PeriodoService";
import "../styles/Instructores.css";

function Periodos() {
  const [periodos, setPeriodos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [exito, setExito] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [editando, setEditando] = useState(null);
  // "activos" | "inactivos"
  const [vista, setVista] = useState("activos");
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
      setError("");
      const datos = await listarPeriodos();
      setPeriodos(datos || []);
    } catch (err) {
      setError("No se pudieron cargar los periodos.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarPeriodos();
  }, []);

  const periodosFiltrados = periodos.filter((p) => {
    const activo = String(p.estado || "").toLowerCase() === "activo";
    return vista === "activos" ? activo : !activo;
  });

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario({ ...formulario, [name]: value });
  };

  const manejarSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setExito("");
    try {
      if (editando) {
        await actualizarPeriodo(editando.id_periodo, formulario);
        setExito("Periodo actualizado.");
      } else {
        await crearPeriodo({ ...formulario, estado: "Activo" });
        setExito("Periodo creado.");
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
        typeof detalle === "string" ? detalle : "Error al guardar el periodo."
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
    setError("");
    setExito("");
  };

  const manejarDesactivar = async (p) => {
    if (
      !window.confirm(
        `¿Desactivar el periodo "${p.nombre}"?\n\nLos aprendices ya no podrán evaluar en este periodo. El historial de evaluaciones se conserva.`
      )
    ) {
      return;
    }
    try {
      setError("");
      await desactivarPeriodo(p.id_periodo);
      setExito(`Periodo "${p.nombre}" desactivado. Historial conservado.`);
      await cargarPeriodos();
    } catch (err) {
      const d = err.response?.data?.detail;
      setError(typeof d === "string" ? d : "No se pudo desactivar el periodo.");
    }
  };

  const manejarReactivar = async (p) => {
    if (
      !window.confirm(
        `¿Reactivar el periodo "${p.nombre}"?\nLos aprendices asignados a este periodo podrán volver a evaluar.`
      )
    ) {
      return;
    }
    try {
      setError("");
      await reactivarPeriodo(p.id_periodo);
      setExito(`Periodo "${p.nombre}" reactivado.`);
      setVista("activos");
      await cargarPeriodos();
    } catch (err) {
      const d = err.response?.data?.detail;
      setError(typeof d === "string" ? d : "No se pudo reactivar el periodo.");
    }
  };

  return (
    <div className="container-fluid page-content py-4">
      <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
        <div>
          <h1 className="titulo">
            <i className="bi bi-calendar-range"></i> Gestión de Periodos
          </h1>
          <p className="subtitulo">
            Gestiona los periodos de evaluación. Desactivar no borra el historial.
          </p>
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
            setError("");
            setExito("");
          }}
        >
          <i className="bi bi-plus-circle"></i> Nuevo Periodo
        </button>
      </div>

      {/* Filtro Activos / Inactivos */}
      <div
        style={{
          display: "inline-flex",
          gap: 0,
          marginBottom: 16,
          borderRadius: 10,
          overflow: "hidden",
          border: "1px solid #d1d5db",
        }}
      >
        <button
          type="button"
          onClick={() => setVista("activos")}
          style={{
            padding: "8px 18px",
            border: "none",
            cursor: "pointer",
            fontWeight: 600,
            background: vista === "activos" ? "#39a900" : "#fff",
            color: vista === "activos" ? "#fff" : "#374151",
          }}
        >
          <i className="bi bi-check-circle"></i> Activos
        </button>
        <button
          type="button"
          onClick={() => setVista("inactivos")}
          style={{
            padding: "8px 18px",
            border: "none",
            borderLeft: "1px solid #d1d5db",
            cursor: "pointer",
            fontWeight: 600,
            background: vista === "inactivos" ? "#6b7280" : "#fff",
            color: vista === "inactivos" ? "#fff" : "#374151",
          }}
        >
          <i className="bi bi-pause-circle"></i> Inactivos
        </button>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}
      {exito && (
        <div className="alert alert-success" role="alert">
          {exito}
        </div>
      )}

      {mostrarFormulario && (
        <div className="card mb-4 shadow-sm">
          <div className="card-body">
            <h5 className="card-title">
              {editando ? "Editar periodo" : "Nuevo periodo"}
            </h5>
            <form onSubmit={manejarSubmit}>
              <div className="row g-3">
                <div className="col-md-4">
                  <label className="form-label">Nombre *</label>
                  <input
                    type="text"
                    name="nombre"
                    className="form-control"
                    value={formulario.nombre}
                    onChange={manejarCambio}
                    required
                    placeholder="Ej. 2026-Trim3"
                  />
                </div>
                <div className="col-md-4">
                  <label className="form-label">Fecha inicio *</label>
                  <input
                    type="date"
                    name="fecha_inicio"
                    className="form-control"
                    value={formulario.fecha_inicio}
                    onChange={manejarCambio}
                    required
                  />
                </div>
                <div className="col-md-4">
                  <label className="form-label">Fecha fin *</label>
                  <input
                    type="date"
                    name="fecha_fin"
                    className="form-control"
                    value={formulario.fecha_fin}
                    onChange={manejarCambio}
                    required
                  />
                </div>
                <div className="col-md-8">
                  <label className="form-label">Descripción</label>
                  <input
                    type="text"
                    name="descripcion"
                    className="form-control"
                    value={formulario.descripcion}
                    onChange={manejarCambio}
                    placeholder="Opcional"
                  />
                </div>
                {editando && (
                  <div className="col-md-4">
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
                )}
              </div>
              <div className="mt-3 text-end">
                <button
                  type="button"
                  className="btn btn-outline-secondary me-2"
                  onClick={() => {
                    setMostrarFormulario(false);
                    setEditando(null);
                  }}
                >
                  Cancelar
                </button>
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

      {!cargando && periodosFiltrados.length === 0 && (
        <div
          style={{
            textAlign: "center",
            padding: "40px 16px",
            background: "#f9fafb",
            borderRadius: 12,
            color: "#6b7280",
          }}
        >
          <i className="bi bi-calendar-x" style={{ fontSize: 32 }}></i>
          <p className="mt-2 mb-0">
            {vista === "activos"
              ? "No hay periodos activos."
              : "No hay periodos inactivos."}
          </p>
        </div>
      )}

      {!cargando && periodosFiltrados.length > 0 && (
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
              {periodosFiltrados.map((p) => (
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
                      className="badge"
                      style={{
                        background:
                          p.estado === "Activo" ? "#d1fae5" : "#e5e7eb",
                        color: p.estado === "Activo" ? "#065f46" : "#374151",
                        border:
                          p.estado === "Activo"
                            ? "1px solid #a7f3d0"
                            : "1px solid #d1d5db",
                        fontWeight: 700,
                        padding: "6px 12px",
                        borderRadius: 20,
                      }}
                    >
                      {p.estado}
                    </span>
                  </td>
                  <td className="text-end">
                    <button
                      className="btn btn-sm btn-outline-primary me-1"
                      title="Editar"
                      onClick={() => iniciarEdicion(p)}
                    >
                      <i className="bi bi-pencil"></i>
                    </button>
                    {String(p.estado || "").toLowerCase() === "activo" ? (
                      <button
                        className="btn btn-sm btn-outline-warning"
                        title="Desactivar (conserva historial)"
                        onClick={() => manejarDesactivar(p)}
                      >
                        <i className="bi bi-pause-circle"></i>
                      </button>
                    ) : (
                      <button
                        className="btn btn-sm btn-outline-success"
                        title="Reactivar"
                        onClick={() => manejarReactivar(p)}
                      >
                        <i className="bi bi-play-circle"></i>
                      </button>
                    )}
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
