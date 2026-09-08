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
      setMensaje("Mensaje enviado correctamente. El administrador lo verá en Novedades.");
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
    <>
      <header className="page-header">
        <h1>CONTACTO</h1>
      </header>

      <div className="contact-wrapper">
        <section className="contact-form-section">
          <div className="section-header">
            <h2>Contáctanos / Enviar novedad</h2>
            <p>
              Envía un mensaje al administrador. Aparecerá en la sección de
              Novedades.
            </p>
          </div>

          {mensaje && (
            <div
              className={`mensaje-login ${esError ? "error" : "exito"}`}
              style={{ marginBottom: "1rem", padding: "0.75rem", borderRadius: "8px" }}
            >
              {mensaje}
            </div>
          )}

          <form className="contact-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="nombre">Nombre completo</label>
              <input
                type="text"
                id="nombre"
                value={`${nombre} ${apellido}`.trim()}
                disabled
                readOnly
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Correo electrónico</label>
              <input type="email" id="email" value={correo} disabled readOnly />
            </div>

            <div className="form-group">
              <label htmlFor="ficha">Ficha</label>
              <input type="text" id="ficha" value={String(ficha)} disabled readOnly />
            </div>

            <div className="form-group">
              <label htmlFor="asunto">Asunto (opcional)</label>
              <input
                type="text"
                id="asunto"
                placeholder="Asunto del mensaje..."
                value={asunto}
                onChange={(e) => setAsunto(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="mensaje">Mensaje</label>
              <textarea
                id="mensaje"
                rows="5"
                placeholder="Escribe tu mensaje o novedad aquí..."
                required
                value={textoMensaje}
                onChange={(e) => setTextoMensaje(e.target.value)}
              ></textarea>
            </div>

            <button type="submit" className="btn-enviar" disabled={enviando}>
              {enviando ? "Enviando..." : "Enviar mensaje"}
              <i className="fas fa-paper-plane"></i>
            </button>
          </form>
        </section>

        <section className="contact-info-section">
          <div className="section-header">
            <h2>Información de contacto</h2>
          </div>

          <div className="info-cards">
            <div className="info-card">
              <div className="info-icon">
                <i className="fas fa-location-dot"></i>
              </div>
              <div className="info-content">
                <h3>Dirección</h3>
                <p>Cl. 52 #13-65</p>
                <p>Bogotá D.C., Colombia</p>
              </div>
            </div>

            <div className="info-card">
              <div className="info-icon">
                <i className="fas fa-phone"></i>
              </div>
              <div className="info-content">
                <h3>Teléfono</h3>
                <p>(+57) 322 659 9083</p>
              </div>
            </div>

            <div className="info-card">
              <div className="info-icon">
                <i className="fas fa-envelope"></i>
              </div>
              <div className="info-content">
                <h3>Correo Institucional</h3>
                <p>evaluacioninstructores@sena.edu.co</p>
              </div>
            </div>

            <div className="info-card">
              <div className="info-icon">
                <i className="fas fa-clock"></i>
              </div>
              <div className="info-content">
                <h3>Horarios de atención</h3>
                <p>Lunes a Viernes</p>
                <p>7:00 a.m. - 6:00 p.m.</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}

export default Contacto;
