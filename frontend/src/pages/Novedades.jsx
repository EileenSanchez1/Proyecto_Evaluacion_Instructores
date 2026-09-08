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
      setError("");
      const data = await listarNovedades();
      setNovedades(Array.isArray(data) ? data : []);
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

  const extraerAsunto = (mensaje) => {
    if (!mensaje) return { asunto: null, cuerpo: "" };
    const m = String(mensaje).match(/^Asunto:\s*(.+?)(?:\n\n|\n)([\s\S]*)$/i);
    if (m) return { asunto: m[1].trim(), cuerpo: m[2].trim() };
    return { asunto: null, cuerpo: mensaje };
  };

  const nuevas = novedades.filter((n) => !n.leido).length;

  return (
    <div className="novedades-page">
      <header className="novedades-header">
        <div>
          <h1>
            <i className="bi bi-bell"></i> Novedades
          </h1>
          <p>Mensajes enviados por los aprendices desde Contacto.</p>
        </div>
        {novedades.length > 0 && (
          <div className="novedades-resumen">
            <span className="novedades-chip">
              <i className="bi bi-inbox"></i> {novedades.length} total
            </span>
            {nuevas > 0 && (
              <span className="novedades-chip novedades-chip-nueva">
                <i className="bi bi-envelope-exclamation"></i> {nuevas} sin leer
              </span>
            )}
          </div>
        )}
      </header>

      {cargando && (
        <div className="novedades-estado">
          <div className="novedades-spinner"></div>
          <p>Cargando novedades...</p>
        </div>
      )}

      {error && (
        <div className="novedades-alerta novedades-alerta-error">
          <i className="bi bi-exclamation-circle"></i> {error}
        </div>
      )}

      {!cargando && !error && novedades.length === 0 && (
        <div className="novedades-vacio">
          <i className="bi bi-inbox"></i>
          <h3>No hay novedades</h3>
          <p>Cuando un aprendiz envíe un mensaje desde Contacto, aparecerá aquí.</p>
        </div>
      )}

      <div className="novedades-grid">
        {novedades.map((n) => {
          const { asunto, cuerpo } = extraerAsunto(n.mensaje);
          return (
            <article
              key={n.id_novedad}
              className={`novedad-card ${n.leido ? "leida" : "nueva"}`}
            >
              <div className="novedad-header">
                <div className="novedad-avatar">
                  {(n.nombre?.[0] || "?").toUpperCase()}
                  {(n.apellido?.[0] || "").toUpperCase()}
                </div>
                <div className="novedad-info">
                  <h4>
                    {n.nombre} {n.apellido}
                  </h4>
                  <span className="novedad-meta">
                    Ficha: {n.ficha || "—"} ·{" "}
                    {n.fecha
                      ? new Date(n.fecha).toLocaleString("es-CO")
                      : "—"}
                  </span>
                </div>
                {!n.leido ? (
                  <span className="badge-nueva">NUEVA</span>
                ) : (
                  <span className="badge-leida">Leída</span>
                )}
              </div>

              <div className="novedad-body">
                {asunto && (
                  <p className="novedad-asunto">
                    <strong>Asunto:</strong> {asunto}
                  </p>
                )}
                <p className="novedad-texto">{cuerpo || n.mensaje}</p>
                {n.correo && (
                  <a className="novedad-correo" href={`mailto:${n.correo}`}>
                    <i className="bi bi-envelope"></i> {n.correo}
                  </a>
                )}
              </div>

              {!n.leido && (
                <button
                  type="button"
                  className="btn-marcar-leida"
                  onClick={() => marcarLeida(n.id_novedad)}
                >
                  <i className="bi bi-check2-all"></i> Marcar como leída
                </button>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}

export default Novedades;
