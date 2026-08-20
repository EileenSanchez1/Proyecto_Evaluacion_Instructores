import "./Navbar.css";

function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-left">
        <button className="menu-toggle">
          <i className="fas fa-bars"></i>
        </button>
      </div>

      <div className="navbar-center">
        <div className="search-box">
          <i className="fas fa-search"></i>
          <input type="text" placeholder="Buscar..." />
        </div>
      </div>

      <div className="navbar-right">
        <button className="icon-btn">
          <i className="fas fa-bell"></i>
          <span className="badge"></span>
        </button>
        <button className="icon-btn">
          <i className="fas fa-envelope"></i>
          <span className="badge"></span>
        </button>

        <div className="user-menu">
          <div className="user-avatar">
            <i className="fas fa-user"></i>
          </div>
          <div className="user-info">
            <span className="user-name">Usuario</span>
            <span className="user-role">Invitado</span>
          </div>
          <i className="fas fa-chevron-down chevron"></i>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
{/* Meses */}