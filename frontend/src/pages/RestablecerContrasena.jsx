import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { restablecerContrasena } from "../services/authService";
import "../styles/Login.css";

// Paso 2 del flujo real (HU-004): esta es la página a la que llega
// el enlace del correo, con el token en la URL:
//   /restablecer-contrasena?token=xxxxx
function RestablecerContrasena() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [nuevaContrasena, setNuevaContrasena] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [cargando, setCargando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);

    if (!token) {
      setEsError(true);
      setMensaje("El enlace no es válido o le falta el token.");
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
      const respuesta = await restablecerContrasena(token, nuevaContrasena);
      setEsError(false);
      setMensaje(respuesta.mensaje || "Contraseña actualizada correctamente.");

      setTimeout(() => {
        navigate("/login");
      }, 1200);
    } catch (error) {
      console.error("Error al restablecer contraseña:", error);
      setEsError(true);
      const detalle = error.response?.data?.detail;
      setMensaje(
        typeof detalle === "string"
          ? detalle
          : "El enlace expiró o no es válido. Solicita uno nuevo."
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
          <h2>Define tu nueva contraseña</h2>
          <p>Último paso para recuperar tu acceso</p>
        </div>

        <div className="lado-formulario">
          <h1>Nueva contraseña</h1>
          <p className="subtitulo">
            Este enlace expira a los 30 minutos de haberse generado.
          </p>

          {mensaje && (
            <div className={`mensaje-login ${esError ? "error" : "exito"}`}>
              {mensaje}
            </div>
          )}

          <form onSubmit={handleSubmit}>
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
              ¿El enlace ya no sirve?{" "}
              <Link to="/recuperar-contrasena">Solicitar uno nuevo</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RestablecerContrasena;
