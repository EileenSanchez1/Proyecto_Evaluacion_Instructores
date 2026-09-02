import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listarInstructoresPorFichaYPeriodo } from "../services/Fichainstructorservice";
import { obtenerInstructor } from "../services/instructorService";
import { iniciarEvaluacion, listarEvaluaciones } from "../services/Evaluacionservice";
import { listarPreguntasActivas } from "../services/Preguntaservice";
import { obtenerUsuarioSesion, esAdmin } from "../utils/sesion";
import { historialEvaluaciones } from "../services/Reporteservice";
import "../styles/Evaluaciones.css";

function Evaluaciones() {
  const navigate = useNavigate();
  const usuario = obtenerUsuarioSesion();
  const esAdminUser = esAdmin();

  const [instructores, setInstructores] = useState([]);
  const [evaluaciones, setEvaluaciones] = useState([]);
  const [preguntas, setPreguntas] = useState([]);
  const [historial, setHistorial] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        setCargando(true);
        setError("");

        if (esAdminUser) {
          // Admin ve historial de evaluaciones
          const hist = await historialEvaluaciones();
          setHistorial(hist);
        } else {
          // Aprendiz ve instructores de su ficha/periodo
          if (!usuario?.id_ficha || !usuario?.id_periodo || !usuario?.id_aprendiz) {
            setError("No se encontró información completa del aprendiz.");
            setCargando(false);
            return;
          }

          const [asignaciones, evals, p] = await Promise.all([
            listarInstructoresPorFichaYPeriodo(usuario.id_ficha, usuario.id_periodo),
            listarEvaluaciones(),
            listarPreguntasActivas()
          ]);

          const detalles = await Promise.all(
            asignaciones.map((a) => obtenerInstructor(a.id_instructor).catch(() => null))
          );

          // Filtrar evaluaciones del aprendiz actual
          const misEvals = evals.filter((e) => e.id_aprendiz === usuario.id_aprendiz);

          setInstructores(detalles.filter(Boolean));
          setEvaluaciones(misEvals);
          setPreguntas(p);
        }
      } catch (err) {
        console.error(err);
        setError("No se pudieron cargar los datos.");
      } finally {
        setCargando(false);
      }
    };

    cargarDatos();
  }, []);

  const obtenerEstadoInstructor = (idInstructor) => {
    const ev = evaluaciones.find(
      (e) => e.id_instructor === idInstructor && e.id_periodo === usuario.id_periodo
    );
    if (!ev) return { estado: "Pendiente", id_evaluacion: null };
    return { estado: ev.estado, id_evaluacion: ev.id_evaluacion };
  };

  const manejarEvaluar = async (idInstructor) => {
    try {
      const ev = await iniciarEvaluacion(usuario.id_aprendiz, idInstructor, usuario.id_periodo);
      navigate(`/evaluaciones/${ev.id_evaluacion}`);
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(typeof detalle === "string" ? detalle : "Error al iniciar la evaluación.");
    }
  };

  const manejarVerResultado = (idEvaluacion) => {
    navigate(`/evaluaciones/${idEvaluacion}`);
  };

  if (cargando) {
    return (
      <div className="pagina-evaluaciones">
        <p className="text-muted">Cargando...</p>
      </div>
    );
  }

  return (
    <div className="pagina-evaluaciones">
      <div className="encabezado">
        <div>
          <h1 className="titulo">
            {esAdminUser ? "Historial de Evaluaciones" : "Evaluación de Instructores"}
          </h1>
          <p className="subtitulo">
            {esAdminUser
              ? "Consulta el historial completo de evaluaciones realizadas"
              : "Evalúa a los instructores asignados a tu ficha de formación"}
          </p>
        </div>
      </div>

      {error && <div className="alerta alerta-error">{error}</div>}

      {esAdminUser ? (
        // Vista Admin
        <div className="tabla-historial">
          {historial.length === 0 ? (
            <div className="estado-vacio">
              <i className="bi bi-clipboard-data"></i>
              <h4>No hay evaluaciones registradas</h4>
            </div>
          ) : (
            <table className="tabla">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Periodo</th>
                  <th>Aprendiz</th>
                  <th>Ficha</th>
                  <th>Instructor</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {historial.map((h) => (
                  <tr key={h.id_evaluacion}>
                    <td>{new Date(h.fecha).toLocaleDateString()}</td>
                    <td>{h.periodo}</td>
                    <td>{h.aprendiz}</td>
                    <td>{h.ficha}</td>
                    <td>{h.instructor}</td>
                    <td>
                      <span className={`badge-estado ${h.estado.toLowerCase()}`}>
                        {h.estado}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      ) : (
        // Vista Aprendiz
        <>
          {preguntas.length === 0 && (
            <div className="alerta alerta-warning">
              <i className="bi bi-exclamation-triangle"></i>
              Aún no hay preguntas de evaluación configuradas. Contacta al administrador.
            </div>
          )}

          {instructores.length === 0 ? (
            <div className="estado-vacio">
              <i className="bi bi-search"></i>
              <h4>No tienes instructores asignados</h4>
              <p>Contacta al coordinador para que te asigne instructores a tu ficha.</p>
            </div>
          ) : (
            <div className="grid-evaluaciones">
              {instructores.map((inst) => {
                const { estado, id_evaluacion } = obtenerEstadoInstructor(inst.id_instructor);
                const yaEvaluado = estado === "Evaluado";

                return (
                  <div className="evaluacion-card" key={inst.id_instructor}>
                    <div className="perfil">
                      {inst.foto ? (
                        <img className="foto" src={`http://localhost:8000${inst.foto}`} alt={inst.nombre} />
                      ) : (
                        <div className="foto-placeholder">
                          <i className="bi bi-person-fill"></i>
                        </div>
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

                    <div className="estado-evaluacion">
                      <span className={`badge-estado ${yaEvaluado ? "evaluado" : "pendiente"}`}>
                        {yaEvaluado ? "Evaluado" : "Pendiente"}
                      </span>
                    </div>

                    <button
                      className={yaEvaluado ? "btn-ver" : "btn-evaluar"}
                      onClick={() => yaEvaluado ? manejarVerResultado(id_evaluacion) : manejarEvaluar(inst.id_instructor)}
                    >
                      <i className={`bi ${yaEvaluado ? "bi-eye" : "bi-pencil-square"}`}></i>
                      {yaEvaluado ? "Ver resultado" : "Evaluar"}
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Evaluaciones;
