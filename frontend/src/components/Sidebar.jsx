import { NavLink } from "react-router-dom";
import {
  esAdmin,
  esAdminOCoordinador,
  esInstructor,
  obtenerRol,
} from "../utils/sesion";
import "../styles/Layout.css";

function Sidebar() {
  const admin = esAdmin();
  const adminOCoordinador = esAdminOCoordinador();
  const instructor = esInstructor();
  const rol = obtenerRol();
  const esAprendiz = rol === "Aprendiz";

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

        {instructor && (
          <>
            <NavLink
              to="/perfil-instructor"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <i className="bi bi-person-badge"></i> Mi Perfil
            </NavLink>
            <NavLink
              to="/mi-promedio"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <i className="bi bi-graph-up-arrow"></i> Mi Promedio
            </NavLink>
            <NavLink
              to="/evaluaciones"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <i className="bi bi-clipboard-check"></i> Evaluaciones
            </NavLink>
          </>
        )}

        {!instructor && (
          <NavLink
            to="/instructores"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <i className="bi bi-people"></i> Instructores
          </NavLink>
        )}

        {/* Aprendiz: Evaluaciones para calificar */}
        {esAprendiz && (
          <NavLink
            to="/evaluaciones"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <i className="bi bi-clipboard-check"></i> Evaluaciones
          </NavLink>
        )}

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
              to="/novedades"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <i className="bi bi-bell"></i> Novedades
            </NavLink>

            <NavLink
              to="/fichas"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <i className="bi bi-card-text"></i> Fichas
            </NavLink>

            <NavLink
              to="/competencias"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <i className="bi bi-award"></i> Competencias
            </NavLink>

            <NavLink
              to="/periodos"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <i className="bi bi-calendar-range"></i> Periodos
            </NavLink>

            {/* Antes: Historial. Ahora se muestra como Evaluaciones (misma lógica /historial) */}
            <NavLink
              to="/historial"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <i className="bi bi-clipboard-check"></i> Evaluaciones
            </NavLink>

            <NavLink
              to="/reportes"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <i className="bi bi-bar-chart"></i> Reportes
            </NavLink>
          </>
        )}

        {/* Contacto solo Aprendiz */}
        {esAprendiz && (
          <NavLink
            to="/contacto"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <i className="bi bi-envelope"></i> Contacto / Novedad
          </NavLink>
        )}
      </nav>
    </aside>
  );
}

export default Sidebar;
