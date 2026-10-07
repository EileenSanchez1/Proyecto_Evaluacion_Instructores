import { useEffect, useState } from "react";
import {
  listarFichas,
  crearFicha,
  actualizarFicha,
  eliminarFicha,
} from "../services/FichaServices";
import {
  listarAprendices,
  listarAprendicesPorFicha,
  cargaMasivaAprendices,
  actualizarAprendiz,
  desactivarAprendiz,
  reactivarAprendiz,
  reenviarCorreosFicha,
} from "../services/Aprendizservice";
import {
  listarInstructoresPorFicha,
  crearFichaInstructor,
  eliminarFichaInstructor,
} from "../services/Fichainstructorservice";
import { listarInstructores } from "../services/instructorService";
import { listarPeriodos } from "../services/PeriodoService";
import { obtenerInstructor } from "../services/instructorService";
import { listarResultadosAprendizaje } from "../services/resultadoAprendizajeService";
import "../styles/Fichas.css";

function Fichas() {
  const [fichas, setFichas] = useState([]);
  const [aprendices, setAprendices] = useState([]);
  const [instructores, setInstructores] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [resultadosRA, setResultadosRA] = useState([]);
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
  const [idsInstructoresSeleccionados, setIdsInstructoresSeleccionados] = useState([]);
  const [idPeriodoSeleccionado, setIdPeriodoSeleccionado] = useState("");
  const [idResultadoSeleccionado, setIdResultadoSeleccionado] = useState("");
  const [guardandoAsignacion, setGuardandoAsignacion] = useState(false);
  const [archivoCarga, setArchivoCarga] = useState(null);
  const [periodoCarga, setPeriodoCarga] = useState("");
  const [enviandoCarga, setEnviandoCarga] = useState(false);
  const [resultadoCarga, setResultadoCarga] = useState(null);
  const [aprendicesFicha, setAprendicesFicha] = useState([]);
  const [editAprendiz, setEditAprendiz] = useState(null);
  const [formAprendiz, setFormAprendiz] = useState({ nombre: "", apellido: "", correo: "" });
  const [guardandoAprendiz, setGuardandoAprendiz] = useState(false);
  const [enviandoCorreosFicha, setEnviandoCorreosFicha] = useState(false);



  const cargarDatos = async () => {
    try {
      setCargando(true);
      setError("");
      const [fichasData, aprendicesData, instructoresData, periodosData, raData] =
        await Promise.all([
          listarFichas(),
          listarAprendices(),
          listarInstructores(),
          listarPeriodos(),
          listarResultadosAprendizaje().catch(() => []),
        ]);
      setFichas(fichasData);
      setAprendices(aprendicesData);
      setInstructores(instructoresData);
      setPeriodos(periodosData);
      setResultadosRA(
        (raData || []).filter((r) => r.estado !== false && r.estado !== 0)
      );
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
    setAprendicesFicha([]);
    setEditAprendiz(null);
    setCargandoDetalle(true);
    setMostrarAsignar(false);
    setIdsInstructoresSeleccionados([]);
    setIdPeriodoSeleccionado("");
    setIdResultadoSeleccionado("");
    try {
      const aprs = await listarAprendicesPorFicha(ficha.id_ficha).catch(() => []);
      setAprendicesFicha(Array.isArray(aprs) ? aprs : []);
      const relaciones = await listarInstructoresPorFicha(ficha.id_ficha);
      const instructores = await Promise.all(
        relaciones.map(async (rel) => {
          const inst = await obtenerInstructor(rel.id_instructor).catch(() => null);
          if (!inst) return null;
          const periodo = periodos.find((p) => p.id_periodo === rel.id_periodo);
          const ra = resultadosRA.find(
            (r) => Number(r.id_resultado) === Number(rel.id_resultado)
          );
          return {
            ...inst,
            id_relacion: rel.id,
            id_periodo: rel.id_periodo,
            id_resultado: rel.id_resultado ?? null,
            nombre_periodo: periodo?.nombre || `Periodo #${rel.id_periodo}`,
            nombre_resultado:
              ra?.nombre ||
              (rel.id_resultado ? `RA #${rel.id_resultado}` : null),
          };
        })
      );
      setInstructoresFicha(instructores.filter(Boolean));
    } catch (err) {
      console.error("No se pudieron cargar los instructores de la ficha", err);
    } finally {
      setCargandoDetalle(false);
    }
  };

  const cerrarDetalle = () => {
    setFichaSeleccionada(null);
    setInstructoresFicha([]);
    setAprendicesFicha([]);
    setEditAprendiz(null);
    setMostrarAsignar(false);
    setIdsInstructoresSeleccionados([]);
    setIdResultadoSeleccionado("");
  };

  const abrirEditarAprendiz = (a) => {
    setEditAprendiz(a);
    setFormAprendiz({
      nombre: a.nombre || "",
      apellido: a.apellido || "",
      correo: a.correo || "",
    });
  };

  const guardarAprendiz = async (e) => {
    e.preventDefault();
    if (!editAprendiz) return;
    try {
      setGuardandoAprendiz(true);
      setError("");
      await actualizarAprendiz(editAprendiz.id_aprendiz, {
        nombre: formAprendiz.nombre.trim(),
        apellido: formAprendiz.apellido.trim(),
        correo: formAprendiz.correo.trim().toLowerCase(),
      });
      const aprs = await listarAprendicesPorFicha(fichaSeleccionada.id_ficha);
      setAprendicesFicha(aprs);
      setEditAprendiz(null);
      await cargarDatos();
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(typeof detalle === "string" ? detalle : "No se pudo actualizar el aprendiz.");
    } finally {
      setGuardandoAprendiz(false);
    }
  };


  const reenviarCorreos = async () => {
    if (!fichaSeleccionada) return;
    if (
      !window.confirm(
        "Se generará una nueva contraseña temporal y se enviará correo a TODOS los aprendices ACTIVOS de esta ficha. ¿Continuar?"
      )
    )
      return;
    try {
      setEnviandoCorreosFicha(true);
      const res = await reenviarCorreosFicha(fichaSeleccionada.id_ficha);
      alert(res?.mensaje || "Proceso de envío terminado.");
    } catch (err) {
      const detalle = err.response?.data?.detail;
      alert(typeof detalle === "string" ? detalle : "No se pudieron enviar los correos.");
    } finally {
      setEnviandoCorreosFicha(false);
    }
  };

  const toggleActivoAprendiz = async (a) => {
    const accion = a.activo ? "desactivar" : "reactivar";
    const msg = a.activo
      ? `¿Desactivar a ${a.nombre} ${a.apellido}? No podrá iniciar sesión (desertor/baja).`
      : `¿Reactivar a ${a.nombre} ${a.apellido}?`;
    if (!window.confirm(msg)) return;
    try {
      if (a.activo) await desactivarAprendiz(a.id_aprendiz);
      else await reactivarAprendiz(a.id_aprendiz);
      const aprs = await listarAprendicesPorFicha(fichaSeleccionada.id_ficha);
      setAprendicesFicha(aprs);
      await cargarDatos();
    } catch (err) {
      const detalle = err.response?.data?.detail;
      alert(typeof detalle === "string" ? detalle : `No se pudo ${accion} el aprendiz.`);
    }
  };


  const toggleInstructorCheck = (id) => {
    setIdsInstructoresSeleccionados((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const manejarAsignarInstructor = async (e) => {
    e.preventDefault();
    setError("");
    if (!idsInstructoresSeleccionados.length || !idPeriodoSeleccionado) {
      setError("Debes seleccionar al menos un instructor y un periodo.");
      return;
    }
    const periodoSel = periodos.find(
      (p) => String(p.id_periodo) === String(idPeriodoSeleccionado)
    );
    if (
      periodoSel &&
      String(periodoSel.estado || "").toLowerCase() !== "activo"
    ) {
      setError(
        "No se puede asignar: el periodo está desactivado. Elige un periodo activo."
      );
      return;
    }
    try {
      setGuardandoAsignacion(true);
      const errores = [];
      for (const idInst of idsInstructoresSeleccionados) {
        try {
          await crearFichaInstructor({
            id_ficha: fichaSeleccionada.id_ficha,
            id_instructor: Number(idInst),
            id_periodo: Number(idPeriodoSeleccionado),
            id_resultado: idResultadoSeleccionado
              ? Number(idResultadoSeleccionado)
              : null,
          });
        } catch (err) {
          const detalle = err.response?.data?.detail;
          const nombre =
            instructores.find((i) => Number(i.id_instructor) === Number(idInst))
              ?.nombre || `ID ${idInst}`;
          errores.push(
            `${nombre}: ${typeof detalle === "string" ? detalle : "error"}`
          );
        }
      }
      if (errores.length) {
        setError(
          errores.length === idsInstructoresSeleccionados.length
            ? errores.join(" · ")
            : `Algunos no se asignaron: ${errores.join(" · ")}`
        );
      } else {
        setMostrarAsignar(false);
        setIdsInstructoresSeleccionados([]);
        setIdPeriodoSeleccionado("");
        setIdResultadoSeleccionado("");
      }
      await abrirDetalle(fichaSeleccionada);
      await cargarDatos();
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(typeof detalle === "string" ? detalle : "Error al asignar instructor.");
    } finally {
      setGuardandoAsignacion(false);
    }
  };


  const manejarCargaMasiva = async (e) => {
    e.preventDefault();
    if (!archivoCarga) {
      setError("Selecciona un archivo CSV.");
      return;
    }
    try {
      setEnviandoCarga(true);
      setError("");
      setResultadoCarga(null);
      const fd = new FormData();
      fd.append("archivo", archivoCarga);
      if (periodoCarga) fd.append("id_periodo", periodoCarga);
      fd.append("enviar_correo", "true");
      const res = await cargaMasivaAprendices(fd);
      setResultadoCarga(res);
      setArchivoCarga(null);
      await cargarDatos();
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(typeof detalle === "string" ? detalle : "Error en la carga masiva.");
    } finally {
      setEnviandoCarga(false);
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


      <div className="form-inline-card" style={{ marginBottom: "1.5rem" }}>
        <h4><i className="bi bi-upload"></i> Carga masiva de aprendices (coordinación)</h4>
        <p className="subtitulo" style={{ marginBottom: 12 }}>
          Sube un CSV con columnas: <code>nombre,apellido,correo,numero_ficha</code>.
          Cada aprendiz queda asignado a su ficha y recibe correo con usuario y contraseña.
        </p>
        <form onSubmit={manejarCargaMasiva} className="form-inline-row" style={{ flexWrap: "wrap", gap: 12 }}>
          <div>
            <label>Archivo CSV</label>
            <input
              type="file"
              accept=".csv,.txt,.tsv"
              onChange={(e) => setArchivoCarga(e.target.files?.[0] || null)}
            />
          </div>
          <div>
            <label>Periodo (opcional)</label>
            <select value={periodoCarga} onChange={(e) => setPeriodoCarga(e.target.value)}>
              <option value="">Periodo activo</option>
              {periodos.filter((p) => String(p.estado).toLowerCase() === "activo").map((p) => (
                <option key={p.id_periodo} value={p.id_periodo}>{p.nombre}</option>
              ))}
            </select>
          </div>
          <div style={{ alignSelf: "flex-end" }}>
            <button type="submit" className="btn btn-success" disabled={enviandoCarga}>
              {enviandoCarga ? "Cargando..." : "Subir y enviar correos"}
            </button>
          </div>
        </form>
        {resultadoCarga && (
          <div style={{ marginTop: 12, padding: 12, background: "#f0fdf4", borderRadius: 8 }}>
            <strong>{resultadoCarga.mensaje}</strong>
            {resultadoCarga.detalle_errores?.length > 0 && (
              <ul style={{ marginTop: 8 }}>
                {resultadoCarga.detalle_errores.slice(0, 10).map((er, idx) => (
                  <li key={idx}>Fila {er.fila} ({er.correo}): {er.error}</li>
                ))}
              </ul>
            )}
          </div>
        )}
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
              <p><i className="bi bi-people"></i><span><strong>Aprendices:</strong> {aprendicesFicha.length}</span></p>

              <div className="detalle-aprendices" style={{ marginBottom: 20 }}>
                <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <p style={{ marginBottom: 0 }}>
                    <i className="bi bi-people-fill"></i>
                    <span><strong>Lista de aprendices</strong> (editar / desactivar)</span>
                  </p>
                  <button
                    type="button"
                    className="btn btn-success btn-sm btn-reenviar-correos"
                    disabled={enviandoCorreosFicha || aprendicesFicha.length === 0}
                    onClick={reenviarCorreos}
                    title="Envía usuario y contraseña temporal a todos los activos de esta ficha"
                  >
                    <i className="bi bi-envelope-arrow-up"></i>{" "}
                    {enviandoCorreosFicha ? "Enviando..." : "Enviar correos a la ficha"}
                  </button>
                </div>
                {cargandoDetalle && <p className="text-muted">Cargando aprendices...</p>}
                {!cargandoDetalle && aprendicesFicha.length === 0 && (
                  <p className="text-muted">Esta ficha no tiene aprendices. Usa la carga masiva CSV.</p>
                )}
                {!cargandoDetalle && aprendicesFicha.length > 0 && (
                  <div style={{ maxHeight: 320, overflowY: "auto", overflowX: "hidden", border: "1px solid #e5e7eb", borderRadius: 8 }}>
                    <table className="tabla-simple" style={{ width: "100%", margin: 0 }}>
                      <thead>
                        <tr>
                          <th>Nombre</th>
                          <th>Correo</th>
                          <th>Estado</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {aprendicesFicha.map((a) => (
                          <tr key={a.id_aprendiz} style={{ opacity: a.activo ? 1 : 0.65 }}>
                            <td>{a.nombre} {a.apellido}</td>
                            <td style={{ fontSize: "0.85rem" }}>{a.correo}</td>
                            <td>
                              <span className={`estado-badge ${a.activo ? "activo" : "inactivo"}`}>
                                {a.activo ? "Activo" : "Inactivo"}
                              </span>
                            </td>
                            <td className="acciones-tabla" style={{ whiteSpace: "nowrap" }}>
                              <button
                                type="button"
                                className="btn btn-sm btn-outline-primary"
                                title="Editar datos"
                                onClick={() => abrirEditarAprendiz(a)}
                              >
                                <i className="bi bi-pencil"></i>
                              </button>{" "}
                              <button
                                type="button"
                                className={`btn btn-sm ${a.activo ? "btn-outline-danger" : "btn-outline-success"}`}
                                title={a.activo ? "Desactivar (desertor)" : "Reactivar"}
                                onClick={() => toggleActivoAprendiz(a)}
                              >
                                <i className={`bi ${a.activo ? "bi-person-x" : "bi-person-check"}`}></i>
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {editAprendiz && (
                  <form
                    onSubmit={guardarAprendiz}
                    style={{ marginTop: 12, padding: 12, background: "#f0fdf4", borderRadius: 8 }}
                  >
                    <h5 style={{ marginTop: 0 }}>Editar aprendiz</h5>
                    {error && <div className="alert alert-danger">{error}</div>}
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                      <div>
                        <label className="form-label">Nombre</label>
                        <input
                          className="form-control"
                          value={formAprendiz.nombre}
                          onChange={(e) => setFormAprendiz({ ...formAprendiz, nombre: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <label className="form-label">Apellido</label>
                        <input
                          className="form-control"
                          value={formAprendiz.apellido}
                          onChange={(e) => setFormAprendiz({ ...formAprendiz, apellido: e.target.value })}
                          required
                        />
                      </div>
                      <div style={{ flex: 1, minWidth: 200 }}>
                        <label className="form-label">Correo</label>
                        <input
                          type="email"
                          className="form-control"
                          value={formAprendiz.correo}
                          onChange={(e) => setFormAprendiz({ ...formAprendiz, correo: e.target.value })}
                          required
                        />
                      </div>
                    </div>
                    <div style={{ marginTop: 10, display: "flex", gap: 8 }}>
                      <button type="submit" className="btn btn-success" disabled={guardandoAprendiz}>
                        {guardandoAprendiz ? "Guardando..." : "Guardar cambios"}
                      </button>
                      <button type="button" className="btn btn-secondary" onClick={() => setEditAprendiz(null)}>
                        Cancelar
                      </button>
                    </div>
                  </form>
                )}
              </div>

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
                    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                      <div>
                        <label className="form-label">
                          Instructores (marca varios a la vez)
                          {idsInstructoresSeleccionados.length > 0 && (
                            <span style={{ marginLeft: 8, fontWeight: 400, color: "#0d6efd" }}>
                              {idsInstructoresSeleccionados.length} seleccionado(s)
                            </span>
                          )}
                        </label>
                        <div
                          style={{
                            maxHeight: 180,
                            overflowY: "auto",
                            border: "1px solid #ced4da",
                            borderRadius: 6,
                            padding: "8px 12px",
                            background: "#fff",
                          }}
                        >
                          {instructores.length === 0 && (
                            <span className="text-muted">No hay instructores registrados</span>
                          )}
                          {instructores.map((inst) => (
                            <label
                              key={inst.id_instructor}
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 8,
                                padding: "4px 0",
                                cursor: "pointer",
                              }}
                            >
                              <input
                                type="checkbox"
                                checked={idsInstructoresSeleccionados.includes(
                                  inst.id_instructor
                                )}
                                onChange={() =>
                                  toggleInstructorCheck(inst.id_instructor)
                                }
                              />
                              <span>
                                {inst.nombre} {inst.apellido}
                              </span>
                            </label>
                          ))}
                        </div>
                      </div>
                      <div style={{ display: "flex", gap: 10, alignItems: "flex-end", flexWrap: "wrap" }}>
                        <div style={{ flex: 1, minWidth: 160 }}>
                          <label className="form-label">Periodo</label>
                          <select
                            className="form-select"
                            value={idPeriodoSeleccionado}
                            onChange={(e) => setIdPeriodoSeleccionado(e.target.value)}
                            required
                          >
                            <option value="">Selecciona periodo</option>
                            {periodos.map((p) => {
                              const activo =
                                String(p.estado || "").toLowerCase() === "activo";
                              return (
                                <option
                                  key={p.id_periodo}
                                  value={p.id_periodo}
                                  disabled={!activo}
                                >
                                  {p.nombre} {activo ? "(Activo)" : "(No activo)"}
                                </option>
                              );
                            })}
                          </select>
                        </div>
                        <div style={{ flex: 1, minWidth: 200 }}>
                          <label className="form-label">
                            Resultado de aprendizaje (de esta ficha)
                          </label>
                          <select
                            className="form-select"
                            value={idResultadoSeleccionado}
                            onChange={(e) => setIdResultadoSeleccionado(e.target.value)}
                          >
                            <option value="">Sin RA / seleccionar</option>
                            {resultadosRA.map((r) => (
                              <option key={r.id_resultado} value={r.id_resultado}>
                                {r.codigo ? `${r.codigo} — ` : ""}
                                {r.nombre}
                              </option>
                            ))}
                          </select>
                          <small className="text-muted">
                            Solo aplica a esta ficha y periodo (1 RA por trimestre).
                          </small>
                        </div>
                        <button
                          type="submit"
                          className="btn btn-success"
                          disabled={guardandoAsignacion}
                        >
                          {guardandoAsignacion
                            ? "Guardando..."
                            : `Asignar${
                                idsInstructoresSeleccionados.length > 1
                                  ? ` (${idsInstructoresSeleccionados.length})`
                                  : ""
                              }`}
                        </button>
                      </div>
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
                      <li key={`${inst.id_instructor}-${inst.id_periodo || inst.id_relacion}`} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
                        <span>
                          <i className="bi bi-person-fill"></i>
                          {inst.nombre} {inst.apellido} —{" "}
                          {inst.nombre_resultado || (inst.resultados_aprendizaje || []).map((c) => c.nombre).join(", ") || "sin RA"} · {inst.nombre_periodo || ""}
                        </span>
                        <button className="btn btn-sm btn-outline-danger"
                          onClick={() => {
                            listarInstructoresPorFicha(fichaSeleccionada.id_ficha).then((rels) => {
                              if (inst.id_relacion) manejarDesasignarInstructor(inst.id_relacion);
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