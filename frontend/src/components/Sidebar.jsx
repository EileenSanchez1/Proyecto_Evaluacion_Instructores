import { NavLink } from "react-router-dom";
import { esAdmin, esAdminOCoordinador } from "../utils/sesion";
import "../styles/Layout.css";

function Sidebar() {
  const admin = esAdmin();
  const adminOCoordinador = esAdminOCoordinador();

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

        {/* Preguntas: exclusivo de Administrador */}
        {admin && (
          <NavLink
            to="/preguntas"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <i className="bi bi-journal-bookmark"></i> Preguntas
          </NavLink>
        )}

        {/* Fichas, Competencias, Horarios y Reportes: Administrador o Coordinador,
            igual que exige el backend (require_roles) */}
        {adminOCoordinador && (
          <NavLink
            to="/fichas"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <i className="bi bi-card-text"></i> Fichas
          </NavLink>
        )}

        {adminOCoordinador && (
          <NavLink
            to="/competencias"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <i className="bi bi-award"></i> Competencias
          </NavLink>
        )}

        {adminOCoordinador && (
          <NavLink
            to="/horarios"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <i className="bi bi-calendar-week"></i> Horarios
          </NavLink>
        )}

        {adminOCoordinador && (
          <NavLink
            to="/reportes"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <i className="bi bi-bar-chart"></i> Reportes
          </NavLink>
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
