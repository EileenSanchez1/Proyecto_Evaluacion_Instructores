import { useEffect, useState } from "react";
import {
  listarFichas,
  crearFicha,
  actualizarFicha,
  eliminarFicha,
} from "../services/FichaServices";
import { listarAprendices } from "../services/Aprendizservice";
import {
  listarInstructoresPorFicha,
  crearFichaInstructor,
  eliminarFichaInstructor,
} from "../services/Fichainstructorservice";
import { listarInstructores } from "../services/instructorService";
import { listarPeriodos } from "../services/PeriodoService";
import { obtenerInstructor } from "../services/instructorService";
import "../styles/Fichas.css";

function Fichas() {
  const [fichas, setFichas] = useState([]);
  const [aprendices, setAprendices] = useState([]);
  const [instructores, setInstructores] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [busqueda, setBusqueda] = useState("");

  const [mostrarModal, setMostrarModal] = useState(false);
  const [editando, setEditando] = useState(null);
  const [formulario, setFormulario] = useState({
    numero_ficha: "",
    programa: "",
    descripcion: "",
  });
  const [guardando, setGuardando] = useState(false);

  const [fichaSeleccionada, setFichaSeleccionada] = useState(null);
  const [instructoresFicha, setInstructoresFicha] = useState([]);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);

  const [mostrarAsignar, setMostrarAsignar] = useState(false);
  const [idInstructorSeleccionado, setIdInstructorSeleccionado] = useState("");
  const [idPeriodoSeleccionado, setIdPeriodoSeleccionado] = useState("");
  const [guardandoAsignacion, setGuardandoAsignacion] = useState(false);

  const cargarDatos = async () => {
    try {
      setCargando(true);
      setError("");
      const [fichasData, aprendicesData, instructoresData, periodosData] =
        await Promise.all([
          listarFichas(),
          listarAprendices(),
          listarInstructores(),
          listarPeriodos(),
        ]);
      setFichas(fichasData);
      setAprendices(aprendicesData);
      setInstructores(instructoresData);
      setPeriodos(periodosData);
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar las fichas.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const contarAprendices = (idFicha) =>
    aprendices.filter((a) => a.id_ficha === idFicha).length;

  const texto = busqueda.toLowerCase().trim();
  const fichasFiltradas = fichas.filter((f) => {
    if (!texto) return true;
    return (
      f.numero_ficha.toLowerCase().includes(texto) ||
      f.programa.toLowerCase().includes(texto)
    );
  });

  const abrirCrear = () => {
    setEditando(null);
    setFormulario({ numero_ficha: "", programa: "", descripcion: "" });
    setError("");
    setMostrarModal(true);
  };

  const abrirEditar = (ficha) => {
    setEditando(ficha);
    setFormulario({
      numero_ficha: ficha.numero_ficha,
      programa: ficha.programa,
      descripcion: ficha.descripcion || "",
    });
    setError("");
    setMostrarModal(true);
  };

  const cerrarModal = () => {
    setMostrarModal(false);
    setEditando(null);
    setFormulario({ numero_ficha: "", programa: "", descripcion: "" });
    setError("");
  };

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario((prev) => ({ ...prev, [name]: value }));
  };

  const manejarGuardar = async (e) => {
    e.preventDefault();
    setError("");
    if (!formulario.numero_ficha.trim() || !formulario.programa.trim()) {
      setError("Numero de ficha y programa son obligatorios.");
      return;
    }
    try {
      setGuardando(true);
      if (editando) {
        await actualizarFicha(editando.id_ficha, formulario);
      } else {
        await crearFicha(formulario);
      }
      cerrarModal();
      await cargarDatos();
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(typeof detalle === "string" ? detalle : "Error al guardar la ficha.");
    } finally {
      setGuardando(false);
    }
  };

  const manejarEliminar = async (id) => {
    if (!window.confirm("Eliminar esta ficha? Se perderan las asignaciones de instructores y aprendices.")) {
      return;
    }
    try {
      await eliminarFicha(id);
      await cargarDatos();
    } catch (err) {
      const detalle = err.response?.data?.detail;
      alert(typeof detalle === "string" ? detalle : "Error al eliminar la ficha.");
    }
  };

  const abrirDetalle = async (ficha) => {
    setFichaSeleccionada(ficha);
    setInstructoresFicha([]);
    setCargandoDetalle(true);
    setMostrarAsignar(false);
    setIdInstructorSeleccionado("");
    setIdPeriodoSeleccionado("");
    try {
      const relaciones = await listarInstructoresPorFicha(ficha.id_ficha);
      const instructores = await Promise.all(
        relaciones.map((rel) => obtenerInstructor(rel.id_instructor))
      );
      setInstructoresFicha(instructores);
    } catch (err) {
      console.error("No se pudieron cargar los instructores de la ficha", err);
    } finally {
      setCargandoDetalle(false);
    }
  };

  const cerrarDetalle = () => {
    setFichaSeleccionada(null);
    setInstructoresFicha([]);
    setMostrarAsignar(false);
  };

  const manejarAsignarInstructor = async (e) => {
    e.preventDefault();
    setError("");
    if (!idInstructorSeleccionado || !idPeriodoSeleccionado) {
      setError("Debes seleccionar un instructor y un periodo.");
      return;
    }
    try {
      setGuardandoAsignacion(true);
      await crearFichaInstructor({
        id_ficha: fichaSeleccionada.id_ficha,
        id_instructor: Number(idInstructorSeleccionado),
        id_periodo: Number(idPeriodoSeleccionado),
      });
      setMostrarAsignar(false);
      setIdInstructorSeleccionado("");
      setIdPeriodoSeleccionado("");
      await abrirDetalle(fichaSeleccionada);
      await cargarDatos();
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(typeof detalle === "string" ? detalle : "Error al asignar instructor.");
    } finally {
      setGuardandoAsignacion(false);
    }
  };

  const manejarDesasignarInstructor = async (idRelacion) => {
    if (!window.confirm("¿Eliminar esta asignación de instructor?")) return;
    try {
      await eliminarFichaInstructor(idRelacion);
      await abrirDetalle(fichaSeleccionada);
      await cargarDatos();
    } catch (err) {
      alert(err.response?.data?.detail || "Error al eliminar la asignación.");
    }
  };

  return (
    <div className="pagina-fichas">
      <div className="encabezado">
        <div>
          <h1 className="titulo">Gestion de Fichas</h1>
          <p className="subtitulo">
            Consulta y administra las fichas de formacion registradas en el sistema
          </p>
        </div>
        <button className="btn btn-success" onClick={abrirCrear}>
          <i className="bi bi-plus-circle"></i> Nueva Ficha
        </button>
      </div>

      <div className="barra-superior">
        <div className="buscador">
          <span className="buscador-icono"><i className="bi bi-search"></i></span>
          <input
            type="text"
            placeholder="Buscar por numero de ficha o programa..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>
      </div>

      {!cargando && !error && (
        <p className="contador-resultados">
          {fichasFiltradas.length}{" "}
          {fichasFiltradas.length === 1 ? "ficha encontrada" : "fichas encontradas"}
        </p>
      )}

      {cargando && <p className="text-muted">Cargando fichas...</p>}
      {error && !mostrarModal && <p className="text-danger">{error}</p>}

      {!cargando && !error && fichasFiltradas.length === 0 && (
        <div className="estado-vacio">
          <i className="bi bi-search"></i>
          <h4>No se encontraron fichas</h4>
          <p>
            {fichas.length === 0
              ? "Aun no hay fichas registradas. Crea una nueva ficha para comenzar."
              : "Intenta con otro termino de busqueda"}
          </p>
        </div>
      )}

      {!cargando && fichasFiltradas.length > 0 && (
        <div className="grid-fichas">
          {fichasFiltradas.map((ficha) => (
            <div className="ficha-card ficha-item" key={ficha.id_ficha}>
              <div className="ficha-encabezado-card">
                <div className="ficha-numero">
                  <i className="bi bi-hash"></i>
                  {ficha.numero_ficha}
                </div>
                <span className="badge-aprendices">
                  <i className="bi bi-people"></i> {contarAprendices(ficha.id_ficha)}
                </span>
              </div>
              <p className="ficha-programa">{ficha.programa}</p>
              <hr />
              <p>
                <i className="bi bi-card-text"></i>
                {ficha.descripcion || "Sin descripcion registrada."}
              </p>
              <p>
                <i className="bi bi-people"></i>
                {contarAprendices(ficha.id_ficha)} aprendiz(ces) asociado(s)
              </p>
              <div className="acciones">
                <button onClick={() => abrirDetalle(ficha)}>
                  <i className="bi bi-eye"></i> Ver detalle
                </button>
                <button className="btn-outline-primary" onClick={() => abrirEditar(ficha)}>
                  <i className="bi bi-pencil"></i> Editar
                </button>
                <button className="btn-outline-danger" onClick={() => manejarEliminar(ficha.id_ficha)}>
                  <i className="bi bi-trash"></i> Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {mostrarModal && (
        <div className="modal-overlay" onClick={cerrarModal}>
          <div className="modal-caja" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h5>
                <i className={`bi ${editando ? "bi-pencil-square" : "bi-plus-circle"} me-2`}></i>
                {editando ? "Editar Ficha" : "Nueva Ficha"}
              </h5>
              <button onClick={cerrarModal} aria-label="Cerrar"><i className="bi bi-x-lg"></i></button>
            </div>
            <div className="modal-body">
              {error && <div className="alert alert-danger">{error}</div>}
              <form onSubmit={manejarGuardar}>
                <div className="mb-3">
                  <label className="form-label">Numero de Ficha *</label>
                  <input type="text" name="numero_ficha" className="form-control"
                    placeholder="Ej: 2876543" value={formulario.numero_ficha}
                    onChange={manejarCambio} required />
                </div>
                <div className="mb-3">
                  <label className="form-label">Programa *</label>
                  <input type="text" name="programa" className="form-control"
                    placeholder="Ej: Analisis y Desarrollo de Software" value={formulario.programa}
                    onChange={manejarCambio} required />
                </div>
                <div className="mb-3">
                  <label className="form-label">Descripcion</label>
                  <textarea name="descripcion" className="form-control" rows={3}
                    placeholder="Descripcion opcional de la ficha..."
                    value={formulario.descripcion} onChange={manejarCambio} />
                </div>
                <div className="d-flex justify-content-end gap-2">
                  <button type="button" className="btn btn-secondary" onClick={cerrarModal}>Cancelar</button>
                  <button type="submit" className="btn btn-success" disabled={guardando}>
                    <i className="bi bi-check-circle"></i>{" "}
                    {guardando ? "Guardando..." : editando ? "Actualizar" : "Crear"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {fichaSeleccionada && (
        <div className="modal-overlay" onClick={cerrarDetalle}>
          <div className="modal-caja modal-caja-grande" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h5><i className="bi bi-card-text me-2"></i> Detalle de la Ficha</h5>
              <button onClick={cerrarDetalle} aria-label="Cerrar"><i className="bi bi-x-lg"></i></button>
            </div>
            <div className="modal-body detalle-body">
              <h3>Ficha {fichaSeleccionada.numero_ficha}</h3>
              <span className="badge-aprendices">
                {contarAprendices(fichaSeleccionada.id_ficha)} aprendices
              </span>
              <hr />
              <p><i className="bi bi-mortarboard"></i><span><strong>Programa:</strong> {fichaSeleccionada.programa}</span></p>
              <p><i className="bi bi-card-text"></i><span><strong>Descripcion:</strong> {fichaSeleccionada.descripcion || "Sin descripcion registrada."}</span></p>
              <p><i className="bi bi-people"></i><span><strong>Aprendices:</strong> {contarAprendices(fichaSeleccionada.id_ficha)}</span></p>

              <div className="detalle-instructores">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <p style={{ marginBottom: 4 }}>
                    <i className="bi bi-person-badge"></i>
                    <span><strong>Instructores asignados:</strong></span>
                  </p>
                  <button className="btn btn-sm btn-success" onClick={() => setMostrarAsignar(!mostrarAsignar)}>
                    <i className="bi bi-plus-circle"></i> {mostrarAsignar ? "Cancelar" : "Asignar instructor"}
                  </button>
                </div>

                {mostrarAsignar && (
                  <form onSubmit={manejarAsignarInstructor}
                    style={{ marginBottom: 16, padding: 12, background: "#f8f9fa", borderRadius: 8 }}>
                    {error && <div className="alert alert-danger">{error}</div>}
                    <div style={{ display: "flex", gap: 10, alignItems: "flex-end" }}>
                      <div style={{ flex: 1 }}>
                        <label className="form-label">Instructor</label>
                        <select className="form-select"
                          value={idInstructorSeleccionado}
                          onChange={(e) => setIdInstructorSeleccionado(e.target.value)} required>
                          <option value="">Selecciona instructor</option>
                          {instructores.map((inst) => (
                            <option key={inst.id_instructor} value={inst.id_instructor}>
                              {inst.nombre} {inst.apellido}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div style={{ flex: 1 }}>
                        <label className="form-label">Periodo</label>
                        <select className="form-select"
                          value={idPeriodoSeleccionado}
                          onChange={(e) => setIdPeriodoSeleccionado(e.target.value)} required>
                          <option value="">Selecciona periodo</option>
                          {periodos.map((p) => (
                            <option key={p.id_periodo} value={p.id_periodo}>
                              {p.nombre} {p.estado === "Activo" ? "(Activo)" : ""}
                            </option>
                          ))}
                        </select>
                      </div>
                      <button type="submit" className="btn btn-success" disabled={guardandoAsignacion}>
                        {guardandoAsignacion ? "Guardando..." : "Asignar"}
                      </button>
                    </div>
                  </form>
                )}

                {cargandoDetalle && (
                  <p className="text-muted" style={{ paddingLeft: 30 }}>Cargando instructores...</p>
                )}

                {!cargandoDetalle && instructoresFicha.length === 0 && (
                  <p className="text-muted" style={{ paddingLeft: 30 }}>Esta ficha no tiene instructores asignados.</p>
                )}

                {!cargandoDetalle && instructoresFicha.length > 0 && (
                  <ul>
                    {instructoresFicha.map((inst) => (
                      <li key={inst.id_instructor} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span>
                          <i className="bi bi-person-fill"></i>
                          {inst.nombre} {inst.apellido} —{" "}
                          {(inst.competencias || []).map((c) => c.nombre).join(", ") || "sin competencias"}
                        </span>
                        <button className="btn btn-sm btn-outline-danger"
                          onClick={() => {
                            listarInstructoresPorFicha(fichaSeleccionada.id_ficha).then((rels) => {
                              const rel = rels.find((r) => r.id_instructor === inst.id_instructor);
                              if (rel) manejarDesasignarInstructor(rel.id);
                            });
                          }} title="Eliminar asignación">
                          <i className="bi bi-trash"></i>
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
            <div className="modal-footer">
              <button onClick={cerrarDetalle}>Cerrar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Fichas;