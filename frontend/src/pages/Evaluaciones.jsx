import { useEffect, useState, useMemo } from "react";
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

  // Leer usuario UNA SOLA VEZ al montar el componente
  const [usuario] = useState(() => obtenerUsuarioSesion());
  const esAdminUser = useMemo(() => esAdmin(), []);

  const [instructores, setInstructores] = useState([]);
  const [evaluaciones, setEvaluaciones] = useState([]);
  const [preguntas, setPreguntas] = useState([]);
  const [historial, setHistorial] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelado = false;

    const cargarDatos = async () => {
      try {
        if (cancelado) return;
        setCargando(true);
        setError("");

        if (esAdminUser) {
          const hist = await historialEvaluaciones();
          if (!cancelado) setHistorial(hist);
        } else {
          const idFicha = usuario?.id_ficha;
          const idPeriodo = usuario?.id_periodo;

          if (!idFicha) {
            setError("No tienes una ficha de formación asignada. Contacta al coordinador.");
            setCargando(false);
            return;
          }

          const [fichaInstructores, evals, p] = await Promise.all([
            listarInstructoresPorFichaYPeriodo(idFicha, idPeriodo || 1),
            listarEvaluaciones(),
            listarPreguntasActivas()
          ]);

          // Obtener datos completos de cada instructor
          const instructoresCompletos = await Promise.all(
            fichaInstructores.map(async (fi) => {
              try {
                const inst = await obtenerInstructor(fi.id_instructor);
                return { ...inst, id_ficha_instructor: fi.id_ficha_instructor };
              } catch {
                return null;
              }
            })
          );

          if (!cancelado) {
            setInstructores(instructoresCompletos.filter(Boolean));
            setEvaluaciones(evals);
            setPreguntas(p);
          }
        }
      } catch (err) {
        console.error(err);
        if (!cancelado) setError("Error al cargar los datos.");
      } finally {
        if (!cancelado) setCargando(false);
      }
    };

    cargarDatos();

    return () => { cancelado = true; };
  }, [esAdminUser]); // <- SOLO depende de esAdminUser, NO de usuario

  const obtenerEstadoInstructor = (idInstructor) => {
    const ev = evaluaciones.find(
      (e) => e.id_instructor === idInstructor && e.id_aprendiz === usuario?.id_aprendiz
    );
    return ev ? { estado: ev.estado, id_evaluacion: ev.id_evaluacion } : { estado: "Pendiente", id_evaluacion: null };
  };

  const manejarEvaluar = async (idInstructor) => {
    try {
      const idPeriodo = usuario?.id_periodo || 1;
      const ev = await iniciarEvaluacion(usuario.id_aprendiz, idInstructor, idPeriodo);
      navigate(`/evaluaciones/responder/${ev.id_evaluacion}`);
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
        <div className="cargando-centrado">
          <div className="spinner"></div>
          <p>Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pagina-evaluaciones">
      <div className="encabezado-evaluacion">
        <div>
          <h1 className="titulo-principal">
            {esAdminUser ? "Historial de Evaluaciones" : "Evaluación de Instructores"}
          </h1>
          <p className="subtitulo-principal">
            {esAdminUser
              ? "Consulta el historial completo de evaluaciones realizadas"
              : "Evalúa a los instructores asignados a tu ficha de formación"}
          </p>
        </div>
      </div>

      {error && <div className="alerta alerta-error">{error}</div>}

      {esAdminUser ? (
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
                    <div className="card-header">
                      <div className="card-foto-wrap">
                        {inst.foto ? (
                          <img className="card-foto" src={`http://localhost:8000${inst.foto}`} alt={inst.nombre} />
                        ) : (
                          <div className="card-foto-placeholder">
                            <i className="bi bi-person-fill"></i>
                          </div>
                        )}
                      </div>
                      <div className="card-info">
                        <h4>{inst.nombre} {inst.apellido}</h4>
                        <p className="card-email"><i className="bi bi-envelope"></i> {inst.correo}</p>
                        {inst.telefono && <p className="card-tel"><i className="bi bi-telephone"></i> {inst.telefono}</p>}
                      </div>
                    </div>

                    <div className="card-competencias">
                      {(inst.competencias || []).slice(0, 3).map((c) => (
                        <span className="badge-competencia" key={c.id_competencia}>{c.nombre}</span>
                      ))}
                      {(inst.competencias || []).length > 3 && (
                        <span className="badge-competencia mas">+{(inst.competencias || []).length - 3}</span>
                      )}
                    </div>

                    <div className="card-footer">
                      <span className={`badge-estado ${yaEvaluado ? "evaluado" : "pendiente"}`}>
                        {yaEvaluado ? "Evaluado" : "Pendiente"}
                      </span>
                      <button
                        className={yaEvaluado ? "btn-ver" : "btn-evaluar"}
                        onClick={() => yaEvaluado ? manejarVerResultado(id_evaluacion) : manejarEvaluar(inst.id_instructor)}
                      >
                        <i className={`bi ${yaEvaluado ? "bi-eye" : "bi-pencil-square"}`}></i>
                        {yaEvaluado ? "Ver resultado" : "Evaluar"}
                      </button>
                    </div>
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
