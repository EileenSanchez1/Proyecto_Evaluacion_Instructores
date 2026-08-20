import "../styles/Contacto.css";

function Contacto() {
  const mensaje = () => {
    alert("Mensaje enviado correctamente");
  };

  return (
    <>
      <header className="page-header">
        <h1>CONTACTO</h1>
      </header>

      <div className="contact-wrapper">

        {/* FORMULARIO */}
        <section className="contact-form-section">

          <div className="section-header">
            <h2>Contáctanos</h2>
            <p>Estamos aquí para ayudarte.</p>
          </div>

          <form className="contact-form">

            <div className="form-group">
              <label htmlFor="nombre">Nombre completo</label>

              <input
                type="text"
                id="nombre"
                placeholder="Escribe tu nombre..."
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Correo electrónico</label>

              <input
                type="email"
                id="email"
                placeholder="Escribe tu correo..."
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="asunto">Asunto</label>

              <input
                type="text"
                id="asunto"
                placeholder="Escribe el asunto..."
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="mensaje">Mensaje</label>

              <textarea
                id="mensaje"
                rows="5"
                placeholder="Escribe tu mensaje aquí..."
                required
              ></textarea>
            </div>

            <button
              type="button"
              className="btn-enviar"
              onClick={mensaje}
            >
              Enviar mensaje
              <i className="fas fa-paper-plane"></i>
            </button>

          </form>

        </section>


        {/* INFORMACIÓN DE CONTACTO */}
        <section className="contact-info-section">

          <div className="section-header">
            <h2>Información de contacto</h2>
          </div>

          <div className="info-cards">

            {/* Dirección */}
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


            {/* Teléfono */}
            <div className="info-card">

              <div className="info-icon">
                <i className="fas fa-phone"></i>
              </div>

              <div className="info-content">
                <h3>Teléfono</h3>
                <p>(+57) 322 659 9083</p>
              </div>

            </div>


            {/* Correo */}
            <div className="info-card">

              <div className="info-icon">
                <i className="fas fa-envelope"></i>
              </div>

              <div className="info-content">
                <h3>Correo Institucional</h3>
                <p>evaluacioninstructores@sena.edu.co</p>
              </div>

            </div>


            {/* Horario */}
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