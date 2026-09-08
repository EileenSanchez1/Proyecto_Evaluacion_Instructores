import { NavLink } from "react-router-dom";
import { esAdmin, esAdminOCoordinador, esInstructor, obtenerUsuarioSesion } from "../utils/sesion";
import "../styles/Layout.css";

function Sidebar() {
  const admin = esAdmin();
  const adminOCoordinador = esAdminOCoordinador();
  const instructor = esInstructor ? esInstructor() : obtenerUsuarioSesion()?.rol === "INSTRUCTOR";

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img src="/imgs/logo-sena.png" alt="Logo SENA" className="logo-mark" />
        <div className="logo-text">
          <strong>SENA</strong>
          <span>Evaluación de Instructores</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink
          to="/"
          end
          className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
        >
          <i className="bi bi-house"></i> Inicio
        </NavLink>

        {/* Enlaces exclusivos o de interés para Instructor */}
        {instructor && (
          <>
            <NavLink
              to="/perfil-instructor"
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            >
              <i className="bi bi-person-badge"></i> Mi Perfil
            </NavLink>
            <NavLink
              to="/mi-promedio"
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            >
              <i className="bi bi-graph-up-arrow"></i> Mi Promedio
            </NavLink>
          </>
        )}

        <NavLink
          to="/instructores"
          className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
        >
          <i className="bi bi-people"></i> Instructores
        </NavLink>

        <NavLink
          to="/evaluaciones"
          className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
        >
          <i className="bi bi-clipboard-check"></i> Evaluaciones
        </NavLink>

        {admin && (
          <NavLink
            to="/preguntas"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <i className="bi bi-journal-bookmark"></i> Preguntas
          </NavLink>
        )}

        {adminOCoordinador && (
          <>
            <NavLink
              to="/fichas"
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            >
              <i className="bi bi-card-text"></i> Fichas
            </NavLink>

            <NavLink
              to="/competencias"
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            >
              <i className="bi bi-award"></i> Competencias
            </NavLink>

            <NavLink
              to="/horarios"
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            >
              <i className="bi bi-calendar-week"></i> Horarios
            </NavLink>

            <NavLink
              to="/periodos"
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            >
              <i className="bi bi-calendar-range"></i> Periodos
            </NavLink>

            <NavLink
              to="/historial"
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            >
              <i className="bi bi-clock-history"></i> Historial
            </NavLink>

            <NavLink
              to="/reportes"
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            >
              <i className="bi bi-bar-chart"></i> Reportes
            </NavLink>
          </>
        )}

        <NavLink
          to="/contacto"
          className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
        >
          <i className="bi bi-envelope"></i> Contacto
        </NavLink>
      </nav>
    </aside>
  );
}

export default Sidebar;