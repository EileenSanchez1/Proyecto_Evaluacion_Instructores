import { useEffect, useState } from "react";
import { listarNovedades, marcarNovedadLeida } from "../services/NovedadService";
import "../styles/Novedades.css";

function Novedades() {
  const [novedades, setNovedades] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargar = async () => {
    try {
      setCargando(true);
      const data = await listarNovedades();
      setNovedades(data);
    } catch (err) {
      setError("No se pudieron cargar las novedades.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  const marcarLeida = async (id) => {
    try {
      await marcarNovedadLeida(id);
      setNovedades((prev) =>
        prev.map((n) => (n.id_novedad === id ? { ...n, leido: true } : n))
      );
    } catch (err) {
      alert("No se pudo marcar como leída.");
    }
  };

  return (
    <div className="novedades-page">
      <header className="page-header">
        <h1>NOVEDADES</h1>
        <p>Mensajes enviados por los aprendices.</p>
      </header>

      {cargando && <p className="text-muted">Cargando novedades...</p>}
      {error && <p className="text-danger">{error}</p>}

      {!cargando && novedades.length === 0 && (
        <p className="text-muted">No hay novedades registradas.</p>
      )}

      <div className="novedades-grid">
        {novedades.map((n) => (
          <div
            key={n.id_novedad}
            className={`novedad-card ${n.leido ? "leida" : "nueva"}`}
          >
            <div className="novedad-header">
              <div className="novedad-avatar">
                {n.nombre[0]}
                {n.apellido[0]}
              </div>
              <div className="novedad-info">
                <h4>
                  {n.nombre} {n.apellido}
                </h4>
                <span className="novedad-ficha">Ficha: {n.ficha}</span>
                <span className="novedad-fecha">
                  {new Date(n.fecha).toLocaleString("es-CO")}
                </span>
              </div>
              {!n.leido && <span className="badge-nueva">NUEVA</span>}
            </div>
            <div className="novedad-body">
              <p>{n.mensaje}</p>
              <small className="novedad-correo">{n.correo}</small>
            </div>
            {!n.leido && (
              <button
                className="btn-marcar-leida"
                onClick={() => marcarLeida(n.id_novedad)}
              >
                Marcar como leída
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Novedades;