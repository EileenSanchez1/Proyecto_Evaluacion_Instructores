import { useNavigate } from "react-router-dom";
import { obtenerUsuarioSesion, cerrarSesion } from "../utils/sesion";
import "../styles/Layout.css";

function Navbar() {
  const navigate = useNavigate();
  const usuario = obtenerUsuarioSesion();

  const nombreCompleto = usuario
    ? `${usuario.nombre} ${usuario.apellido}`
    : "Usuario";
  const inicial = usuario?.nombre ? usuario.nombre[0].toUpperCase() : "U";

  const manejarLogout = () => {
    cerrarSesion();
    navigate("/login");
  };

  const abrirMenu = () => {
    document.querySelector(".sidebar")?.classList.toggle("sidebar--open");
  };

  return (
    <nav className="navbar">
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <button className="navbar-hamburger" onClick={abrirMenu} aria-label="Abrir menú">
          <i className="bi bi-list"></i>
        </button>
        <div className="navbar-logo">
          <i className="bi bi-mortarboard-fill"></i>
          <span>SENA Evaluación</span>
        </div>
      </div>

      <div className="navbar-user">
        <div className="user-avatar">{inicial}</div>
        <div className="user-info">
          <span className="user-name">{nombreCompleto}</span>
          <span className="user-role">{usuario?.rol || "Aprendiz"}</span>
        </div>
        <button className="btn-logout" onClick={manejarLogout}>
          <i className="bi bi-box-arrow-right"></i> Cerrar sesión
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
