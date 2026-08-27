import { useState } from "react";
import { Link } from "react-router-dom";
import { solicitarRecuperacion } from "../services/authService";
import "../styles/Login.css";

// Paso 1 del flujo real (HU-004): el usuario solo pide el enlace.
// El backend nunca confirma si el correo existe o no (evita
// que alguien use este formulario para adivinar cuentas).
function RecuperarContrasena() {
  const [correo, setCorreo] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [enviado, setEnviado] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);

    if (!correo.trim()) {
      setEsError(true);
      setMensaje("Ingresa tu correo.");
      return;
    }

    try {
      setCargando(true);
      const respuesta = await solicitarRecuperacion(correo.trim());
      setEnviado(true);
      setMensaje(
        respuesta.mensaje ||
          "Si el correo está registrado, recibirás un enlace de recuperación."
      );
    } catch (error) {
      console.error("Error al solicitar recuperación:", error);
      setEsError(true);
      const detalle = error.response?.data?.detail;
      setMensaje(
        typeof detalle === "string"
          ? detalle
          : "No se pudo conectar con el servidor."
      );
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="contenedor-login">
      <div className="tarjeta-login">
        <div className="lado-imagen">
          <img src="/imgs/logo-sena.png" alt="Logo SENA" className="logo-sena" />
          <h2>¿Olvidaste tu contraseña?</h2>
          <p>Te enviamos un enlace para recuperarla</p>
        </div>

        <div className="lado-formulario">
          <h1>Recuperar contraseña</h1>
          <p className="subtitulo">
            Ingresa el correo de tu cuenta y te enviaremos un enlace
            para definir una nueva contraseña.
          </p>

          {mensaje && (
            <div className={`mensaje-login ${esError ? "error" : "exito"}`}>
              {mensaje}
            </div>
          )}

          {!enviado && (
            <form onSubmit={handleSubmit}>
              <div>
                <label>Correo</label>
                <input
                  type="email"
                  placeholder="Ingresa tu correo registrado"
                  value={correo}
                  onChange={(e) => setCorreo(e.target.value)}
                  required
                />
              </div>

              <button type="submit" disabled={cargando}>
                {cargando ? "Enviando..." : "Enviar enlace"}
              </button>
            </form>
          )}

          <div className="registro-link">
            <p>
              ¿Ya la recordaste? <Link to="/login">Volver al inicio de sesión</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RecuperarContrasena;
