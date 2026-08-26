import { useNavigate } from "react-router-dom";
import { obtenerAprendizSesion } from "../utils/sesion";
import "../styles/Layout.css";

function Navbar() {
  const navigate = useNavigate();
  const aprendiz = obtenerAprendizSesion();

  const nombreCompleto = aprendiz
    ? `${aprendiz.nombre} ${aprendiz.apellido}`
    : "Usuario";
  const inicial = aprendiz?.nombre ? aprendiz.nombre[0].toUpperCase() : "U";

  const manejarLogout = () => {
    localStorage.removeItem("usuario");
    navigate("/login");
  };

  const abrirMenu = () => {
    document.querySelector(".sidebar")?.classList.toggle("sidebar--open");
  };

  return (
    <nav className="navbar">
      <div style={{ display: "flex", alignItems: "center" }}>
        <button className="navbar-hamburger" onClick={abrirMenu} aria-label="Abrir menú">
          <i className="bi bi-list"></i>
        </button>
        <div className="navbar-logo">
          <i className="bi bi-mortarboard-fill"></i>
          Sistema de Evaluación de Instructores
        </div>
      </div>

      <div className="navbar-user">
        <div className="user-avatar">{inicial}</div>
        <div className="user-info">
          <span className="user-name">{nombreCompleto}</span>
          <span className="user-role">
            {aprendiz?.es_admin ? "Administrador" : "Aprendiz"}
          </span>
        </div>
        <button className="btn-logout" onClick={manejarLogout}>
          Cerrar sesión
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
