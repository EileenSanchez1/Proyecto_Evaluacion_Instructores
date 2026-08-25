import { useEffect, useState } from "react";
import {
  listarPreguntas,
  crearPregunta,
  actualizarPregunta,
  eliminarPregunta,
} from "../services/Preguntaservice";
import "../styles/Preguntas.css";

const FORM_VACIO = { descripcion: "", orden: "" };

function Preguntas() {
  const [preguntas, setPreguntas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [mostrarForm, setMostrarForm] = useState(false);
  const [editandoId, setEditandoId] = useState(null);
  const [formulario, setFormulario] = useState(FORM_VACIO);
  const [guardando, setGuardando] = useState(false);

  const cargarPreguntas = async () => {
    try {
      setCargando(true);
      setError("");
      const datos = await listarPreguntas();
      // Se muestran ordenadas tal como se responden en la evaluación.
      datos.sort((a, b) => a.orden - b.orden);
      setPreguntas(datos);
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar las preguntas.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarPreguntas();
  }, []);

  const abrirFormNueva = () => {
    setEditandoId(null);
    setFormulario({
      descripcion: "",
      orden:
        preguntas.length > 0
          ? Math.max(...preguntas.map((p) => p.orden)) + 1
          : 1,
    });
    setMostrarForm(true);
  };

  const abrirFormEditar = (pregunta) => {
    setEditandoId(pregunta.id_pregunta);
    setFormulario({
      descripcion: pregunta.descripcion,
      orden: pregunta.orden,
    });
    setMostrarForm(true);
  };

  const cerrarForm = () => {
    setMostrarForm(false);
    setEditandoId(null);
    setFormulario(FORM_VACIO);
  };

  const manejarCambio = (campo, valor) => {
    setFormulario((prev) => ({ ...prev, [campo]: valor }));
  };

  const manejarGuardar = async (e) => {
    e.preventDefault();
    setError("");

    if (!formulario.descripcion.trim() || formulario.orden === "") {
      setError("La descripción y el orden son obligatorios.");
      return;
    }

    try {
      setGuardando(true);

      if (editandoId) {
        await actualizarPregunta(editandoId, {
          descripcion: formulario.descripcion.trim(),
          orden: Number(formulario.orden),
        });
      } else {
        await crearPregunta({
          descripcion: formulario.descripcion.trim(),
          orden: Number(formulario.orden),
          estado: true,
        });
      }

      cerrarForm();
      await cargarPreguntas();
    } catch (err) {
      console.error(err);
      const detalle = err.response?.data?.detail;
      setError(
        typeof detalle === "string" ? detalle : "No se pudo guardar la pregunta."
      );
    } finally {
      setGuardando(false);
    }
  };

  const alternarEstado = async (pregunta) => {
    try {
      await actualizarPregunta(pregunta.id_pregunta, {
        estado: !pregunta.estado,
      });
      await cargarPreguntas();
    } catch (err) {
      console.error(err);
      alert("No se pudo cambiar el estado de la pregunta.");
    }
  };

  const manejarEliminar = async (pregunta) => {
    if (
      !window.confirm(
        `¿Eliminar la pregunta "${pregunta.descripcion}"? Esta acción no se puede deshacer.`
      )
    ) {
      return;
    }

    try {
      await eliminarPregunta(pregunta.id_pregunta);
      setPreguntas((prev) =>
        prev.filter((p) => p.id_pregunta !== pregunta.id_pregunta)
      );
    } catch (err) {
      console.error(err);
      alert("No se pudo eliminar la pregunta.");
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="evaluation-header mb-4">
        <div>
          <h2>
            <i className="bi bi-pencil-square"></i> Editor de Cuestionarios
          </h2>
          <p>
            Modifique, agregue o elimine las preguntas que componen la
            evaluación de instructores.
          </p>
        </div>
      </div>

      <div className="card shadow-sm mb-4">
        <div className="card-header bg-dark text-white d-flex justify-content-between align-items-center">
          <h5 className="mb-0">
            <i className="bi bi-list-task"></i> Preguntas del sistema
          </h5>
          {!mostrarForm && (
            <button className="btn btn-success btn-sm" onClick={abrirFormNueva}>
              <i className="bi bi-plus-circle"></i> Agregar nueva pregunta
            </button>
          )}
        </div>

        {mostrarForm && (
          <div className="card-body border-bottom">
            <h6>{editandoId ? "Editar pregunta" : "Nueva pregunta"}</h6>

            {error && <p className="text-danger">{error}</p>}

            <form onSubmit={manejarGuardar} className="row g-3 align-items-end">
              <div className="col-md-8">
                <label className="form-label small text-muted">Enunciado</label>
                <textarea
                  className="form-control"
                  rows={2}
                  value={formulario.descripcion}
                  onChange={(e) => manejarCambio("descripcion", e.target.value)}
                  required
                />
              </div>

              <div className="col-md-2">
                <label className="form-label small text-muted">Orden</label>
                <input
                  type="number"
                  min="1"
                  className="form-control"
                  value={formulario.orden}
                  onChange={(e) => manejarCambio("orden", e.target.value)}
                  required
                />
              </div>

              <div className="col-md-2 d-flex gap-2">
                <button
                  type="submit"
                  className="btn btn-success"
                  disabled={guardando}
                >
                  {guardando ? "Guardando..." : "Guardar"}
                </button>
                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={cerrarForm}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="card-body">
          {cargando && <p className="text-muted mb-0">Cargando preguntas...</p>}
          {error && !mostrarForm && <p className="text-danger mb-0">{error}</p>}

          {!cargando && !error && preguntas.length === 0 && (
            <p className="text-muted mb-0">No hay preguntas registradas.</p>
          )}

          {!cargando && preguntas.length > 0 && (
            <div className="table-responsive">
              <table className="table table-hover align-middle preguntas-table">
                <thead>
                  <tr>
                    <th style={{ width: "8%" }}>Bloque</th>
                    <th>Enunciado de la pregunta</th>
                    <th style={{ width: "12%" }}>Estado</th>
                    <th style={{ width: "15%" }} className="text-end">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {preguntas.map((pregunta) => (
                    <tr key={pregunta.id_pregunta}>
                      <td>
                        <span className="preguntas-orden-badge">
                          {pregunta.orden}
                        </span>
                      </td>
                      <td>{pregunta.descripcion}</td>
                      <td>
                        <button
                          className={`badge border-0 ${
                            pregunta.estado ? "badge-evaluado" : "bg-secondary"
                          }`}
                          onClick={() => alternarEstado(pregunta)}
                          title="Clic para activar/desactivar"
                        >
                          {pregunta.estado ? "Activa" : "Inactiva"}
                        </button>
                      </td>
                      <td className="text-end">
                        <button
                          className="btn btn-sm btn-outline-warning me-1"
                          onClick={() => abrirFormEditar(pregunta)}
                          title="Editar"
                        >
                          <i className="bi bi-pencil"></i>
                        </button>
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => manejarEliminar(pregunta)}
                          title="Eliminar"
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
      </div>
    </div>
  );
}

export default Preguntas;