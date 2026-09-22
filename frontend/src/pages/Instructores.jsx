import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listarInstructores, eliminarInstructor, obtenerInstructor, resetPrimerAccesoInstructor, reactivarInstructor } from "../services/instructorService";
import { resolverPeriodoOperativoAprendiz } from "../utils/periodoAprendiz";
import { esAdmin as esAdminSesion, obtenerUsuarioSesion } from "../utils/sesion";
import "../styles/Instructores.css";

function Instructores() {
  const navigate = useNavigate();
  const esAdmin = esAdminSesion();

  const [instructores, setInstructores] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [mostrarInactivos, setMostrarInactivos] = useState(false);
  const [busqueda, setBusqueda] = useState("");

  const cargarInstructores = async () => {
    try {
      setCargando(true);
      setError("");

      if (esAdmin) {
        // Trae todos; la vista muestra solo activos o solo inactivos
        const datos = await listarInstructores(true);
        const filtrados = (datos || []).filter((inst) =>
          mostrarInactivos ? inst.activo === false : inst.activo !== false
        );
        setInstructores(filtrados);
      } else {
        const usuario = obtenerUsuarioSesion();
        if (!usuario || !usuario.id_ficha) {
          setError("No se encontró la ficha del aprendiz.");
          setCargando(false);
          return;
        }
        const contexto = await resolverPeriodoOperativoAprendiz(
          usuario.id_ficha,
          usuario.id_periodo
        );
        if (contexto.sinPeriodoActivo) {
          setError(contexto.mensaje || "No hay periodo activo.");
          setInstructores([]);
          setCargando(false);
          return;
        }
        const asignaciones = contexto.asignaciones || [];
        const detalles = await Promise.all(
          asignaciones.map((a) => obtenerInstructor(a.id_instructor).catch(() => null))
        );
        setInstructores(detalles.filter(Boolean));
      }
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar los instructores.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarInstructores();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mostrarInactivos]);

  const manejarEliminar = async (id) => {
    if (
      window.confirm(
        "¿Desactivar este instructor?\nNo se borrarán sus datos ni evaluaciones. Podrás reactivarlo cuando regrese."
      )
    ) {
      try {
        await eliminarInstructor(id);
        await cargarInstructores();
      } catch (err) {
        const d = err.response?.data?.detail;
        const msg = Array.isArray(d)
          ? d[0]?.msg || JSON.stringify(d)
          : d || "Error al desactivar el instructor.";
        alert(msg);
      }
    }
  };

  const manejarReactivar = async (id, nombre) => {
    if (!window.confirm(`¿Reactivar a ${nombre}? Volverá a aparecer y podrá iniciar sesión.`)) {
      return;
    }
    try {
      await reactivarInstructor(id);
      await cargarInstructores();
      alert("Instructor reactivado.");
    } catch (err) {
      const d = err.response?.data?.detail;
      alert(typeof d === "string" ? d : "No se pudo reactivar.");
    }
  };

  const manejarResetPrimerAcceso = async (id, nombre) => {
    if (
      !window.confirm(
        `¿Resetear primer acceso de ${nombre}?\nAl iniciar sesión pedirá código (consola del backend) y crear contraseña.`
      )
    ) {
      return;
    }
    try {
      const res = await resetPrimerAccesoInstructor(id);
      alert(res.mensaje || "Primer acceso restablecido.");
    } catch (err) {
      const d = err.response?.data?.detail;
      alert(typeof d === "string" ? d : "No se pudo resetear el primer acceso.");
    }
  };

  const texto = busqueda.toLowerCase().trim();
  const instructoresFiltrados = instructores.filter((inst) => {
    if (!texto) return true;
    const nombresCompetencias = (inst.competencias || [])
      .map((c) => c.nombre)
      .join(" ")
      .toLowerCase();
    return (
      `${inst.nombre} ${inst.apellido}`.toLowerCase().includes(texto) ||
      nombresCompetencias.includes(texto) ||
      (inst.correo || "").toLowerCase().includes(texto)
    );
  });

  return (
    <div className="pagina-instructores">
      <div className="encabezado">
        <div>
          <h1 className="titulo">Gestión de Instructores</h1>
          <p className="subtitulo">
            Administra, consulta y actualiza los instructores registrados
          </p>
          {esAdmin && (
            <div
              style={{
                display: "inline-flex",
                marginTop: 12,
                borderRadius: 10,
                overflow: "hidden",
                border: "1px solid #d1d5db",
              }}
            >
              <button
                type="button"
                onClick={() => setMostrarInactivos(false)}
                style={{
                  padding: "8px 16px",
                  border: "none",
                  cursor: "pointer",
                  fontWeight: 600,
                  background: !mostrarInactivos ? "#39a900" : "#fff",
                  color: !mostrarInactivos ? "#fff" : "#374151",
                }}
              >
                <i className="bi bi-person-check"></i> Activos
              </button>
              <button
                type="button"
                onClick={() => setMostrarInactivos(true)}
                style={{
                  padding: "8px 16px",
                  border: "none",
                  borderLeft: "1px solid #d1d5db",
                  cursor: "pointer",
                  fontWeight: 600,
                  background: mostrarInactivos ? "#6b7280" : "#fff",
                  color: mostrarInactivos ? "#fff" : "#374151",
                }}
              >
                <i className="bi bi-person-x"></i> Inactivos
              </button>
            </div>
          )}
        </div>
        {esAdmin && (
          <button className="btn-nuevo" onClick={() => navigate("/instructores/crear")}>
            <i className="bi bi-plus-circle"></i> Nuevo Instructor
          </button>
        )}
      </div>

      <div className="barra-superior">
        <div className="buscador">
          <span className="buscador-icono"><i className="bi bi-search"></i></span>
          <input
            type="text"
            placeholder="Buscar instructor..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>
      </div>

      {cargando && <p className="text-muted">Cargando instructores...</p>}
      {error && <p className="form-mensaje-error">{error}</p>}

      {!cargando && !error && instructoresFiltrados.length === 0 && (
        <div className="estado-vacio">
          <i className="bi bi-search"></i>
          <h4>No se encontraron instructores</h4>
          <p>{instructores.length === 0
            ? (mostrarInactivos ? "No hay instructores inactivos." : "Aún no hay instructores activos.")
            : "Intenta con otro término de búsqueda"}</p>
        </div>
      )}

      {!cargando && instructoresFiltrados.length > 0 && (
        <div className="grid-instructores">
          {instructoresFiltrados.map((inst) => (
            <div className="instructor-card" key={inst.id_instructor}>
              <div className="perfil">
                {inst.foto ? (
                  <img
                    className="foto"
                    src={`http://127.0.0.1:8000${inst.foto}`}
                    alt={inst.nombre}
                    onError={(e) => {
                      e.target.style.display = "none";
                      e.target.parentElement.innerHTML = '<div class="foto-placeholder"><i class="bi bi-person-fill"></i></div>';
                    }}
                  />
                ) : (
                  <div className="foto-placeholder"><i className="bi bi-person-fill"></i></div>
                )}
                <div>
                  <h4>{inst.nombre} {inst.apellido}</h4>
                  <div className="badges-competencias">
                    {(inst.competencias || []).map((c) => (
                      <span className="badge-competencia" key={c.id_competencia}>{c.nombre}</span>
                    ))}
                  </div>
                </div>
              </div>
              <hr />
              <p><i className="bi bi-envelope"></i> {inst.correo}</p>
              <p><i className="bi bi-telephone"></i> {inst.telefono}</p>
              {esAdmin && (
                <div className="acciones">
                  <button className="btn-editar" title="Editar" onClick={() => navigate(`/instructores/editar/${inst.id_instructor}`)}>
                    <i className="bi bi-pencil"></i>
                  </button>
                  <button
                    className="btn-editar-icon"
                    title="Resetear primer acceso"
                    onClick={() => manejarResetPrimerAcceso(inst.id_instructor, `${inst.nombre} ${inst.apellido}`)}
                  >
                    <i className="bi bi-key"></i>
                  </button>
                  {inst.activo === false ? (
                    <button
                      className="btn-editar-icon"
                      title="Reactivar"
                      onClick={() => manejarReactivar(inst.id_instructor, `${inst.nombre} ${inst.apellido}`)}
                    >
                      <i className="bi bi-person-check"></i>
                    </button>
                  ) : (
                    <button
                      className="btn-eliminar-icon"
                      title="Desactivar"
                      onClick={() => manejarEliminar(inst.id_instructor)}
                    >
                      <i className="bi bi-person-x"></i>
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Instructores;