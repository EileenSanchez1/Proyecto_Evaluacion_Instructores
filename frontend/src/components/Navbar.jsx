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
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.querySelector(".sidebar-overlay");
    sidebar?.classList.toggle("sidebar--open");
    overlay?.classList.toggle("visible");
  };

  const cerrarMenu = () => {
    document.querySelector(".sidebar")?.classList.remove("sidebar--open");
    document.querySelector(".sidebar-overlay")?.classList.remove("visible");
  };

  return (
    <>
      <nav className="navbar">
        <div style={{ display: "flex", alignItems: "center", gap: "8px", minWidth: 0 }}>
          <button
            className="navbar-hamburger"
            onClick={abrirMenu}
            aria-label="Abrir menú"
          >
            <i className="bi bi-list"></i>
          </button>
          <div className="navbar-logo">
            <i className="bi bi-mortarboard-fill"></i>
            <span>SENA Evaluación</span>
          </div>
        </div>

        <div className="navbar-user">
          <div className="user-avatar" title={nombreCompleto}>
            {inicial}
          </div>
          <div className="user-info">
            <span className="user-name">{nombreCompleto}</span>
            <span className="user-role">{usuario?.rol || "Aprendiz"}</span>
          </div>
          <button className="btn-logout" onClick={manejarLogout} title="Cerrar sesión">
            <i className="bi bi-box-arrow-right"></i>
            <span className="logout-text">Cerrar sesión</span>
          </button>
        </div>
      </nav>

      {/* Overlay para cerrar el menú en móvil al tocar fuera */}
      <div className="sidebar-overlay" onClick={cerrarMenu}></div>
    </>
  );
}

export default Navbar;
