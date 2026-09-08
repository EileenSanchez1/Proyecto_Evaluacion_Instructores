import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  solicitarRecuperacion,
  verificarCodigoRecuperacion,
  restablecerContrasena,
} from "../services/authService";
import "../styles/Login.css";

function validarContrasenaSegura(contrasena) {
  if (contrasena.length < 8) return "La contraseña debe tener al menos 8 caracteres.";
  if (!/[A-Z]/.test(contrasena)) return "Debe contener al menos una mayúscula.";
  if (!/[a-z]/.test(contrasena)) return "Debe contener al menos una minúscula.";
  if (!/\d/.test(contrasena)) return "Debe contener al menos un número.";
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(contrasena))
    return "Debe contener al menos un carácter especial.";
  return null;
}

function RecuperarContrasena() {
  const navigate = useNavigate();
  const [paso, setPaso] = useState(1);
  const [correo, setCorreo] = useState("");
  const [codigo, setCodigo] = useState("");
  const [nuevaPass, setNuevaPass] = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [mostrarPass, setMostrarPass] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [cargando, setCargando] = useState(false);

  const handlePaso1 = async (e) => {
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
      await solicitarRecuperacion(correo.trim());
      setPaso(2);
      setMensaje("Si el correo está registrado, recibirás un código. Revisa tu bandeja (o la consola del backend en desarrollo).");
    } catch (error) {
      setEsError(true);
      setMensaje(error.response?.data?.detail || "Error al solicitar recuperación.");
    } finally {
      setCargando(false);
    }
  };

  const handlePaso2 = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);
    if (!codigo.trim()) {
      setEsError(true);
      setMensaje("Ingresa el código.");
      return;
    }
    try {
      setCargando(true);
      await verificarCodigoRecuperacion(correo.trim(), codigo.trim());
      setPaso(3);
      setMensaje("Código verificado. Ahora define tu nueva contraseña.");
    } catch (error) {
      setEsError(true);
      setMensaje(error.response?.data?.detail || "Código inválido o expirado.");
    } finally {
      setCargando(false);
    }
  };

  const handlePaso3 = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);
    const err = validarContrasenaSegura(nuevaPass);
    if (err) {
      setEsError(true);
      setMensaje(err);
      return;
    }
    if (nuevaPass !== confirmPass) {
      setEsError(true);
      setMensaje("Las contraseñas no coinciden.");
      return;
    }
    try {
      setCargando(true);
      await restablecerContrasena({
        correo: correo.trim(),
        codigo: codigo.trim(),
        nueva_contrasena: nuevaPass,
      });
      setMensaje("Contraseña actualizada. Ya puedes iniciar sesión.");
      setTimeout(() => navigate("/login"), 1500);
    } catch (error) {
      setEsError(true);
      setMensaje(error.response?.data?.detail || "No se pudo restablecer la contraseña.");
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
          <p>Recuperación por código de verificación</p>
        </div>

        <div className="lado-formulario">
          <h1>Recuperar contraseña</h1>
          <p className="subtitulo">
            {paso === 1 && "Ingresa el correo de tu cuenta"}
            {paso === 2 && "Ingresa el código que enviamos a tu correo"}
            {paso === 3 && "Define una nueva contraseña segura"}
          </p>

          {mensaje && (
            <div className={`mensaje-login ${esError ? "error" : "exito"}`}>
              {mensaje}
            </div>
          )}

          {paso === 1 && (
            <form onSubmit={handlePaso1}>
              <div>
                <label>Correo</label>
                <input
                  type="email"
                  placeholder="Correo registrado"
                  value={correo}
                  onChange={(e) => setCorreo(e.target.value)}
                  required
                />
              </div>
              <button type="submit" disabled={cargando}>
                {cargando ? "Enviando..." : "Enviar código"}
              </button>
            </form>
          )}

          {paso === 2 && (
            <form onSubmit={handlePaso2}>
              <div>
                <label>Código de verificación</label>
                <input
                  type="text"
                  placeholder="Ej: 123456"
                  value={codigo}
                  onChange={(e) => setCodigo(e.target.value)}
                  required
                  maxLength={8}
                />
              </div>
              <button type="submit" disabled={cargando}>
                {cargando ? "Verificando..." : "Verificar código"}
              </button>
            </form>
          )}

          {paso === 3 && (
            <form onSubmit={handlePaso3}>
              <div className="password-field">
                <label>Nueva contraseña</label>
                <div className="password-input-wrapper">
                  <input
                    type={mostrarPass ? "text" : "password"}
                    value={nuevaPass}
                    onChange={(e) => setNuevaPass(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    className="btn-ojito"
                    onClick={() => setMostrarPass(!mostrarPass)}
                  >
                    <i className={`bi ${mostrarPass ? "bi-eye-slash" : "bi-eye"}`}></i>
                  </button>
                </div>
                <small className="hint-pass">
                  Mín. 8 car., mayúscula, minúscula, número y especial.
                </small>
              </div>
              <div>
                <label>Confirmar contraseña</label>
                <input
                  type="password"
                  value={confirmPass}
                  onChange={(e) => setConfirmPass(e.target.value)}
                  required
                />
              </div>
              <button type="submit" disabled={cargando}>
                {cargando ? "Guardando..." : "Cambiar contraseña"}
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
