import { NavLink } from "react-router-dom";
import "./Sidebar.css";

function Sidebar() {
  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-header">
        <div className="logo-circle">
          <i className="fas fa-graduation-cap"></i>
        </div>
        <div className="logo-text">
          <strong>SENA</strong>
          <span>Sistema de Evaluación de Instructores</span>
        </div>
      </div>

      {/* Menú */}
      <nav className="sidebar-menu">
        <NavLink to="/" end className={({ isActive }) => `menu-item ${isActive ? "active" : ""}`}>
          <i className="fas fa-home"></i>
          <span>Inicio</span>
        </NavLink>

        <NavLink to="/instructores" className={({ isActive }) => `menu-item ${isActive ? "active" : ""}`}>
          <i className="fas fa-chalkboard-teacher"></i>
          <span>Instructores</span>
        </NavLink>

        <NavLink to="/evaluaciones" className={({ isActive }) => `menu-item ${isActive ? "active" : ""}`}>
          <i className="fas fa-clipboard-check"></i>
          <span>Evaluaciones</span>
        </NavLink>

        <NavLink to="/reportes" className={({ isActive }) => `menu-item ${isActive ? "active" : ""}`}>
          <i className="fas fa-chart-bar"></i>
          <span>Reportes</span>
        </NavLink>

        <NavLink to="/fichas" className={({ isActive }) => `menu-item ${isActive ? "active" : ""}`}>
          <i className="fas fa-id-card"></i>
          <span>Fichas</span>
        </NavLink>

        <NavLink to="/usuarios" className={({ isActive }) => `menu-item ${isActive ? "active" : ""}`}>
          <i className="fas fa-users"></i>
          <span>Usuarios</span>
        </NavLink>

        <NavLink to="/contacto" className={({ isActive }) => `menu-item ${isActive ? "active" : ""}`}>
          <i className="fas fa-envelope"></i>
          <span>Contacto</span>
        </NavLink>

        <NavLink to="/configuracion" className={({ isActive }) => `menu-item ${isActive ? "active" : ""}`}>
          <i className="fas fa-cog"></i>
          <span>Configuración</span>
        </NavLink>
      </nav>

      {/* Cerrar sesión */}
      <div className="sidebar-footer">
        <button className="logout-btn">
          <i className="fas fa-sign-out-alt"></i>
          <span>Cerrar sesión</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
{/* Meses */}