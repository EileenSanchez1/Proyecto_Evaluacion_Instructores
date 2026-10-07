import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { contarNovedadesNoLeidas } from "../services/NovedadService";
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
  const [novedadesNuevas, setNovedadesNuevas] = useState(0);

  useEffect(() => {
    if (!adminOCoordinador) return;
    let vivo = true;
    const cargar = async () => {
      try {
        const data = await contarNovedadesNoLeidas();
        if (vivo) setNovedadesNuevas(Number(data?.count || 0));
      } catch {
        /* silencioso */
      }
    };
    cargar();
    const id = setInterval(cargar, 30000); // cada 30s
    return () => {
      vivo = false;
      clearInterval(id);
    };
  }, [adminOCoordinador]);

  const badgeNovedades =
    novedadesNuevas > 99 ? "99+" : novedadesNuevas > 0 ? String(novedadesNuevas) : null;

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
          to="/cambiar-contrasena"
          className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
        >
          <i className="bi bi-key"></i> Cambiar contraseña
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
              {badgeNovedades && (
                <span className="nav-badge-novedades">{badgeNovedades}</span>
              )}
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
              to="/resultados-aprendizaje"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <i className="bi bi-award"></i> Resultados de Aprendizaje
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
