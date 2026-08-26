import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { recuperarContrasena } from "../services/authService";
import "../styles/Login.css";

function RecuperarContrasena() {
  const navigate = useNavigate();

  const [correo, setCorreo] = useState("");
  const [nuevaContrasena, setNuevaContrasena] = useState("");
  const [confirmar, setConfirmar] = useState("");

  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [cargando, setCargando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);

    if (!correo.trim() || !nuevaContrasena) {
      setEsError(true);
      setMensaje("Ingresa tu correo y la nueva contraseña.");
      return;
    }

    if (nuevaContrasena.length < 6) {
      setEsError(true);
      setMensaje("La contraseña debe tener al menos 6 caracteres.");
      return;
    }

    if (nuevaContrasena !== confirmar) {
      setEsError(true);
      setMensaje("Las contraseñas no coinciden.");
      return;
    }

    try {
      setCargando(true);
      const respuesta = await recuperarContrasena(correo.trim(), nuevaContrasena);

      setEsError(false);
      setMensaje(respuesta.mensaje || "Contraseña actualizada correctamente.");

      setTimeout(() => {
        navigate("/login");
      }, 1200);
    } catch (error) {
      console.error("Error al recuperar contraseña:", error);
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
          <p>Tranquilo, en unos pasos la recuperas</p>
        </div>

        <div className="lado-formulario">
          <h1>Recuperar contraseña</h1>
          <p className="subtitulo">
            Ingresa el correo de tu cuenta y define una nueva contraseña
          </p>

          {mensaje && (
            <div className={`mensaje-login ${esError ? "error" : "exito"}`}>
              {mensaje}
            </div>
          )}

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

            <div>
              <label>Nueva contraseña</label>
              <input
                type="password"
                placeholder="Mínimo 6 caracteres"
                value={nuevaContrasena}
                onChange={(e) => setNuevaContrasena(e.target.value)}
                required
              />
            </div>

            <div>
              <label>Confirmar nueva contraseña</label>
              <input
                type="password"
                placeholder="Repite la nueva contraseña"
                value={confirmar}
                onChange={(e) => setConfirmar(e.target.value)}
                required
              />
            </div>

            <button type="submit" disabled={cargando}>
              {cargando ? "Actualizando..." : "Actualizar contraseña"}
            </button>
          </form>

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
