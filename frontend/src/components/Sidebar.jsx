import { Link } from "react-router-dom";

function Sidebar() {
  return (
    <aside className="sidebar">
      <h2>Menú</h2>

      <nav>
        <Link to="/">Inicio</Link>
        <Link to="/instructores">Instructores</Link>
        <Link to="/evaluaciones">Evaluaciones</Link>
        <Link to="/preguntas">Preguntas</Link>
        <Link to="/fichas">Fichas</Link>
        <Link to="/reportes">Reportes</Link>
        <Link to="/contacto">Contacto</Link>
      </nav>
    </aside>
  );
}

export default Sidebar;