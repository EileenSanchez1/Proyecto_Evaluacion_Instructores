import { NavLink } from "react-router-dom";
import { esAdmin } from "../utils/sesion";
import "../styles/Layout.css";

function Sidebar() {
  const admin = esAdmin();

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

        {/* Igual que en el Flask original: Preguntas, Fichas y Reportes
            son exclusivos del admin */}
        {admin && (
          <NavLink
            to="/preguntas"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <i className="bi bi-journal-bookmark"></i> Preguntas
          </NavLink>
        )}

        {admin && (
          <NavLink
            to="/fichas"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <i className="bi bi-card-text"></i> Fichas
          </NavLink>
        )}

        {admin && (
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
