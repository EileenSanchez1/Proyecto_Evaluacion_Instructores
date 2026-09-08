import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  instructorIniciar,
  instructorCrearPassword,
  loginInstructorPaso1,
} from "../services/authService";
import "../styles/Login.css";

function validarContrasenaSegura(contrasena) {
  if (contrasena.length < 8) return "La contraseña debe tener al menos 8 caracteres.";
  if (!/[A-Z]/.test(contrasena)) return "Debe contener al menos una mayúscula.";
  if (!/[a-z]/.test(contrasena)) return "Debe contener al menos una minúscula.";
  if (!/\d/.test(contrasena)) return "Debe contener al menos un número.";
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(contrasena))
    return "Debe contener al menos un carácter especial (!@#$%^&* etc.).";
  return null;
}

function LoginInstructor() {
  const navigate = useNavigate();
  // 1 correo | 2 primer acceso | 3 login normal
  const [paso, setPaso] = useState(1);
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [codigo, setCodigo] = useState("");
  const [mostrarPass, setMostrarPass] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [cargando, setCargando] = useState(false);

  const guardarSesion = (respuesta) => {
    localStorage.setItem("token", respuesta.access_token);
    localStorage.setItem("usuario", JSON.stringify(respuesta.usuario));
  };

  const handleCorreo = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);
    const c = correo.trim().toLowerCase();
    if (!c.endsWith("@sena.edu.co")) {
      setEsError(true);
      setMensaje("El correo debe ser institucional (@sena.edu.co).");
      return;
    }
    try {
      setCargando(true);
      const res = await instructorIniciar(c);
      setCorreo(c);
      if (res.requiere_crear_password) {
        setPaso(2);
        setMensaje("Primer acceso: mira el código en la consola del backend y crea tu contraseña.");
      } else {
        setPaso(3);
        setMensaje("Ya iniciaste antes. Ingresa tu contraseña.");
      }
    } catch (error) {
      setEsError(true);
      setMensaje(error.response?.data?.detail || "No se pudo verificar el correo.");
    } finally {
      setCargando(false);
    }
  };

  const handleCrearPassword = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);
    const err = validarContrasenaSegura(contrasena);
    if (err) { setEsError(true); setMensaje(err); return; }
    if (contrasena !== confirmPass) {
      setEsError(true); setMensaje("Las contraseñas no coinciden."); return;
    }
    if (!codigo.trim()) {
      setEsError(true); setMensaje("Ingresa el código de verificación."); return;
    }
    try {
      setCargando(true);
      const respuesta = await instructorCrearPassword({
        correo,
        codigo: codigo.trim(),
        nueva_contrasena: contrasena,
      });
      guardarSesion(respuesta);
      setMensaje("¡Listo! Contraseña creada e ingreso exitoso.");
      setTimeout(() => navigate("/"), 500);
    } catch (error) {
      setEsError(true);
      setMensaje(error.response?.data?.detail || "No se pudo crear la contraseña.");
    } finally {
      setCargando(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);
    try {
      setCargando(true);
      const respuesta = await loginInstructorPaso1({ correo, contrasena });
      if (!respuesta.access_token) {
        setEsError(true);
        setMensaje("No se recibió token.");
        return;
      }
      guardarSesion(respuesta);
      setMensaje("Inicio de sesión exitoso");
      setTimeout(() => navigate("/"), 400);
    } catch (error) {
      setEsError(true);
      setMensaje(error.response?.data?.detail || "Correo o contraseña incorrectos.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="contenedor-login">
      <div className="tarjeta-login">
        <div className="lado-imagen">
          <img src="/imgs/logo-sena.png" alt="Logo SENA" className="logo-sena" />
          <h2>Acceso Instructor</h2>
          <p>Plataforma de evaluación SENA</p>
        </div>
        <div className="lado-formulario">
          <h1>Soy Instructor</h1>
          <p className="subtitulo">
            {paso === 1 && "Correo institucional @sena.edu.co"}
            {paso === 2 && "Crea tu contraseña (solo la primera vez)"}
            {paso === 3 && "Ingresa tu contraseña"}
          </p>

          {mensaje && (
            <div className={`mensaje-login ${esError ? "error" : "exito"}`}>{mensaje}</div>
          )}

          {paso === 1 && (
            <form onSubmit={handleCorreo}>
              <div>
                <label>Correo institucional</label>
                <input
                  type="email"
                  placeholder="tu.nombre@sena.edu.co"
                  value={correo}
                  onChange={(e) => setCorreo(e.target.value)}
                  required
                />
              </div>
              <button type="submit" disabled={cargando}>
                {cargando ? "Verificando..." : "Continuar"}
              </button>
            </form>
          )}

          {paso === 2 && (
            <form onSubmit={handleCrearPassword}>
              <div>
                <label>Código de verificación</label>
                <input
                  type="text"
                  placeholder="123456"
                  value={codigo}
                  onChange={(e) => setCodigo(e.target.value)}
                  maxLength={8}
                  required
                />
              </div>
              <div className="password-field">
                <label>Nueva contraseña</label>
                <div className="password-input-wrapper">
                  <input
                    type={mostrarPass ? "text" : "password"}
                    value={contrasena}
                    onChange={(e) => setContrasena(e.target.value)}
                    required
                  />
                  <button type="button" className="btn-ojito" onClick={() => setMostrarPass(!mostrarPass)}>
                    <i className={`bi ${mostrarPass ? "bi-eye-slash" : "bi-eye"}`}></i>
                  </button>
                </div>
                <small className="hint-pass">
                  Mín. 8 · Mayúscula · Minúscula · Número · Especial (!@#$%)
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
                {cargando ? "Guardando..." : "Crear contraseña e ingresar"}
              </button>
              <button type="button" className="btn-secundario" onClick={() => setPaso(1)}>Volver</button>
            </form>
          )}

          {paso === 3 && (
            <form onSubmit={handleLogin}>
              <div className="password-field">
                <label>Contraseña</label>
                <div className="password-input-wrapper">
                  <input
                    type={mostrarPass ? "text" : "password"}
                    value={contrasena}
                    onChange={(e) => setContrasena(e.target.value)}
                    required
                  />
                  <button type="button" className="btn-ojito" onClick={() => setMostrarPass(!mostrarPass)}>
                    <i className={`bi ${mostrarPass ? "bi-eye-slash" : "bi-eye"}`}></i>
                  </button>
                </div>
              </div>
              <button type="submit" disabled={cargando}>
                {cargando ? "Ingresando..." : "Ingresar"}
              </button>
              <button type="button" className="btn-secundario" onClick={() => setPaso(1)}>Volver</button>
            </form>
          )}

          <div className="registro-link">
            <p><Link to="/login">← Volver al login principal</Link></p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginInstructor;
