import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listarInstructores, eliminarInstructor, obtenerInstructor } from "../services/instructorService";
import { listarInstructoresPorFicha } from "../services/Fichainstructorservice";
import { esAdmin as esAdminSesion } from "../utils/sesion";
import "../styles/Instructores.css";

function Instructores() {
  const navigate = useNavigate();
  const esAdmin = esAdminSesion();

  const [instructores, setInstructores] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [busqueda, setBusqueda] = useState("");

  const cargarInstructores = async () => {
    try {
      setCargando(true);
      setError("");

      if (esAdmin) {
        // El admin ve todos los instructores registrados
        const datos = await listarInstructores();
        setInstructores(datos);
      } else {
        // El aprendiz solo ve los instructores asignados a su ficha
        const asignaciones = await listarInstructoresPorFicha(aprendiz.id_ficha);

        const detalles = await Promise.all(
          asignaciones.map((asignacion) =>
            obtenerInstructor(asignacion.id_instructor).catch(() => null)
          )
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
  }, []);

  const manejarEliminar = async (id) => {
    if (window.confirm("¿Está seguro de eliminar este instructor?")) {
      try {
        await eliminarInstructor(id);
        setInstructores(instructores.filter((inst) => inst.id_instructor !== id));
      } catch (err) {
        console.error(err);
        alert("Error al intentar eliminar el instructor.");
      }
    }
  };

  const texto = busqueda.toLowerCase().trim();
  const instructoresFiltrados = instructores.filter((inst) => {
    if (!texto) return true;
    return (
      `${inst.nombre} ${inst.apellido}`.toLowerCase().includes(texto) ||
      (inst.competencia || "").toLowerCase().includes(texto) ||
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
        </div>

        {esAdmin && (
          <button className="btn-nuevo" onClick={() => navigate("/instructores/crear")}>
            <i className="bi bi-plus-circle"></i>
            Nuevo Instructor
          </button>
        )}
      </div>

      <div className="barra-superior">
        <div className="buscador">
          <span className="buscador-icono">
            <i className="bi bi-search"></i>
          </span>
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
          <p>{instructores.length === 0 ? "Aún no hay instructores registrados." : "Intenta con otro término de búsqueda"}</p>
        </div>
      )}

      {!cargando && instructoresFiltrados.length > 0 && (
        <div className="grid-instructores">
          {instructoresFiltrados.map((inst) => (
            <div className="instructor-card" key={inst.id_instructor}>
              <div className="perfil">
                {inst.foto ? (
                  <img src={inst.foto} alt={inst.nombre} className="foto" />
                ) : (
                  <div className="foto-placeholder">
                    <i className="bi bi-person-fill"></i>
                  </div>
                )}
                <div>
                  <h4>
                    {inst.nombre} {inst.apellido}
                  </h4>
                  <span className="badge-competencia">{inst.competencia}</span>
                </div>
              </div>
              <hr />
              <p>
                <i className="bi bi-envelope"></i> {inst.correo}
              </p>
              <p>
                <i className="bi bi-telephone"></i> {inst.telefono}
              </p>

              {esAdmin && (
                <div className="acciones">
                  <button
                    className="btn-editar"
                    title="Editar"
                    onClick={() => navigate(`/instructores/editar/${inst.id_instructor}`)}
                  >
                    <i className="bi bi-pencil"></i>
                  </button>
                  <button
                    className="btn-eliminar-icon"
                    title="Eliminar"
                    onClick={() => manejarEliminar(inst.id_instructor)}
                  >
                    <i className="bi bi-trash"></i>
                  </button>
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
