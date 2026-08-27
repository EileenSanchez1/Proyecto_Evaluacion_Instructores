import { useEffect, useState } from "react";
import {
  listarHorarios,
  crearHorario,
  actualizarHorario,
  eliminarHorario,
} from "../services/horarioService";
import { listarInstructores } from "../services/instructorService";
import { listarFichas } from "../services/FichaServices";
import "../styles/Estructura.css";

const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

const FORMULARIO_VACIO = {
  id_instructor: "",
  id_ficha: "",
  dia: "Lunes",
  hora_inicio: "07:00",
  hora_fin: "09:00",
};

function Horarios() {
  const [horarios, setHorarios] = useState([]);
  const [instructores, setInstructores] = useState([]);
  const [fichas, setFichas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [editandoId, setEditandoId] = useState(null);
  const [formulario, setFormulario] = useState(FORMULARIO_VACIO);

  const cargar = async () => {
    try {
      setCargando(true);
      setError("");

      const [h, i, f] = await Promise.all([
        listarHorarios(),
        listarInstructores(),
        listarFichas(),
      ]);

      setHorarios(h);
      setInstructores(i);
      setFichas(f);
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar los horarios.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  const nombreInstructor = (id) => {
    const inst = instructores.find((i) => i.id_instructor === id);
    return inst ? `${inst.nombre} ${inst.apellido}` : `#${id}`;
  };

  const numeroFicha = (id) => {
    const ficha = fichas.find((f) => f.id_ficha === id);
    return ficha ? ficha.numero_ficha : `#${id}`;
  };

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario({ ...formulario, [name]: value });
  };

  const iniciarEdicion = (horario) => {
    setEditandoId(horario.id_horario);
    setFormulario({
      id_instructor: horario.id_instructor,
      id_ficha: horario.id_ficha,
      dia: horario.dia,
      hora_inicio: horario.hora_inicio.slice(0, 5),
      hora_fin: horario.hora_fin.slice(0, 5),
    });
  };

  const cancelarEdicion = () => {
    setEditandoId(null);
    setFormulario(FORMULARIO_VACIO);
  };

  const manejarEnvio = async (e) => {
    e.preventDefault();
    setError("");

    if (!formulario.id_instructor || !formulario.id_ficha) {
      setError("Selecciona un instructor y una ficha.");
      return;
    }

    const payload = {
      ...formulario,
      id_instructor: Number(formulario.id_instructor),
      id_ficha: Number(formulario.id_ficha),
    };

    try {
      if (editandoId) {
        await actualizarHorario(editandoId, payload);
      } else {
        await crearHorario(payload);
      }

      cancelarEdicion();
      await cargar();
    } catch (err) {
      console.error(err);
      // Aquí llega, por ejemplo, el mensaje de cruce de horarios
      // que arma HorarioService en el backend.
      setError(err.response?.data?.detail || "No se pudo guardar el horario.");
    }
  };

  const manejarEliminar = async (id) => {
    if (!window.confirm("¿Eliminar este horario?")) return;

    try {
      await eliminarHorario(id);
      await cargar();
    } catch (err) {
      console.error(err);
      alert("No se pudo eliminar el horario.");
    }
  };

  return (
    <div className="pagina-estructura">
      <div className="encabezado">
        <div>
          <h1 className="titulo">Horarios</h1>
          <p className="subtitulo">
            Asigna horarios de instructores por ficha. El sistema impide
            cruces de horario para un mismo instructor.
          </p>
        </div>
      </div>

      <div className="form-inline-card">
        <h4>{editandoId ? "Editar horario" : "Nuevo horario"}</h4>
        {error && <div className="form-mensaje-error">{error}</div>}
        <form onSubmit={manejarEnvio} className="form-inline-row">
          <div>
            <label>Instructor *</label>
            <select name="id_instructor" value={formulario.id_instructor} onChange={manejarCambio}>
              <option value="">Selecciona...</option>
              {instructores.map((i) => (
                <option key={i.id_instructor} value={i.id_instructor}>
                  {i.nombre} {i.apellido}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Ficha *</label>
            <select name="id_ficha" value={formulario.id_ficha} onChange={manejarCambio}>
              <option value="">Selecciona...</option>
              {fichas.map((f) => (
                <option key={f.id_ficha} value={f.id_ficha}>
                  {f.numero_ficha}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Día *</label>
            <select name="dia" value={formulario.dia} onChange={manejarCambio}>
              {DIAS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Hora inicio *</label>
            <input
              type="time"
              name="hora_inicio"
              value={formulario.hora_inicio}
              onChange={manejarCambio}
            />
          </div>
          <div>
            <label>Hora fin *</label>
            <input
              type="time"
              name="hora_fin"
              value={formulario.hora_fin}
              onChange={manejarCambio}
            />
          </div>
          <div>
            <button type="submit" className="btn-submit-form">
              {editandoId ? "Guardar cambios" : "Crear"}
            </button>
          </div>
          {editandoId && (
            <div>
              <button type="button" className="btn-cancel-form" onClick={cancelarEdicion}>
                Cancelar
              </button>
            </div>
          )}
        </form>
      </div>

      {cargando && <p className="text-muted">Cargando horarios...</p>}

      {!cargando && (
        <table className="tabla-simple">
          <thead>
            <tr>
              <th>Instructor</th>
              <th>Ficha</th>
              <th>Día</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {horarios.map((h) => (
              <tr key={h.id_horario}>
                <td>{nombreInstructor(h.id_instructor)}</td>
                <td>{numeroFicha(h.id_ficha)}</td>
                <td>{h.dia}</td>
                <td>{h.hora_inicio.slice(0, 5)}</td>
                <td>{h.hora_fin.slice(0, 5)}</td>
                <td className="acciones-tabla">
                  <button className="editar" onClick={() => iniciarEdicion(h)}>
                    <i className="bi bi-pencil"></i>
                  </button>
                  <button className="eliminar" onClick={() => manejarEliminar(h.id_horario)}>
                    <i className="bi bi-trash"></i>
                  </button>
                </td>
              </tr>
            ))}
            {horarios.length === 0 && (
              <tr>
                <td colSpan="6" className="text-muted">
                  Aún no hay horarios registrados.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Horarios;
