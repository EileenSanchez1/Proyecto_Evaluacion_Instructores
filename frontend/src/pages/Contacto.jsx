import { useState } from "react";
import { enviarNovedad } from "../services/NovedadService";
import { obtenerUsuarioSesion } from "../utils/sesion";
import "../styles/Contacto.css";

function Contacto() {
  const usuario = obtenerUsuarioSesion();
  const [mensaje, setMensaje] = useState("");
  const [asunto, setAsunto] = useState("");
  const [textoMensaje, setTextoMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [enviando, setEnviando] = useState(false);

  const nombre = usuario?.nombre || "";
  const apellido = usuario?.apellido || "";
  const correo = usuario?.correo || "";
  const ficha = usuario?.ficha || usuario?.id_ficha || "N/A";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);

    if (!textoMensaje.trim()) {
      setEsError(true);
      setMensaje("Escribe un mensaje antes de enviar.");
      return;
    }

    if (!usuario) {
      setEsError(true);
      setMensaje("Debes iniciar sesión como aprendiz para enviar un mensaje.");
      return;
    }

    try {
      setEnviando(true);
      const cuerpo = asunto.trim()
        ? `Asunto: ${asunto.trim()}\n\n${textoMensaje.trim()}`
        : textoMensaje.trim();

      await enviarNovedad({
        nombre,
        apellido,
        correo,
        ficha: String(ficha),
        mensaje: cuerpo,
      });

      setEsError(false);
      setMensaje(
        "Mensaje enviado correctamente. El administrador lo verá en Novedades."
      );
      setAsunto("");
      setTextoMensaje("");
    } catch (error) {
      console.error("Error al enviar novedad:", error);
      setEsError(true);
      setMensaje(
        error.response?.data?.detail ||
          "No se pudo enviar el mensaje. Intenta de nuevo."
      );
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="contacto-page">
      <header className="contacto-header">
        <div>
          <h1>
            <i className="bi bi-envelope-heart"></i> Contacto
          </h1>
          <p>
            Envía una novedad o mensaje al administrador. Aparecerá en la
            sección de Novedades.
          </p>
        </div>
      </header>

      <div className="contacto-grid">
        <section className="contacto-card contacto-form-card">
          <div className="contacto-card-title">
            <h2>Enviar mensaje</h2>
            <p>Tu nombre, correo y ficha se toman de tu sesión.</p>
          </div>

          {mensaje && (
            <div
              className={`contacto-alerta ${
                esError ? "contacto-alerta-error" : "contacto-alerta-ok"
              }`}
            >
              <i
                className={`bi ${
                  esError ? "bi-exclamation-circle" : "bi-check-circle"
                }`}
              ></i>
              <span>{mensaje}</span>
            </div>
          )}

          <form className="contacto-form" onSubmit={handleSubmit}>
            <div className="contacto-row">
              <div className="contacto-field">
                <label>Nombre</label>
                <input type="text" value={nombre} disabled readOnly />
              </div>
              <div className="contacto-field">
                <label>Apellido</label>
                <input type="text" value={apellido} disabled readOnly />
              </div>
            </div>

            <div className="contacto-row">
              <div className="contacto-field">
                <label>Correo</label>
                <input type="email" value={correo} disabled readOnly />
              </div>
              <div className="contacto-field">
                <label>Ficha</label>
                <input type="text" value={String(ficha)} disabled readOnly />
              </div>
            </div>

            <div className="contacto-field">
              <label htmlFor="asunto">Asunto (opcional)</label>
              <input
                id="asunto"
                type="text"
                placeholder="Ej. Solicitud, duda, novedad..."
                value={asunto}
                onChange={(e) => setAsunto(e.target.value)}
              />
            </div>

            <div className="contacto-field">
              <label htmlFor="mensaje">Mensaje</label>
              <textarea
                id="mensaje"
                rows="6"
                placeholder="Escribe tu mensaje o novedad aquí..."
                required
                value={textoMensaje}
                onChange={(e) => setTextoMensaje(e.target.value)}
              />
            </div>

            <button type="submit" className="contacto-btn" disabled={enviando}>
              {enviando ? (
                <>
                  <span className="contacto-spinner"></span> Enviando...
                </>
              ) : (
                <>
                  <i className="bi bi-send-fill"></i> Enviar mensaje
                </>
              )}
            </button>
          </form>
        </section>

        <aside className="contacto-card contacto-info-card">
          <div className="contacto-card-title">
            <h2>Información</h2>
            <p>Datos de atención institucional</p>
          </div>

          <ul className="contacto-info-list">
            <li>
              <span className="contacto-info-icon">
                <i className="bi bi-geo-alt-fill"></i>
              </span>
              <div>
                <strong>Dirección</strong>
                <p>Cl. 52 #13-65 · Bogotá D.C., Colombia</p>
              </div>
            </li>
            <li>
              <span className="contacto-info-icon">
                <i className="bi bi-telephone-fill"></i>
              </span>
              <div>
                <strong>Teléfono</strong>
                <p>(+57) 322 659 9083</p>
              </div>
            </li>
            <li>
              <span className="contacto-info-icon">
                <i className="bi bi-envelope-fill"></i>
              </span>
              <div>
                <strong>Correo</strong>
                <p>evaluacioninstructores@sena.edu.co</p>
              </div>
            </li>
            <li>
              <span className="contacto-info-icon">
                <i className="bi bi-clock-fill"></i>
              </span>
              <div>
                <strong>Horario</strong>
                <p>Lunes a viernes · 7:00 a.m. – 6:00 p.m.</p>
              </div>
            </li>
          </ul>
        </aside>
      </div>
    </div>
  );
}

export default Contacto;
